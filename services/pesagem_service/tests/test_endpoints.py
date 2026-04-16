"""
Testes para Endpoints (API)
"""
import pytest
from datetime import date, timedelta


class TestPesagemEndpoints:
    """Testes dos endpoints da API"""
    
    def test_registrar_pesagem_endpoint(self, client):
        """Testa POST /pesagens"""
        response = client.post(
            "/api/v1/pesagens",
            json={
                "animal_id": 1,
                "peso_kg": 450.5,
                "data": "2026-04-15"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["animal_id"] == 1
        assert data["peso_kg"] == 450.5
        assert data["peso_arroba"] == pytest.approx(30.033, rel=0.01)

    def test_registrar_pesagem_invalida(self, client):
        """Testa validação ao registrar"""
        response = client.post(
            "/api/v1/pesagens",
            json={"peso_kg": -10}  # Falta animal_id e peso negativo
        )
        assert response.status_code == 422

    def test_obter_pesagem_endpoint(self, client):
        """Testa GET /pesagens/{id}"""
        # Criar pesagem primeiro
        create_response = client.post(
            "/api/v1/pesagens",
            json={
                "animal_id": 1,
                "peso_kg": 450.0,
                "data": "2026-04-15"
            }
        )
        pesagem_id = create_response.json()["id"]
        
        # Obter pesagem
        response = client.get(f"/api/v1/pesagens/{pesagem_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pesagem_id
        assert data["peso_kg"] == 450.0

    def test_obter_historico_endpoint(self, client):
        """Testa GET /pesagens/animal/{id}/historico"""
        # Criar 2 pesagens
        for i in range(2):
            client.post(
                "/api/v1/pesagens",
                json={
                    "animal_id": 1,
                    "peso_kg": 450 + i * 10,
                    "data": str(date(2026, 4, 15) + timedelta(days=i))
                }
            )
        
        response = client.get("/api/v1/pesagens/animal/1/historico")
        assert response.status_code == 200
        data = response.json()
        assert "pesagens" in data
        assert len(data["pesagens"]) >= 2

    def test_obter_ultima_endpoint(self, client):
        """Testa GET /pesagens/animal/{id}/ultima"""
        # Criar 2 pesagens
        for i in range(2):
            client.post(
                "/api/v1/pesagens",
                json={
                    "animal_id": 1,
                    "peso_kg": 450 + i * 10,
                    "data": str(date(2026, 4, 15) + timedelta(days=i))
                }
            )
        
        response = client.get("/api/v1/pesagens/animal/1/ultima")
        assert response.status_code == 200
        data = response.json()
        assert data["peso_kg"] == 460.0

    def test_obter_ganho_endpoint(self, client):
        """Testa GET /pesagens/animal/{id}/ganho"""
        # Criar 2 pesagens
        for i in range(2):
            client.post(
                "/api/v1/pesagens",
                json={
                    "animal_id": 1,
                    "peso_kg": 450 + i * 10,
                    "data": str(date(2026, 4, 15) + timedelta(days=i))
                }
            )
        
        response = client.get(
            "/api/v1/pesagens/animal/1/ganho",
            params={
                "data_inicio": "2026-04-15",
                "data_fim": "2026-04-16"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ganho_kg"] == 10.0

    def test_atualizar_pesagem_endpoint(self, client):
        """Testa PUT /pesagens/{id}"""
        # Criar pesagem
        create_response = client.post(
            "/api/v1/pesagens",
            json={
                "animal_id": 1,
                "peso_kg": 450.0,
                "data": "2026-04-15"
            }
        )
        pesagem_id = create_response.json()["id"]
        
        # Atualizar
        response = client.put(
            f"/api/v1/pesagens/{pesagem_id}",
            json={"peso_kg": 500.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["peso_kg"] == 500.0

    def test_deletar_pesagem_endpoint(self, client):
        """Testa DELETE /pesagens/{id}"""
        # Criar pesagem
        create_response = client.post(
            "/api/v1/pesagens",
            json={
                "animal_id": 1,
                "peso_kg": 450.0,
                "data": "2026-04-15"
            }
        )
        pesagem_id = create_response.json()["id"]
        
        # Deletar
        response = client.delete(f"/api/v1/pesagens/{pesagem_id}")
        assert response.status_code == 204
        
        # Verificar que foi deletado
        get_response = client.get(f"/api/v1/pesagens/{pesagem_id}")
        assert get_response.status_code == 404
