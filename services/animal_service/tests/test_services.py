"""
Testes para Services (Lógica de Negócio)
"""
import pytest
from datetime import date
from app.services import AnimalService
from app.schemas import AnimalCreate, AnimalUpdate


class TestAnimalService:
    """Testes do serviço de negócio Animal"""
    
    def test_criar_animal(self, db_session, animal_data):
        """Testa criar animal via service"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        
        animal = service.criar_animal(animal_create)
        
        assert animal.id is not None
        assert animal.nome == "Boi Bravo"
        assert animal.rfid == "BOI_001"

    def test_criar_animal_rfid_duplicado(self, db_session, animal_data):
        """Testa validação de RFID duplicado"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        
        # Criar primeiro animal
        service.criar_animal(animal_create)
        
        # Tentar criar outro com mesmo RFID
        with pytest.raises(ValueError, match="já existe"):
            service.criar_animal(animal_create)

    def test_obter_animal(self, db_session, animal_data):
        """Testa obter animal"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        created = service.criar_animal(animal_create)
        
        retrieved = service.obter_animal(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_obter_animal_inexistente(self, db_session):
        """Testa obter animal que não existe"""
        service = AnimalService(db_session)
        result = service.obter_animal(99999)
        assert result is None

    def test_obter_por_rfid(self, db_session, animal_data):
        """Testa obter por RFID"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        service.criar_animal(animal_create)
        
        retrieved = service.obter_por_rfid("BOI_001")
        assert retrieved is not None
        assert retrieved.rfid == "BOI_001"

    def test_listar_animais(self, db_session, animal_data):
        """Testa listar animais"""
        service = AnimalService(db_session)
        
        # Criar 3 animais
        for i in range(3):
            data = animal_data.copy()
            data["rfid"] = f"BOI_{i:03d}"
            service.criar_animal(AnimalCreate(**data))
        
        animais = service.listar_animais()
        assert len(animais) >= 3

    def test_atualizar_animal(self, db_session, animal_data):
        """Testa atualizar animal"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        created = service.criar_animal(animal_create)
        
        update_data = AnimalUpdate(nome="Novo Nome")
        updated = service.atualizar_animal(created.id, update_data)
        
        assert updated is not None
        assert updated.nome == "Novo Nome"

    def test_deletar_animal(self, db_session, animal_data):
        """Testa deletar animal"""
        service = AnimalService(db_session)
        animal_create = AnimalCreate(**animal_data)
        created = service.criar_animal(animal_create)
        
        deleted = service.deletar_animal(created.id)
        assert deleted is True
        
        # Verificar que foi deletado
        result = service.obter_animal(created.id)
        assert result is None

    def test_contar_animais(self, db_session, animal_data):
        """Testa contar animais"""
        service = AnimalService(db_session)
        
        inicial = service.contar_animais()
        
        # Criar 1 animal
        animal_create = AnimalCreate(**animal_data)
        service.criar_animal(animal_create)
        
        final = service.contar_animais()
        assert final == inicial + 1
