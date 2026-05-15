from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas import (
    SignupRequest, LoginRequest, RefreshTokenRequest,
    OTPVerifyRequest, ForgotPasswordRequest, ResetPasswordRequest,
    AuthResponse, TokenResponse, UserOut, MessageResponse
)
from app.services import auth_service
from app.middleware.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=MessageResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    return auth_service.signup(db, payload)


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    return auth_service.verify_otp(db, payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_token(db, payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.logout(db, payload.refresh_token)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.forgot_password(db, payload)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, payload)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    full_name = current_user.customer.full_name if current_user.customer else None
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_verified=current_user.is_verified,
        full_name=full_name,
        created_at=current_user.created_at,
    )
