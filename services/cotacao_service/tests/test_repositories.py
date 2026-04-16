import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import Cotacao
from app.repositories import CotacaoRepository


class TestCotacaoRepository:
    """Testes para CotacaoRepository"""

    def test_criar_cotacao(self, db_session: Session, cotacao_data: dict):
        """Deve criar uma nova cotação"""
        repo = CotacaoRepository(db_session)
        cotacao = repo.criar(cotacao_data)
        
        assert cotacao.id is not None
        assert cotacao.preco_arroba == cotacao_data["preco_arroba"]
        assert cotacao.data_referencia == cotacao_data["data_referencia"]

    def test_obter_cotacao_por_id(self, db_session: Session, cotacao_data: dict):
        """Deve obter cotação por ID"""
        repo = CotacaoRepository(db_session)
        criada = repo.criar(cotacao_data)
        
        obtida = repo.obter_por_id(criada.id)
        
        assert obtida is not None
        assert obtida.id == criada.id
        assert obtida.preco_arroba == cotacao_data["preco_arroba"]

    def test_obter_cotacao_invalida_retorna_none(self, db_session: Session):
        """Deve retornar None para ID inexistente"""
        repo = CotacaoRepository(db_session)
        resultado = repo.obter_por_id(999)
        
        assert resultado is None

    def test_listar_todas_cotacoes(self, db_session: Session, cotacao_data: dict):
        """Deve listar todas as cotações"""
        repo = CotacaoRepository(db_session)
        repo.criar(cotacao_data)
        repo.criar({**cotacao_data, "data_referencia": date(2026, 4, 14)})
        
        cotacoes = repo.listar()
        
        assert len(cotacoes) >= 2

    def test_obter_cotacao_atual(self, db_session: Session, cotacao_data: dict):
        """Deve obter a cotação mais recente"""
        repo = CotacaoRepository(db_session)
        repo.criar({**cotacao_data, "data_referencia": date(2026, 4, 10)})
        repo.criar({**cotacao_data, "data_referencia": date(2026, 4, 15), "preco_arroba": 260.0})
        
        atual = repo.obter_atual()
        
        assert atual is not None
        assert atual.data_referencia == date(2026, 4, 15)
        assert atual.preco_arroba == 260.0

    def test_obter_historico_ultimos_dias(self, db_session: Session, cotacao_data: dict):
        """Deve obter histórico dos últimos N dias"""
        repo = CotacaoRepository(db_session)
        
        from datetime import date as date_class
        hoje = date_class(2026, 4, 15)
        
        # Criar cotações para os últimos 10 dias
        for i in range(10):
            data = hoje - timedelta(days=i)
            repo.criar({**cotacao_data, "data_referencia": data, "preco_arroba": 250.0 + i})
        
        # Obter últimos 5 dias
        historico = repo.obter_historico(dias=5)
        
        # Tenho 5 cotações dos últimos 5 dias
        assert len(historico) >= 5
        # Todas devem estar dentro dos últimos 5 dias
        min_data = hoje - timedelta(days=5)
        assert all(h.data_referencia >= min_data for h in historico)

    def test_obter_por_date_range(self, db_session: Session, cotacao_data: dict):
        """Deve obter cotações entre datas"""
        repo = CotacaoRepository(db_session)
        
        for i in range(10):
            data = date(2026, 4, 1) + timedelta(days=i)
            repo.criar({**cotacao_data, "data_referencia": data})
        
        resultado = repo.obter_por_date_range(
            data_inicio=date(2026, 4, 5),
            data_fim=date(2026, 4, 8)
        )
        
        assert len(resultado) == 4
        assert all(date(2026, 4, 5) <= c.data_referencia <= date(2026, 4, 8) for c in resultado)

    def test_atualizar_cotacao(self, db_session: Session, cotacao_data: dict):
        """Deve atualizar uma cotação existente"""
        repo = CotacaoRepository(db_session)
        criada = repo.criar(cotacao_data)
        
        criada.preco_arroba = 300.0
        atualizada = repo.atualizar(criada)
        
        obtida = repo.obter_por_id(atualizada.id)
        assert obtida.preco_arroba == 300.0

    def test_deletar_cotacao(self, db_session: Session, cotacao_data: dict):
        """Deve deletar uma cotação"""
        repo = CotacaoRepository(db_session)
        criada = repo.criar(cotacao_data)
        cotacao_id = criada.id
        
        repo.deletar(criada)
        
        obtida = repo.obter_por_id(cotacao_id)
        assert obtida is None

    def test_contar_cotacoes(self, db_session: Session, cotacao_data: dict):
        """Deve contar total de cotações"""
        repo = CotacaoRepository(db_session)
        repo.criar(cotacao_data)
        repo.criar({**cotacao_data, "data_referencia": date(2026, 4, 14)})
        
        total = repo.contar()
        
        assert total >= 2
