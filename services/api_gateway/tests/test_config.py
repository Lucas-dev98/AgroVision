"""Testes de configuração do API Gateway"""
import pytest
from app.config import settings


class TestSettings:
    """Testes de configuração"""
    
    def test_settings_has_service_urls(self):
        """Deve ter URLs dos serviços"""
        assert settings.animal_service_url is not None
        assert settings.pesagem_service_url is not None
        assert settings.cotacao_service_url is not None
    
    def test_settings_animal_service_url_default(self):
        """URL do animal-service deve ter valor padrão"""
        assert "animal-service" in settings.animal_service_url or "8000" in settings.animal_service_url
    
    def test_settings_pesagem_service_url_default(self):
        """URL do pesagem-service deve ter valor padrão"""
        assert "pesagem-service" in settings.pesagem_service_url or "8001" in settings.pesagem_service_url
    
    def test_settings_cotacao_service_url_default(self):
        """URL do cotacao-service deve ter valor padrão"""
        assert "cotacao-service" in settings.cotacao_service_url or "8002" in settings.cotacao_service_url
    
    def test_settings_has_jwt_config(self):
        """Deve ter configuração de JWT"""
        assert settings.secret_key is not None
        assert settings.algorithm is not None
        assert settings.access_token_expire_minutes > 0
    
    def test_settings_algorithm_is_hs256(self):
        """Algoritmo deve ser HS256"""
        assert settings.algorithm == "HS256"
    
    def test_settings_has_rate_limit_config(self):
        """Deve ter configuração de rate limit"""
        assert hasattr(settings, 'rate_limit_enabled')
        assert hasattr(settings, 'rate_limit_requests')
        assert hasattr(settings, 'rate_limit_seconds')
    
    def test_settings_rate_limit_defaults(self):
        """Rate limit deve ter valores padrão"""
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_requests == 100
        assert settings.rate_limit_seconds == 60
    
    def test_settings_gateway_port_default(self):
        """Port do gateway deve ser 8080"""
        assert settings.port == 8080
    
    def test_settings_gateway_host_default(self):
        """Host deve ser 0.0.0.0 para docker"""
        assert settings.host == "0.0.0.0"
    
    def test_settings_log_level_default(self):
        """Log level deve ser INFO"""
        assert settings.log_level == "INFO"
