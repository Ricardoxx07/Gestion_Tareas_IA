from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DATABASE_URL: str
    DATABASE_URL_DOCKER: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # El proveedor falso es el valor seguro para desarrollo, CI y pruebas.
    IA_PROVIDER: Literal["falso", "ollama"] = "falso"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0
    OLLAMA_MAX_TOKENS: int = 800

    model_config = SettingsConfigDict(
        env_file=".env"
    )


settings = Settings()
