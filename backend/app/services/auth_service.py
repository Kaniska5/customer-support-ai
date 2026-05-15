from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, Customer, UserSession, OTPVerification, PasswordReset
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.utils.otp import generate_otp, otp_expires_at, is_expired
from app.schemas import (
    SignupRequest, LoginRequest, OTPVerifyRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    AuthResponse, TokenResponse, UserOut, MessageResponse
)
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
import secrets


def _token_response(user: User) -> TokenResponse:
    access = create_access_token(subject=user.id, role=user.role)
    refresh = create_refresh_token(subject=user.id)
    from app.core.config import settings
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _user_out(user: User) -> UserOut:
    full_name = user.customer.full_name if user.customer else None
    return UserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        full_name=full_name,
        created_at=user.created_at,
    )


def signup(db: Session, payload: SignupRequest) -> MessageResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="customer",
        is_verified=False,
    )
    db.add(user)
    db.flush()

    customer = Customer(
        user_id=user.id,
        full_name=payload.full_name,
        phone=payload.phone,
    )
    db.add(customer)

    otp = OTPVerification(
        user_id=user.id,
        otp_code=generate_otp(),
        purpose="email_verify",
        expires_at=otp_expires_at(),
    )
    db.add(otp)
    db.commit()

    # TODO Phase 5: send OTP via email SMTP
    # For demo, OTP is returned in message
    return MessageResponse(
        message="Account created. Please verify your email.",
        detail=f"[DEV] Your OTP is: {otp.otp_code}",
    )


def verify_otp(db: Session, payload: OTPVerifyRequest) -> MessageResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id == user.id,
            OTPVerification.purpose == payload.purpose,
            OTPVerification.used == False,
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="No valid OTP found")
    if is_expired(record.expires_at):
        raise HTTPException(status_code=400, detail="OTP has expired")
    if record.otp_code != payload.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    record.used = True
    if payload.purpose == "email_verify":
        user.is_verified = True
    db.commit()
    return MessageResponse(message="OTP verified successfully")


def login(db: Session, payload: LoginRequest) -> AuthResponse:
    user = db.query(User).filter(User.email == payload.email, User.deleted_at == None).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your OTP.")

    tokens = _token_response(user)

    session = UserSession(
        user_id=user.id,
        refresh_token=tokens.refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(session)
    db.commit()

    return AuthResponse(user=_user_out(user), tokens=tokens)


def refresh_token(db: Session, refresh_tok: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_tok)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    session = (
        db.query(UserSession)
        .filter(
            UserSession.refresh_token == refresh_tok,
            UserSession.revoked == False,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
    if is_expired(session.expires_at):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Rotate refresh token
    session.revoked = True
    tokens = _token_response(user)
    new_session = UserSession(
        user_id=user.id,
        refresh_token=tokens.refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(new_session)
    db.commit()
    return tokens


def logout(db: Session, refresh_tok: str) -> MessageResponse:
    session = db.query(UserSession).filter(UserSession.refresh_token == refresh_tok).first()
    if session:
        session.revoked = True
        db.commit()
    return MessageResponse(message="Logged out successfully")


def forgot_password(db: Session, payload: ForgotPasswordRequest) -> MessageResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal if email exists
        return MessageResponse(message="If that email is registered, a reset link has been sent.")

    token = secrets.token_urlsafe(48)
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()

    # TODO Phase 5: send email with reset link
    return MessageResponse(
        message="If that email is registered, a reset link has been sent.",
        detail=f"[DEV] Reset token: {token}",
    )


def reset_password(db: Session, payload: ResetPasswordRequest) -> MessageResponse:
    reset = (
        db.query(PasswordReset)
        .filter(PasswordReset.token == payload.token, PasswordReset.used == False)
        .first()
    )
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if is_expired(reset.expires_at):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user = db.query(User).filter(User.id == reset.user_id).first()
    user.hashed_password = hash_password(payload.new_password)
    reset.used = True
    db.commit()
    return MessageResponse(message="Password reset successfully. You may now log in.")
