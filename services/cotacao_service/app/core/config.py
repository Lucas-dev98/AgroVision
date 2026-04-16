import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Cotacao Service"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
