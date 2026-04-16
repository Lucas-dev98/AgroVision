"""
Testes para Endpoints (API)
"""
import pytest
from datetime import date


class TestAnimalEndpoints:
    """Testes dos endpoints da API"""
    
    def test_criar_animal_endpoint(self, client, animal_data):
        """Testa POST /animals"""
        response = client.post(
            "/api/v1/animals",
            json={
                "nome": "Boi Bravo",
                "raca": "Nelore",
                "data_nascimento": "2020-01-15",
                "rfid": "BOI_001"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nome"] == "Boi Bravo"
        assert data["rfid"] == "BOI_001"

    def test_criar_animal_invalido(self, client):
        """Testa validação ao criar animal"""
        response = client.post(
            "/api/v1/animals",
            json={"raca": "Nelore"}  # Falta 'nome'
        )
        assert response.status_code == 422  # Validation error

    def test_listar_animais_endpoint(self, client):
        """Testa GET /animals"""
        response = client.get("/api/v1/animals")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "animais" in data
        assert isinstance(data["animais"], list)

    def test_obter_animal_endpoint(self, client):
        """Testa GET /animals/{id}"""
        # Criar um animal primeiro
        create_response = client.post(
            "/api/v1/animals",
            json={
                "nome": "Boi",
                "raca": "Nelore",
                "rfid": "BOI_TEST"
            }
        )
        animal_id = create_response.json()["id"]
        
        # Obter o animal
        response = client.get(f"/api/v1/animals/{animal_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == animal_id
        assert data["nome"] == "Boi"

    def test_obter_animal_inexistente(self, client):
        """Testa GET /animals/{id} com ID inexistente"""
        response = client.get("/api/v1/animals/99999")
        assert response.status_code == 404

    def test_obter_por_rfid_endpoint(self, client):
        """Testa GET /animals/rfid/{rfid}"""
        # Criar um animal
        client.post(
            "/api/v1/animals",
            json={
                "nome": "Boi",
                "raca": "Nelore",
                "rfid": "BOI_RFID_TEST"
            }
        )
        
        # Obter por RFID
        response = client.get("/api/v1/animals/rfid/BOI_RFID_TEST")
        assert response.status_code == 200
        data = response.json()
        assert data["rfid"] == "BOI_RFID_TEST"

    def test_atualizar_animal_endpoint(self, client):
        """Testa PUT /animals/{id}"""
        # Criar um animal
        create_response = client.post(
            "/api/v1/animals",
            json={
                "nome": "Boi",
                "raca": "Nelore",
                "rfid": "BOI_UPD"
            }
        )
        animal_id = create_response.json()["id"]
        
        # Atualizar
        response = client.put(
            f"/api/v1/animals/{animal_id}",
            json={"nome": "Novo Nome"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "Novo Nome"

    def test_deletar_animal_endpoint(self, client):
        """Testa DELETE /animals/{id}"""
        # Criar um animal
        create_response = client.post(
            "/api/v1/animals",
            json={
                "nome": "Boi",
                "raca": "Nelore",
                "rfid": "BOI_DEL"
            }
        )
        animal_id = create_response.json()["id"]
        
        # Deletar
        response = client.delete(f"/api/v1/animals/{animal_id}")
        assert response.status_code == 204
        
        # Verificar que foi deletado
        get_response = client.get(f"/api/v1/animals/{animal_id}")
        assert get_response.status_code == 404

    def test_health_check(self, client):
        """Testa GET /health"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint(self, client):
        """Testa GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
