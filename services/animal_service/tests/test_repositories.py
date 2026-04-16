"""
Testes para Repositories
"""
import pytest
from datetime import date
from app.repositories import AnimalRepository
from app.schemas import AnimalCreate, AnimalUpdate


class TestAnimalRepository:
    """Testes do repositório Animal"""
    
    def test_create_animal(self, db_session, animal_data):
        """Testa criar animal"""
        repo = AnimalRepository(db_session)
        animal_create = AnimalCreate(**animal_data)
        animal = repo.create(animal_create)
        
        assert animal.id is not None
        assert animal.nome == "Boi Bravo"
        assert animal.rfid == "BOI_001"

    def test_get_by_id(self, db_session, animal_data):
        """Testa obter animal por ID"""
        repo = AnimalRepository(db_session)
        animal_create = AnimalCreate(**animal_data)
        animal = repo.create(animal_create)
        
        retrieved = repo.get_by_id(animal.id)
        assert retrieved is not None
        assert retrieved.id == animal.id
        assert retrieved.nome == "Boi Bravo"

    def test_get_by_id_not_found(self, db_session):
        """Testa obter animal inexistente"""
        repo = AnimalRepository(db_session)
        animal = repo.get_by_id(99999)
        assert animal is None

    def test_get_by_rfid(self, db_session, animal_data):
        """Testa obter animal por RFID"""
        repo = AnimalRepository(db_session)
        animal_create = AnimalCreate(**animal_data)
        repo.create(animal_create)
        
        retrieved = repo.get_by_rfid("BOI_001")
        assert retrieved is not None
        assert retrieved.rfid == "BOI_001"

    def test_list_all(self, db_session, animal_data):
        """Testa listar todos os animais"""
        repo = AnimalRepository(db_session)
        
        # Criar 3 animais
        for i in range(3):
            data = animal_data.copy()
            data["rfid"] = f"BOI_00{i}"
            repo.create(AnimalCreate(**data))
        
        animais = repo.list_all()
        assert len(animais) >= 3

    def test_list_all_pagination(self, db_session, animal_data):
        """Testa paginação"""
        repo = AnimalRepository(db_session)
        
        # Criar 5 animais
        for i in range(5):
            data = animal_data.copy()
            data["rfid"] = f"BOI_{i:03d}"
            repo.create(AnimalCreate(**data))
        
        # Skip 2, limit 2
        animais = repo.list_all(skip=2, limit=2)
        assert len(animais) <= 2

    def test_update_animal(self, db_session, animal_data):
        """Testa atualizar animal"""
        repo = AnimalRepository(db_session)
        animal_create = AnimalCreate(**animal_data)
        animal = repo.create(animal_create)
        
        update_data = AnimalUpdate(nome="Novo Nome")
        updated = repo.update(animal.id, update_data)
        
        assert updated is not None
        assert updated.nome == "Novo Nome"

    def test_update_not_found(self, db_session):
        """Testa atualizar animal inexistente"""
        repo = AnimalRepository(db_session)
        update_data = AnimalUpdate(nome="Novo")
        result = repo.update(99999, update_data)
        assert result is None

    def test_delete_animal(self, db_session, animal_data):
        """Testa deletar animal"""
        repo = AnimalRepository(db_session)
        animal_create = AnimalCreate(**animal_data)
        animal = repo.create(animal_create)
        
        deleted = repo.delete(animal.id)
        assert deleted is True
        
        # Verificar que foi deletado
        retrieved = repo.get_by_id(animal.id)
        assert retrieved is None

    def test_delete_not_found(self, db_session):
        """Testa deletar animal inexistente"""
        repo = AnimalRepository(db_session)
        result = repo.delete(99999)
        assert result is False

    def test_count_animals(self, db_session, animal_data):
        """Testa contar animais"""
        repo = AnimalRepository(db_session)
        
        inicial = repo.count()
        
        # Criar 2 animais
        for i in range(2):
            data = animal_data.copy()
            data["rfid"] = f"BOI_{i:04d}"
            repo.create(AnimalCreate(**data))
        
        final = repo.count()
        assert final == inicial + 2
