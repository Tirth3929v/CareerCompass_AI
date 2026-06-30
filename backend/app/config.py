"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings backed by .env file."""

    # Gemini API
    google_genai_api_key: str = ""
    gemini_api_key: str = ""

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017/careercompass"

    # CORS
    allowed_origins: str = "http://localhost:4200,http://localhost:4000"

    # Rate Limiting
    rate_limit_per_day: int = 20

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Mock Mode
    mock_mode: bool = False

    # Gemini Model
    gemini_model: str = "gemini-2.0-flash"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
