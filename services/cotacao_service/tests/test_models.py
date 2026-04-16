import pytest
from datetime import date
from app.models import Cotacao


class TestCotacaoModel:
    """Testes para o modelo ORM Cotacao"""

    def test_cotacao_creation(self):
        """Deve criar uma instância de Cotacao"""
        cotacao = Cotacao(
            preco_arroba=250.50,
            data_referencia=date(2026, 4, 15)
        )
        assert cotacao.preco_arroba == 250.50
        assert cotacao.data_referencia == date(2026, 4, 15)

    def test_cotacao_repr(self):
        """Deve ter boa representação string"""
        cotacao = Cotacao(
            id=1,
            preco_arroba=250.50,
            data_referencia=date(2026, 4, 15)
        )
        repr_str = repr(cotacao)
        assert "Cotacao" in repr_str or "cotacao" in repr_str.lower()

    def test_cotacao_defaults(self):
        """Deve ter valores padrão para campos opcionais"""
        cotacao = Cotacao(
            preco_arroba=250.50,
            data_referencia=date(2026, 4, 15)
        )
        assert cotacao.id is None  # Será atribuído pelo banco
