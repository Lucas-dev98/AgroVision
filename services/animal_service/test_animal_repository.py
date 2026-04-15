"""
TESTES UNITÁRIOS - Animal Repository
TDD Phase 1: RED - Escrevemos os testes ANTES do código
Fase 2: GREEN - Fazemos o código passar
Fase 3: REFACTOR - Melhoramos o código
"""
import pytest
from uuid import uuid4
from shared.schemas import AnimalCreate, AnimalUpdate, AnimalStatus


class TestAnimalRepositoryCreate:
    """Testes para criar animais"""

    def test_create_animal_success(self, animal_repository, animal_create_dto):
        """
        GIVEN: DTO válido para criar animal
        WHEN: Chamar repository.create()
        THEN: Deve retornar AnimalModel com ID gerado
        """
        # Act
        animal = animal_repository.create(animal_create_dto)

        # Assert
        assert animal.id is not None
        assert animal.ear_tag == "001"
        assert animal.name == "Bessie"
        assert animal.breed == "Nelore"
        assert animal.gender == "F"
        assert animal.status == "active"
        assert animal.created_at is not None
        assert animal.updated_at is not None

    def test_create_animal_with_minimal_data(self, animal_repository, db):
        """
        GIVEN: Apenas dados obrigatórios (breed, gender)
        WHEN: Criar animal
        THEN: Deve funcionar com valores opcionais como None
        """
        # Arrange
        animal_data = AnimalCreate(
            breed="Nelore",
            gender="M",
            ear_tag="minimal"
        )
        
        # Act
        animal = animal_repository.create(animal_data)

        # Assert
        assert animal.id is not None
        assert animal.breed == "Nelore"
        assert animal.name is None
        assert animal.birth_date is None

    def test_create_duplicate_ear_tag_should_fail(self, animal_repository, animal_create_dto):
        """
        GIVEN: Dois animais com mesmo ear_tag
        WHEN: Criar segundo animal
        THEN: Deve lançar erro de constraint UNIQUE
        """
        # Arrange
        animal_repository.create(animal_create_dto)
        duplicate_data = AnimalCreate(
            ear_tag="001",  # Mesmo ear_tag
            breed="Brahman",
            gender="M"
        )

        # Act & Assert
        with pytest.raises(Exception):  # IntegrityError
            animal_repository.create(duplicate_data)


class TestAnimalRepositoryRead:
    """Testes para ler/buscar animais"""

    def test_get_by_id_success(self, animal_repository, created_animal):
        """
        GIVEN: Um animal já criado
        WHEN: Buscar por ID
        THEN: Deve retornar o animal
        """
        # Act
        animal = animal_repository.get_by_id(created_animal.id)

        # Assert
        assert animal is not None
        assert animal.id == created_animal.id
        assert animal.ear_tag == "001"

    def test_get_by_id_not_found(self, animal_repository):
        """
        GIVEN: ID que não existe
        WHEN: Buscar por ID
        THEN: Deve retornar None
        """
        # Act
        animal = animal_repository.get_by_id(uuid4())

        # Assert
        assert animal is None

    def test_get_by_ear_tag_success(self, animal_repository, created_animal):
        """
        GIVEN: Um animal já criado
        WHEN: Buscar por ear_tag
        THEN: Deve retornar o animal
        """
        # Act
        animal = animal_repository.get_by_ear_tag("001")

        # Assert
        assert animal is not None
        assert animal.ear_tag == "001"
        assert animal.name == "Bessie"

    def test_get_by_ear_tag_not_found(self, animal_repository):
        """
        GIVEN: ear_tag que não existe
        WHEN: Buscar
        THEN: Deve retornar None
        """
        # Act
        animal = animal_repository.get_by_ear_tag("99999")

        # Assert
        assert animal is None

    def test_list_all_empty(self, animal_repository):
        """
        GIVEN: Banco vazio
        WHEN: Listar animais
        THEN: Deve retornar lista vazia
        """
        # Act
        animals, total = animal_repository.list_all()

        # Assert
        assert len(animals) == 0
        assert total == 0

    def test_list_all_with_animals(self, animal_repository, created_animal, created_animal_2):
        """
        GIVEN: Dois animais criados
        WHEN: Listar todos
        THEN: Deve retornar 2 animais
        """
        # Act
        animals, total = animal_repository.list_all()

        # Assert
        assert len(animals) == 2
        assert total == 2

    def test_list_all_with_pagination(self, animal_repository, created_animal, created_animal_2):
        """
        GIVEN: Dois animais
        WHEN: Listar com limit=1
        THEN: Deve retornar apenas 1, mas total=2
        """
        # Act
        animals, total = animal_repository.list_all(skip=0, limit=1)

        # Assert
        assert len(animals) == 1
        assert total == 2

    def test_list_all_with_status_filter(self, animal_repository, created_animal, db):
        """
        GIVEN: Um animal ativo e um vendido
        WHEN: Filtrar por status ACTIVE
        THEN: Deve retornar apenas o ativo
        """
        # Arrange - Criar animal com status vendido
        inactive_animal_data = AnimalCreate(
            ear_tag="sold_001",
            breed="Nelore",
            gender="F",
            status="sold"
        )
        animal_repository.create(inactive_animal_data)

        # Act
        animals, total = animal_repository.list_all(status=AnimalStatus.ACTIVE)

        # Assert
        assert len(animals) == 1  # Apenas o first created_animal
        assert animals[0].status == "active"

    def test_search_by_name(self, animal_repository, created_animal):
        """
        GIVEN: Animal com name "Bessie"
        WHEN: Buscar por "Bess"
        THEN: Deve encontrar (case-insensitive)
        """
        # Act
        animals = animal_repository.search("bess")

        # Assert
        assert len(animals) == 1
        assert animals[0].name == "Bessie"

    def test_search_by_breed(self, animal_repository, created_animal, created_animal_2):
        """
        GIVEN: Dois animais diferentes (Nelore, Brahman)
        WHEN: Buscar por "brahman"
        THEN: Deve encontrar apenas o Brahman
        """
        # Act
        animals = animal_repository.search("brahman")

        # Assert
        assert len(animals) == 1
        assert animals[0].breed == "Brahman"


class TestAnimalRepositoryUpdate:
    """Testes para atualizar animais"""

    def test_update_animal_success(self, animal_repository, created_animal):
        """
        GIVEN: Animal existente
        WHEN: Atualizar name e status
        THEN: Deve retornar animal atualizado
        """
        # Arrange
        update_data = AnimalUpdate(
            name="Bessie Atualizada",
            status=AnimalStatus.SOLD
        )

        # Act
        updated = animal_repository.update(created_animal.id, update_data)

        # Assert
        assert updated is not None
        assert updated.name == "Bessie Atualizada"
        assert updated.status == "sold"
        assert updated.ear_tag == "001"  # Não muda

    def test_update_animal_not_found(self, animal_repository):
        """
        GIVEN: ID que não existe
        WHEN: Tentar atualizar
        THEN: Deve retornar None
        """
        # Arrange
        update_data = AnimalUpdate(name="Novo Nome")

        # Act
        result = animal_repository.update(uuid4(), update_data)

        # Assert
        assert result is None

    def test_update_only_provided_fields(self, animal_repository, created_animal):
        """
        GIVEN: Animal existente
        WHEN: Atualizar apenas um campo (name)
        THEN: Outros campos devem manter valores anteriores
        """
        # Arrange
        original_breed = created_animal.breed
        update_data = AnimalUpdate(name="Novo Nome")

        # Act
        updated = animal_repository.update(created_animal.id, update_data)

        # Assert
        assert updated.name == "Novo Nome"
        assert updated.breed == original_breed  # Keep original


class TestAnimalRepositoryDelete:
    """Testes para deletar animais"""

    def test_delete_animal_soft_delete(self, animal_repository, created_animal):
        """
        GIVEN: Animal existente
        WHEN: Deletar
        THEN: Deve marcar como DEAD (soft delete), não remover do BD
        """
        # Act
        result = animal_repository.delete(created_animal.id)

        # Assert
        assert result is True
        animal = animal_repository.get_by_id(created_animal.id)
        assert animal is not None
        assert animal.status == AnimalStatus.DEAD

    def test_delete_animal_not_found(self, animal_repository):
        """
        GIVEN: ID que não existe
        WHEN: Tentar deletar
        THEN: Deve retornar False
        """
        # Act
        result = animal_repository.delete(uuid4())

        # Assert
        assert result is False


class TestAnimalRepositoryAggregations:
    """Testes para agregações e contagens"""

    def test_count_total(self, animal_repository, created_animal, created_animal_2):
        """
        GIVEN: Dois animais criados
        WHEN: Contar total
        THEN: Deve retornar 2
        """
        # Act
        total = animal_repository.count_total()

        # Assert
        assert total == 2

    def test_count_by_status_active(self, animal_repository, created_animal, db):
        """
        GIVEN: Um animal ativo
        WHEN: Contar por status ACTIVE
        THEN: Deve retornar 1
        """
        # Act
        count = animal_repository.count_by_status(AnimalStatus.ACTIVE)

        # Assert
        assert count == 1

    def test_list_by_breed(self, animal_repository, created_animal, created_animal_2):
        """
        GIVEN: Dois animais diferentes (Nelore, Brahman)
        WHEN: Listar por breed "Nelore"
        THEN: Deve retornar apenas Nelore
        """
        # Act
        animals = animal_repository.list_by_breed("Nelore")

        # Assert
        assert len(animals) == 1
        assert animals[0].breed == "Nelore"

    def test_list_active(self, animal_repository, created_animal, db):
        """
        GIVEN: Um animal ativo
        WHEN: Listar apenas ativos
        THEN: Deve retornar o ativo
        """
        # Act
        animals, total = animal_repository.list_active()

        # Assert
        assert len(animals) == 1
        assert total == 1
