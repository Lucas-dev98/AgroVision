import pytest
from datetime import date
from fastapi.testclient import TestClient


class TestCotacaoEndpoints:
    """Testes para endpoints de cotação"""

    def test_criar_cotacao_com_sucesso(self, client: TestClient, cotacao_data: dict):
        """Deve criar uma cotação com sucesso"""
        response = client.post(
            "/api/v1/cotacoes",
            json=cotacao_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["preco_arroba"] == cotacao_data["preco_arroba"]
        assert data["id"] is not None

    def test_criar_cotacao_preco_invalido(self, client: TestClient):
        """Deve rejeitar cotação com pre ço inválido"""
        response = client.post(
            "/api/v1/cotacoes",
            json={
                "preco_arroba": -100.0,
                "data_referencia": "2026-04-15"
            }
        )
        
        assert response.status_code == 422

    def test_obter_cotacao(self, client: TestClient, cotacao_data: dict):
        """Deve obter uma cotação por ID"""
        criar_resp = client.post("/api/v1/cotacoes", json=cotacao_data)
        cotacao_id = criar_resp.json()["id"]
        
        get_resp = client.get(f"/api/v1/cotacoes/{cotacao_id}")
        
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == cotacao_id

    def test_obter_cotacao_inexistente(self, client: TestClient):
        """Deve retornar 404 para cotação inexistente"""
        response = client.get("/api/v1/cotacoes/99999")
        
        assert response.status_code == 404

    def test_listar_cotacoes(self, client: TestClient, cotacao_data: dict):
        """Deve listar todas as cotações"""
        client.post("/api/v1/cotacoes", json=cotacao_data)
        
        response = client.get("/api/v1/cotacoes")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_obter_cotacao_atual(self, client: TestClient, cotacao_data: dict):
        """Deve obter a cotação mais recente"""
        client.post("/api/v1/cotacoes", json=cotacao_data)
        
        response = client.get("/api/v1/cotacoes/atual")
        
        assert response.status_code == 200
        data = response.json()
        assert "preco_arroba" in data
        assert "data_referencia" in data

    def test_obter_historico_cotacoes(self, client: TestClient, cotacao_data: dict):
        """Deve obter histórico das últimas cotações"""
        client.post("/api/v1/cotacoes", json=cotacao_data)
        
        response = client.get("/api/v1/cotacoes/historico?dias=30")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_obter_media_preco(self, client: TestClient, cotacao_data: dict):
        """Deve retornar a média de preço"""
        client.post("/api/v1/cotacoes", json=cotacao_data)
        
        response = client.get("/api/v1/cotacoes/media?dias=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "media" in data

    def test_atualizar_cotacao(self, client: TestClient, cotacao_data: dict):
        """Deve atualizar uma cotação existente"""
        criar_resp = client.post("/api/v1/cotacoes", json=cotacao_data)
        cotacao_id = criar_resp.json()["id"]
        
        atualizar_resp = client.put(
            f"/api/v1/cotacoes/{cotacao_id}",
            json={"preco_arroba": 300.0}
        )
        
        assert atualizar_resp.status_code == 200
        data = atualizar_resp.json()
        assert data["preco_arroba"] == 300.0

    def test_deletar_cotacao(self, client: TestClient, cotacao_data: dict):
        """Deve deletar uma cotação"""
        criar_resp = client.post("/api/v1/cotacoes", json=cotacao_data)
        cotacao_id = criar_resp.json()["id"]
        
        del_resp = client.delete(f"/api/v1/cotacoes/{cotacao_id}")
        
        assert del_resp.status_code == 204
        
        get_resp = client.get(f"/api/v1/cotacoes/{cotacao_id}")
        assert get_resp.status_code == 404

    def test_health_check(self, client: TestClient):
        """Deve disponibilizar health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
