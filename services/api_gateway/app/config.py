"""API Gateway Configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações do API Gateway"""
    
    # Serviços
    animal_service_url: str = "http://animal-service:8000"
    pesagem_service_url: str = "http://pesagem-service:8001"
    cotacao_service_url: str = "http://cotacao-service:8002"
    
    # JWT
    secret_key: str = "sua-chave-secreta-super-segura-aqui-32-caracteres"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Gateway
    port: int = 8080
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_seconds: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
