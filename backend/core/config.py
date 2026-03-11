"""
Application Configuration Management
Loads environment variables and provides centralized settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Info
    APP_NAME: str = Field(default="Workflow Automation System")
    APP_VERSION: str = Field(default="1.0.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://workflow_user:workflow_pass@localhost:5432/workflow_db",
        description="PostgreSQL connection string"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # CORS Settings
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed origins"
    )
    
    # ML Configuration
    ML_MODEL_PATH: str = Field(default="./ml/models/")
    MODEL_VERSION: str = Field(default="v1")
    
    # Admin Configuration
    ADMIN_EMAIL: str = Field(default="admin@university.edu")
    ADMIN_PASSWORD: str = Field(default="Admin@123")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    # Google Gemini LLM
    GEMINI_API_KEY: Optional[str] = Field(default=None)

    # SMTP / Email Alerts (Option A)
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    NOTIFY_ADMIN_EMAIL: Optional[str] = Field(default=None)
    EMAIL_ENABLED: bool = Field(default=False)

    # Alert thresholds
    DELAY_RISK_THRESHOLD: float = Field(default=0.70, description="Min probability to flag as at-risk")
    AUTO_SCAN_INTERVAL_MINUTES: int = Field(default=30, description="Background scan interval")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
