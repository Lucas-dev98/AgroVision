"""
Testes para Modelos
"""
import pytest
from datetime import date
from app.models import Pesagem


class TestPesagemModel:
    """Testes do modelo Pesagem"""
    
    def test_pesagem_creation(self):
        """Testa criação de pesagem"""
        pesagem = Pesagem(
            animal_id=1,
            peso_kg=450.0,
            peso_arroba=30.0,
            data=date(2026, 4, 15)
        )
        assert pesagem.animal_id == 1
        assert pesagem.peso_kg == 450.0
        assert pesagem.peso_arroba == 30.0

    def test_pesagem_repr(self):
        """Testa representação de string"""
        pesagem = Pesagem(id=1, animal_id=1, peso_kg=450.0, data=date(2026, 4, 15))
        assert "Pesagem" in repr(pesagem)
        assert "450" in repr(pesagem)
