from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "RazorRecover AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./razorrecover.db"

    # Security
    # Set SECRET_KEY in your local .env file.
    SECRET_KEY: str = "change-this-development-secret-key"

    # Razorpay Integration
    # Set these values in your local .env file.
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_MODE: str = "test"

    # LLM Settings
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"

    # Policy Guardrail Defaults
    AUTO_RETRY_MAX_AMOUNT: float = 5000.0
    AUTO_RETRY_MIN_PROB: float = 0.75
    MAX_AUTO_RETRIES: int = 2
    HUMAN_APPROVAL_THRESHOLD: float = 50000.0
    MIN_RECOVERY_PROBABILITY: float = 0.60
    MAX_CUSTOMER_CONTACTS: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()