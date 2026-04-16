import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.services import CotacaoService
from app.repositories import CotacaoRepository


class TestCotacaoService:
    """Testes para CotacaoService"""

    def test_criar_cotacao_valida(self, db_session: Session, cotacao_data: dict):
        """Deve criar uma cotação com dados válidos"""
        service = CotacaoService(db_session)
        
        cotacao = service.criar_cotacao(cotacao_data)
        
        assert cotacao.id is not None
        assert cotacao.preco_arroba == cotacao_data["preco_arroba"]

    def test_obter_cotacao_atual(self, db_session: Session, cotacao_data: dict):
        """Deve obter a cotação mais recente"""
        service = CotacaoService(db_session)
        
        service.criar_cotacao({**cotacao_data, "preco_arroba": 250.0})
        service.criar_cotacao({**cotacao_data, "data_referencia": date(2026, 4, 16), "preco_arroba": 260.0})
        
        atual = service.obter_cotacao_atual()
        
        assert atual is not None
        assert atual.preco_arroba == 260.0

    def test_calcular_valor_total(self):
        """Deve calcular valor total de arroba com preço"""
        service = CotacaoService(None)
        
        peso_arroba = 30.0  # 450kg / 15
        preco_arroba = 250.50
        
        valor_total = service.calcular_valor_total(peso_arroba, preco_arroba)
        
        assert valor_total == peso_arroba * preco_arroba
        assert valor_total == 7515.0

    def test_obter_media_preco_ultimos_dias(self, db_session: Session, cotacao_data: dict):
        """Deve calcular média de preço dos últimos dias"""
        service = CotacaoService(db_session)
        
        for i in range(5):
            data = date(2026, 4, 15) - timedelta(days=i)
            service.criar_cotacao({
                **cotacao_data,
                "data_referencia": data,
                "preco_arroba": 250.0 + (i * 2.0)
            })
        
        media = service.obter_media_preco(dias=5)
        
        assert media > 0
        assert 250.0 <= media <= 260.0

    def test_obter_historico_periodo(self, db_session: Session, cotacao_data: dict):
        """Deve obter histórico de cotações em um período"""
        service = CotacaoService(db_session)
        
        for i in range(10):
            data = date(2026, 4, 1) + timedelta(days=i)
            service.criar_cotacao({
                **cotacao_data,
                "data_referencia": data,
                "preco_arroba": 250.0 + i
            })
        
        historico = service.obter_historico_periodo(
            data_inicio=date(2026, 4, 5),
            data_fim=date(2026, 4, 8)
        )
        
        assert len(historico) == 4
        assert historico[0].preco_arroba >= 254.0

    def test_validar_preco_positivo(self, db_session: Session):
        """Deve validar que preço é positivo"""
        service = CotacaoService(db_session)
        
        with pytest.raises(ValueError):
            service.criar_cotacao({
                "preco_arroba": -100.0,
                "data_referencia": date(2026, 4, 15)
            })

    def test_validar_preco_nao_zero(self, db_session: Session):
        """Deve validar que preço não é zero"""
        service = CotacaoService(db_session)
        
        with pytest.raises(ValueError):
            service.criar_cotacao({
                "preco_arroba": 0.0,
                "data_referencia": date(2026, 4, 15)
            })

    def test_atualizar_cotacao(self, db_session: Session, cotacao_data: dict):
        """Deve atualizar uma cotação existente"""
        service = CotacaoService(db_session)
        
        criada = service.criar_cotacao(cotacao_data)
        novo_preco = 300.0
        
        atualizada = service.atualizar_cotacao(criada.id, {"preco_arroba": novo_preco})
        
        assert atualizada.preco_arroba == novo_preco

    def test_deletar_cotacao(self, db_session: Session, cotacao_data: dict):
        """Deve deletar uma cotação existente"""
        service = CotacaoService(db_session)
        
        criada = service.criar_cotacao(cotacao_data)
        
        service.deletar_cotacao(criada.id)
        
        obtida = service.obter_cotacao_por_id(criada.id)
        assert obtida is None
