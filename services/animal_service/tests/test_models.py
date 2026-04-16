"""
Testes para Models
"""
import pytest
from datetime import date
from app.models import Animal
from app.schemas import AnimalStatus


class TestAnimalModel:
    """Testes do modelo Animal"""
    
    def test_animal_creation(self):
        """Testa criação de animal"""
        animal = Animal(
            nome="Boi Bravo",
            raca="Nelore",
            data_nascimento=date(2020, 1, 15),
            rfid="BOI_001"
        )
        assert animal.nome == "Boi Bravo"
        assert animal.raca == "Nelore"
        assert animal.rfid == "BOI_001"
        assert animal.status == AnimalStatus.ATIVO

    def test_animal_default_status(self):
        """Testa status padrão do animal"""
        animal = Animal(nome="Test", raca="Test")
        assert animal.status == AnimalStatus.ATIVO

    def test_animal_repr(self):
        """Testa representação de string"""
        animal = Animal(id=1, nome="Boi", raca="Nelore")
        assert "Animal" in repr(animal)
        assert "Boi" in repr(animal)
