"""
Configurações do Animal Service
"""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Animal Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agrovision:agrovision_dev@localhost:5432/agrovision_db"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # JWT (futuro)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-changeme")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()
