from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DATABASE_URL: str
    DATABASE_URL_DOCKER: str
    TEST_DATABASE_URL: str | None = None

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # El proveedor falso es el valor seguro para desarrollo, CI y pruebas.
    IA_PROVIDER: Literal["falso", "ollama"] = "falso"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0
    OLLAMA_MAX_TOKENS: int = 800
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Convierte una lista de orígenes separada por comas en una lista."""
        return [
            origen.strip()
            for origen in self.CORS_ORIGINS.split(",")
            if origen.strip()
        ]

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env")


settings = Settings()
