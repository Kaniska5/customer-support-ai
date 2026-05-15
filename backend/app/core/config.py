from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

# Resolve .env: try backend dir first, then parent (monorepo root)
_backend_env = os.path.join(os.path.dirname(__file__), "../../.env")
_root_env = os.path.join(os.path.dirname(__file__), "../../../.env")
_env_file = _backend_env if os.path.exists(_backend_env) else _root_env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file, extra="ignore")

    # Application
    APP_NAME: str = "Customer Support AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_SECONDS: int = 3600

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # AI Keys (used in Phase 2+)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "customer-support-ai"
    LANGCHAIN_TRACING_V2: bool = True

    # Enterprise Guardrails & Limits (Phase 6)
    MAX_AGENT_HOPS: int = 5
    REFUND_APPROVAL_LIMIT: float = 200.0
    MIN_CONFIDENCE_THRESHOLD: float = 0.45
    ESCALATION_THRESHOLD: float = 0.40
    MAX_RETRY_COUNT: int = 3


settings = Settings()
