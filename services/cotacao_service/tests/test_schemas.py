import pytest
from datetime import date
from pydantic import ValidationError
from app.schemas import CotacaoCreate, CotacaoResponse, CotacaoHistorico


class TestCotacaoCreateSchema:
    """Testes para validação de CotacaoCreate"""

    def test_cotacao_create_required_fields(self):
        """Deve criar cotação com campos obrigatórios"""
        data = CotacaoCreate(
            preco_arroba=250.50,
            data_referencia=date(2026, 4, 15)
        )
        assert data.preco_arroba == 250.50
        assert data.data_referencia == date(2026, 4, 15)

    def test_cotacao_create_preco_negativo_invalido(self):
        """Preço não pode ser negativo"""
        with pytest.raises(ValidationError):
            CotacaoCreate(
                preco_arroba=-100.0,
                data_referencia=date(2026, 4, 15)
            )

    def test_cotacao_create_preco_zero_invalido(self):
        """Preço não pode ser zero"""
        with pytest.raises(ValidationError):
            CotacaoCreate(
                preco_arroba=0.0,
                data_referencia=date(2026, 4, 15)
            )

    def test_cotacao_create_falta_preco(self):
        """Preço é obrigatório"""
        with pytest.raises(ValidationError):
            CotacaoCreate(data_referencia=date(2026, 4, 15))

    def test_cotacao_create_falta_data(self):
        """Data de referência é obrigatória"""
        with pytest.raises(ValidationError):
            CotacaoCreate(preco_arroba=250.50)


class TestCotacaoResponseSchema:
    """Testes para validação de CotacaoResponse"""

    def test_cotacao_response_completa(self):
        """Deve retornar resposta de cotação com todos os campos"""
        from datetime import datetime
        data = CotacaoResponse(
            id=1,
            preco_arroba=250.50,
            data_referencia=date(2026, 4, 15),
            criada_em=datetime(2026, 4, 15, 10, 0, 0),
            atualizada_em=datetime(2026, 4, 15, 10, 0, 0)
        )
        assert data.id == 1
        assert data.preco_arroba == 250.50
        assert data.data_referencia == date(2026, 4, 15)

    def test_cotacao_response_id_obrigatorio(self):
        """ID é obrigatório na resposta"""
        from datetime import datetime
        with pytest.raises(ValidationError):
            CotacaoResponse(
                preco_arroba=250.50,
                data_referencia=date(2026, 4, 15),
                criada_em=datetime(2026, 4, 15, 10, 0, 0),
                atualizada_em=datetime(2026, 4, 15, 10, 0, 0)
            )


class TestCotacaoHistoricoSchema:
    """Testes para validação de CotacaoHistorico agregado"""

    def test_cotacao_historico_agregada(self):
        """Deve agregar histórico com media, minima e maxima"""
        data = CotacaoHistorico(
            data_referencia=date(2026, 4, 15),
            preco_medio=250.50,
            preco_minimo=240.0,
            preco_maximo=260.0,
            quantidade_registros=5
        )
        assert data.preco_medio == 250.50
        assert data.preco_minimo == 240.0
        assert data.preco_maximo == 260.0
        assert data.quantidade_registros == 5
