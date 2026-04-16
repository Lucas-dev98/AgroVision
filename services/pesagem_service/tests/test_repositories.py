"""
Testes para Repositories
"""
import pytest
from datetime import date, timedelta
from app.repositories import PesagemRepository
from app.schemas import PesagemCreate, PesagemUpdate


class TestPesagemRepository:
    """Testes do repositório Pesagem"""
    
    def test_create_pesagem(self, db_session, pesagem_data):
        """Testa criar pesagem"""
        repo = PesagemRepository(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        pesagem = repo.create(pesagem_create)
        
        assert pesagem.id is not None
        assert pesagem.animal_id == 1
        assert pesagem.peso_kg == 450.0
        assert pesagem.peso_arroba == 30.0  # 450 / 15

    def test_get_by_id(self, db_session, pesagem_data):
        """Testa obter pesagem por ID"""
        repo = PesagemRepository(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        pesagem = repo.create(pesagem_create)
        
        retrieved = repo.get_by_id(pesagem.id)
        assert retrieved is not None
        assert retrieved.id == pesagem.id
        assert retrieved.peso_kg == 450.0

    def test_get_by_animal(self, db_session, pesagem_data):
        """Testa obter pesagens de um animal"""
        repo = PesagemRepository(db_session)
        
        # Criar 3 pesagens
        for i in range(3):
            data = pesagem_data.copy()
            data["peso_kg"] = 450 + i * 10
            data["data"] = date(2026, 4, 15) + timedelta(days=i)
            repo.create(PesagemCreate(**data))
        
        pesagens = repo.get_by_animal(1)
        assert len(pesagens) >= 3

    def test_get_last_pesagem(self, db_session, pesagem_data):
        """Testa obter última pesagem"""
        repo = PesagemRepository(db_session)
        
        # Criar 2 pesagens
        for i in range(2):
            data = pesagem_data.copy()
            data["peso_kg"] = 450 + i * 10
            data["data"] = date(2026, 4, 15) + timedelta(days=i)
            repo.create(PesagemCreate(**data))
        
        last = repo.get_last_pesagem(1)
        assert last is not None
        assert last.peso_kg == 460.0

    def test_get_by_date_range(self, db_session, pesagem_data):
        """Testa obter pesagens em período"""
        repo = PesagemRepository(db_session)
        
        # Criar 5 pesagens em 5 dias
        for i in range(5):
            data = pesagem_data.copy()
            data["data"] = date(2026, 4, 15) + timedelta(days=i)
            repo.create(PesagemCreate(**data))
        
        pesagens = repo.get_by_date_range(1, date(2026, 4, 16), date(2026, 4, 18))
        assert len(pesagens) >= 2

    def test_update_pesagem(self, db_session, pesagem_data):
        """Testa atualizar pesagem"""
        repo = PesagemRepository(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        pesagem = repo.create(pesagem_create)
        
        update_data = PesagemUpdate(peso_kg=500.0)
        updated = repo.update(pesagem.id, update_data)
        
        assert updated is not None
        assert updated.peso_kg == 500.0
        assert updated.peso_arroba == 500.0 / 15

    def test_delete_pesagem(self, db_session, pesagem_data):
        """Testa deletar pesagem"""
        repo = PesagemRepository(db_session)
        pesagem_create = PesagemCreate(**pesagem_data)
        pesagem = repo.create(pesagem_create)
        
        deleted = repo.delete(pesagem.id)
        assert deleted is True
        
        retrieved = repo.get_by_id(pesagem.id)
        assert retrieved is None

    def test_count_by_animal(self, db_session, pesagem_data):
        """Testa contar pesagens"""
        repo = PesagemRepository(db_session)
        
        # Criar 3 pesagens
        for i in range(3):
            data = pesagem_data.copy()
            data["data"] = date(2026, 4, 15) + timedelta(days=i)
            repo.create(PesagemCreate(**data))
        
        count = repo.count_by_animal(1)
        assert count >= 3
