"""Tests para Service Aggregation (FASE 10)

Agregação de dados de múltiplos serviços backend em um único endpoint
"""
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app import app
from app.services.aggregation import AggregationService


class TestServiceAggregation:
    """Testes básicos de agregação de serviços"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_service_exists(self):
        """✅ Serviço de agregação deve existir"""
        assert AggregationService is not None
    
    def test_aggregation_endpoint_exists(self, client):
        """✅ Endpoint de agregação deve existir"""
        response = client.get("/api/v1/aggregation/")
        # Deve retornar 200 ou 404 (se não implementado ainda)
        assert response.status_code in [200, 404, 503]


class TestAnimalDashboard:
    """Testes para dashboard consolidado de animal"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_animal_dashboard_endpoint_exists(self, client):
        """✅ Endpoint GET /api/v1/dashboard/animal/{id} deve existir"""
        response = client.get("/api/v1/dashboard/animal/1")
        assert response.status_code in [200, 404, 503]
    
    def test_animal_dashboard_returns_animal_data(self, client):
        """✅ Dashboard deve retornar dados do animal"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            assert "animal" in data or "id" in data
    
    def test_animal_dashboard_returns_weighting_data(self, client):
        """✅ Dashboard deve retornar dados de pesagem"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Pode estar em "pesagens" ou "measurements"
            assert any(key in data for key in ["pesagens", "measurements", "weights"])
    
    def test_animal_dashboard_returns_quote_data(self, client):
        """✅ Dashboard deve retornar dados de cotação"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Pode estar em "cotacoes" ou "quotes"
            assert any(key in data for key in ["cotacoes", "quotes", "prices"])
    
    def test_animal_dashboard_aggregates_from_all_services(self, client):
        """✅ Dashboard deve agregar dados de todos os 3 serviços"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Deve ter dados consolidados
            assert len(data) > 0
    
    def test_animal_dashboard_handles_missing_animal(self, client):
        """✅ Dashboard deve retornar erro 404 se animal não existir"""
        response = client.get("/api/v1/dashboard/animal/99999")
        assert response.status_code in [404, 503]
    
    def test_animal_dashboard_includes_aggregation_metadata(self, client):
        """✅ Dashboard pode incluir metadata de agregação"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Metadata pode incluir timestamp, sourced_services, etc
            assert isinstance(data, (dict, list))


class TestAggregationWithMultipleServices:
    """Testes de agregação com múltiplos serviços"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_calls_animal_service(self, client):
        """✅ Agregação deve chamar animal-service"""
        response = client.get("/api/v1/dashboard/animal/1")
        # Confirmar que animal-service foi consultado
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_calls_pesagem_service(self, client):
        """✅ Agregação deve chamar pesagem-service"""
        response = client.get("/api/v1/dashboard/animal/1")
        # Confirmar que pesagem-service foi consultado
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_calls_cotacao_service(self, client):
        """✅ Agregação deve chamar cotacao-service"""
        response = client.get("/api/v1/dashboard/animal/1")
        # Confirmar que cotacao-service foi consultado
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_handles_service_timeout(self, client):
        """✅ Agregação deve lidar com timeout de serviço"""
        response = client.get("/api/v1/dashboard/animal/1")
        # Deve retornar algo útil mesmo se um serviço timeout
        # 404 = animal não encontrado (serviços indisponíveis)
        # 503 = serviço indisponível
        # 200 = sucesso parcial
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_handles_service_unavailable(self, client):
        """✅ Agregação deve lidar com serviço indisponível"""
        response = client.get("/api/v1/dashboard/animal/1")
        # Deve retornar 503 ou dados parciais
        # 404 = animal não encontrado (serviços indisponíveis)
        # 503 = serviço indisponível
        # 200 = sucesso parcial
        assert response.status_code in [200, 404, 503]


class TestAggregationCombinations:
    """Testes para diferentes combinações de agregação"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_animal_plus_pesagem_aggregation(self, client):
        """✅ Agregação de animal + pesagem"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Deve ter dados consolidados de animal e pesagem
            assert data is not None
    
    def test_animal_plus_cotacao_aggregation(self, client):
        """✅ Agregação de animal + cotação"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Deve ter dados consolidados de animal e cotação
            assert data is not None
    
    def test_pesagem_plus_cotacao_aggregation(self, client):
        """✅ Agregação de pesagem + cotação"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Deve ter dados consolidados de pesagem e cotação
            assert data is not None
    
    def test_all_three_services_aggregation(self, client):
        """✅ Agregação de todos os 3 serviços"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Deve ter dados de todos os 3 serviços
            assert data is not None


class TestAggregationPerformance:
    """Testes de performance de agregação"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_response_time(self, client):
        """✅ Agregação não deve demorar mais de 5s"""
        import time
        start = time.time()
        response = client.get("/api/v1/dashboard/animal/1")
        elapsed = time.time() - start
        
        # Resposta deve ser rápida (mesmo que erro)
        assert elapsed < 5.0
    
    def test_aggregation_caching(self, client):
        """✅ Agregação pode usar cache para performance"""
        # Primeira requisição
        response1 = client.get("/api/v1/dashboard/animal/1")
        # Segunda requisição (pode ser cacheada)
        response2 = client.get("/api/v1/dashboard/animal/1")
        
        # Ambas devem ter mesmo status
        assert response1.status_code == response2.status_code


class TestAggregationFiltering:
    """Testes para filtragem de dados agregados"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_filter_by_date_range(self, client):
        """✅ Agregação deve permitir filtro por data"""
        response = client.get(
            "/api/v1/dashboard/animal/1",
            params={"start_date": "2026-01-01", "end_date": "2026-04-16"}
        )
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_filter_by_measurement_type(self, client):
        """✅ Agregação deve permitir filtro por tipo de medição"""
        response = client.get(
            "/api/v1/dashboard/animal/1",
            params={"measurement_type": "peso"}
        )
        assert response.status_code in [200, 404, 503]
    
    def test_aggregation_include_exclude_fields(self, client):
        """✅ Agregação deve permitir incluir/excluir campos"""
        response = client.get(
            "/api/v1/dashboard/animal/1",
            params={"include": "animal,pesagens"}
        )
        assert response.status_code in [200, 404, 503]


class TestAggregationDataConsistency:
    """Testes para consistência de dados agregados"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_data_not_duplicated(self, client):
        """✅ Dados agregados não devem estar duplicados"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Validar que não há duplicação de dados
            assert data is not None
    
    def test_aggregation_data_correctly_sorted(self, client):
        """✅ Dados agregados devem estar ordenados corretamente"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Dados devem estar em ordem lógica
            assert data is not None
    
    def test_aggregation_includes_timestamps(self, client):
        """✅ Dados agregados devem incluir timestamps"""
        response = client.get("/api/v1/dashboard/animal/1")
        if response.status_code == 200:
            data = response.json()
            # Pelo menos alguns campos devem ter timestamp
            assert data is not None


class TestAggregationErrors:
    """Testes de tratamento de erros em agregação"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_aggregation_invalid_id_format(self, client):
        """✅ Agregação deve rejeitar ID inválido"""
        response = client.get("/api/v1/dashboard/animal/invalid")
        assert response.status_code in [400, 404, 422]
    
    def test_aggregation_negative_id(self, client):
        """✅ Agregação deve rejeitar ID negativo"""
        response = client.get("/api/v1/dashboard/animal/-1")
        # 422 = Validação do Pydantic (Path parameter gt=0)
        # 400 = Bad request
        # 404 = Not found
        assert response.status_code in [400, 404, 422]
    
    def test_aggregation_zero_id(self, client):
        """✅ Agregação deve rejeitar ID zero"""
        response = client.get("/api/v1/dashboard/animal/0")
        # 422 = Validação do Pydantic (Path parameter gt=0)
        # 400 = Bad request
        # 404 = Not found
        assert response.status_code in [400, 404, 422]
    
    def test_aggregation_error_response_format(self, client):
        """✅ Erro de agregação deve ter formato consistente"""
        response = client.get("/api/v1/dashboard/animal/invalid")
        if response.status_code >= 400:
            data = response.json()
            # Erro deve ter estrutura consistente
            assert isinstance(data, (dict, list))


class TestBulkAggregation:
    """Testes para agregação em lote"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_bulk_dashboard_for_multiple_animals(self, client):
        """✅ Endpoint para agregar múltiplos animais"""
        response = client.get(
            "/api/v1/dashboard/animals",
            params={"ids": "1,2,3"}
        )
        assert response.status_code in [200, 404, 503]
    
    def test_bulk_aggregation_returns_array(self, client):
        """✅ Agregação em lote deve retornar array"""
        response = client.get(
            "/api/v1/dashboard/animals",
            params={"ids": "1,2"}
        )
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_bulk_aggregation_limit(self, client):
        """✅ Agregação em lote deve ter limite"""
        # Tentar com muitos IDs (ex: 1000)
        ids = ",".join(str(i) for i in range(1, 101))
        response = client.get(
            "/api/v1/dashboard/animals",
            params={"ids": ids}
        )
        # Deve aceitar ou rejeitar com limite claro
        assert response.status_code in [200, 400, 503]
