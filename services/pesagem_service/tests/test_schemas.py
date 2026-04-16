"""
Testes para Schemas (Pydantic)
"""
import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas import PesagemCreate, PesagemUpdate, PesagemResponse


class TestPesagemCreateSchema:
    """Testes de validação PesagemCreate"""
    
    def test_valid_pesagem_create(self):
        """Testa criação válida"""
        data = {
            "animal_id": 1,
            "peso_kg": 450.5,
            "data": date(2026, 4, 15)
        }
        schema = PesagemCreate(**data)
        assert schema.animal_id == 1
        assert schema.peso_kg == 450.5

    def test_animal_id_required(self):
        """Testa validação de animal_id obrigatório"""
        data = {"peso_kg": 450.0}
        with pytest.raises(ValidationError):
            PesagemCreate(**data)

    def test_peso_kg_required(self):
        """Testa validação de peso_kg obrigatório"""
        data = {"animal_id": 1}
        with pytest.raises(ValidationError):
            PesagemCreate(**data)

    def test_peso_kg_negative(self):
        """Testa validação peso_kg negativo"""
        data = {"animal_id": 1, "peso_kg": -10}
        with pytest.raises(ValidationError):
            PesagemCreate(**data)

    def test_peso_kg_zero(self):
        """Testa validação peso_kg zero"""
        data = {"animal_id": 1, "peso_kg": 0}
        with pytest.raises(ValidationError):
            PesagemCreate(**data)

    def test_peso_kg_too_high(self):
        """Testa validação peso_kg muito alto"""
        data = {"animal_id": 1, "peso_kg": 2000}
        with pytest.raises(ValidationError):
            PesagemCreate(**data)


class TestPesagemUpdateSchema:
    """Testes de validação PesagemUpdate"""
    
    def test_pesagem_update_partial(self):
        """Testa atualização parcial"""
        data = {"peso_kg": 450.0}
        schema = PesagemUpdate(**data)
        assert schema.peso_kg == 450.0
        assert schema.observacoes is None
