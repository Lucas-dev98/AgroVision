"""
Testes para Services (Lógica de Negócio)
"""
import pytest
from datetime import date, timedelta
from app.services import PesagemService
from app.schemas import PesagemCreate


class TestPesagemService:
    """Testes do serviço de negócio Pesagem"""
    
    def test_calcular_arroba(self):
        """Testa cálculo de arroba"""
        assert PesagemService.calcular_arroba(450) == 30.0
        assert PesagemService.calcular_arroba(150) == 10.0
        assert PesagemService.calcular_arroba(300) == 20.0

    def test_calcular_valor(self):
        """Testa cálculo de valor"""
        valor = PesagemService.calcular_valor(30.0, 280.50)
        assert valor == 8415.0

    def test_registrar_pesagem(self, db_session, pesagem_data):
        """Testa registrar pesagem"""
        service = PesagemService(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        
        pesagem = service.registrar_pesagem(pesagem_create)
        
        assert pesagem.id is not None
        assert pesagem.peso_arroba == 30.0

    def test_obter_pesagem(self, db_session, pesagem_data):
        """Testa obter pesagem"""
        service = PesagemService(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        created = service.registrar_pesagem(pesagem_create)
        
        retrieved = service.obter_pesagem(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_obter_ultima_pesagem(self, db_session, pesagem_data):
        """Testa obter última pesagem"""
        service = PesagemService(db_session)
        
        # Criar 2 pesagens
        for i in range(2):
            data = pesagem_data.copy()
            data["peso_kg"] = 450 + i * 10
            data["data"] = date(2026, 4, 15) + timedelta(days=i)
            service.registrar_pesagem(PesagemCreate(**data))
        
        ultima = service.obter_ultima_pesagem(1)
        assert ultima is not None
        assert ultima.peso_kg == 460.0

    def test_calcular_ganho(self, db_session, pesagem_data):
        """Testa cálculo de ganho"""
        service = PesagemService(db_session)
        
        # Criar 2 pesagens com diferença
        data1 = pesagem_data.copy()
        data1["peso_kg"] = 450.0
        data1["data"] = date(2026, 4, 15)
        service.registrar_pesagem(PesagemCreate(**data1))
        
        data2 = pesagem_data.copy()
        data2["peso_kg"] = 460.0
        data2["data"] = date(2026, 4, 22)
        service.registrar_pesagem(PesagemCreate(**data2))
        
        ganho = service.calcular_ganho(1, date(2026, 4, 15), date(2026, 4, 22))
        assert ganho is not None
        assert ganho.ganho_kg == 10.0
        assert ganho.ganho_arroba == pytest.approx(10.0 / 15)

    def test_atualizar_pesagem(self, db_session, pesagem_data):
        """Testa atualizar pesagem"""
        from app.schemas import PesagemUpdate
        
        service = PesagemService(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        created = service.registrar_pesagem(pesagem_create)
        
        update_data = PesagemUpdate(peso_kg=500.0)
        updated = service.atualizar_pesagem(created.id, update_data)
        
        assert updated is not None
        assert updated.peso_kg == 500.0

    def test_deletar_pesagem(self, db_session, pesagem_data):
        """Testa deletar pesagem"""
        service = PesagemService(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        created = service.registrar_pesagem(pesagem_create)
        
        deleted = service.deletar_pesagem(created.id)
        assert deleted is True
        
        result = service.obter_pesagem(created.id)
        assert result is None
