"""
Configurações do Pesagem Service
"""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Aplicação
    APP_NAME: str = "Pesagem Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Banco de dados
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://agrovision:agrovision_dev@localhost:5432/agrovision_db"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"


settings = Settings()
