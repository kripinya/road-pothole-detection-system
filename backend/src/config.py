"""Configuration for the backend service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Backend settings loaded from environment variables."""

    # Service
    app_name: str = "pothole-backend"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pothole_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ML Service
    ml_service_url: str = "http://localhost:8771"

    # File uploads
    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 10

    # Server
    host: str = "0.0.0.0"
    port: int = 8770

    class Config:
        env_file = ".env"


settings = Settings()
