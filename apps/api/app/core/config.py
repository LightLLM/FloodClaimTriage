"""Application configuration"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    PROJECT_NAME: str = "Flood Triage API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://flooduser:floodpass@localhost:5432/flood_triage"
    )

    # Security
    JWT_SECRET: str = Field(default="dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # S3/MinIO
    S3_ENDPOINT: str = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = Field(default="minioadmin")
    S3_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET: str = Field(default="flood-triage-data")
    S3_REGION: str = Field(default="us-east-1")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    # Scoring model
    MODEL_VERSION: str = "v0.1-rule-based"


settings = Settings()
