"""Configuration for the ML service.

Uses pydantic-settings to load values from environment variables.
Every setting has a default so the service can start without a .env file
in development, but production deployments should override these.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """ML service settings loaded from environment variables."""

    # Service
    app_name: str = "pothole-ml-service"
    debug: bool = True

    # Model
    model_path: str = "models/best.pt"
    confidence_threshold: float = 0.25
    iou_threshold: float = 0.45

    # Ollama (for agentic AI reporting agent)
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Server
    host: str = "0.0.0.0"
    port: int = 8771

    class Config:
        env_file = ".env"
        env_prefix = "ML_"


settings = Settings()
