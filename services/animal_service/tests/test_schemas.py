"""
Testes para Schemas (Pydantic)
"""
import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas import AnimalCreate, AnimalUpdate, AnimalResponse, AnimalStatus


class TestAnimalCreateSchema:
    """Testes de validação AnimalCreate"""
    
    def test_valid_animal_create(self):
        """Testa criação válida"""
        data = {
            "nome": "Boi Bravo",
            "raca": "Nelore",
            "data_nascimento": date(2020, 1, 15),
            "rfid": "BOI_001"
        }
        schema = AnimalCreate(**data)
        assert schema.nome == "Boi Bravo"
        assert schema.raca == "Nelore"

    def test_animal_create_nome_required(self):
        """Testa validação de nome obrigatório"""
        data = {"raca": "Nelore"}
        with pytest.raises(ValidationError):
            AnimalCreate(**data)

    def test_animal_create_raca_required(self):
        """Testa validação de raça obrigatória"""
        data = {"nome": "Boi"}
        with pytest.raises(ValidationError):
            AnimalCreate(**data)

    def test_animal_create_nome_empty(self):
        """Testa validação nome vazio"""
        data = {"nome": "", "raca": "Nelore"}
        with pytest.raises(ValidationError):
            AnimalCreate(**data)

    def test_animal_create_optional_fields(self):
        """Testa campos opcionais"""
        data = {"nome": "Boi", "raca": "Nelore"}
        schema = AnimalCreate(**data)
        assert schema.data_nascimento is None
        assert schema.rfid is None


class TestAnimalUpdateSchema:
    """Testes de validação AnimalUpdate"""
    
    def test_animal_update_partial(self):
        """Testa atualização parcial"""
        data = {"nome": "Novo Nome"}
        schema = AnimalUpdate(**data)
        assert schema.nome == "Novo Nome"
        assert schema.raca is None

    def test_animal_update_empty(self):
        """Testa atualização vazia"""
        schema = AnimalUpdate()
        assert schema.nome is None
        assert schema.raca is None
        assert schema.status is None


class TestAnimalResponseSchema:
    """Testes de validação AnimalResponse"""
    
    def test_valid_response(self):
        """Testa response válida"""
        from datetime import datetime
        data = {
            "id": 1,
            "nome": "Boi",
            "raca": "Nelore",
            "data_nascimento": date(2020, 1, 15),
            "rfid": "BOI_001",
            "lote_id": None,
            "status": AnimalStatus.ATIVO,
            "peso_inicial": None,
            "data_entrada": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        schema = AnimalResponse(**data)
        assert schema.id == 1
        assert schema.nome == "Boi"
