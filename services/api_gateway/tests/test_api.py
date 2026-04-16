"""Testes básicos do API Gateway"""
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Cliente para testes"""
    return TestClient(app)


class TestHealthCheck:
    """Testes de health check"""
    
    def test_health_check_success(self, client):
        """Deve retornar status healthy"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"
    
    def test_health_check_response_structure(self, client):
        """Deve retornar estrutura correta"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data


class TestRootEndpoint:
    """Testes do endpoint raiz"""
    
    def test_root_endpoint_success(self, client):
        """Deve retornar informações do gateway"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "AgroVision API Gateway"
    
    def test_root_endpoint_services_info(self, client):
        """Deve retornar informações dos serviços"""
        response = client.get("/")
        data = response.json()
        assert "services" in data
        assert "animal" in data["services"]
        assert "pesagem" in data["services"]
        assert "cotacao" in data["services"]
    
    def test_root_endpoint_documentation_link(self, client):
        """Deve retornar link de documentação"""
        response = client.get("/")
        data = response.json()
        assert data["documentation"] == "/docs"


class TestCORSConfiguration:
    """Testes de configuração CORS"""
    
    def test_cors_middleware_configured(self, client):
        """CORS middleware deve estar configurado"""
        response = client.get(
            "/",
            headers={"Origin": "http://example.com"}
        )
        assert response.status_code == 200
    
    def test_request_with_origin_header(self, client):
        """Deve responder a requisições com Origin header"""
        response = client.get(
            "/health",
            headers={"Origin": "http://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
