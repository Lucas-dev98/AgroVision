"""
Business Logic Layer
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories import AnimalRepository
from app.schemas import AnimalCreate, AnimalUpdate, AnimalResponse
from app.models import Animal


class AnimalService:
    """Serviço de lógica de negócio para Animais"""

    def __init__(self, db: Session):
        self.repository = AnimalRepository(db)

    def criar_animal(self, animal_data: AnimalCreate) -> AnimalResponse:
        """
        Cria novo animal
        
        Args:
            animal_data: Dados do animal
        
        Returns:
            AnimalResponse
        
        Raises:
            ValueError: Se RFID já existir
        """
        # Validar se RFID já existe
        if animal_data.rfid:
            animal_existente = self.repository.get_by_rfid(animal_data.rfid)
            if animal_existente:
                raise ValueError(f"RFID {animal_data.rfid} já existe")
        
        animal = self.repository.create(animal_data)
        return AnimalResponse.model_validate(animal)

    def obter_animal(self, animal_id: int) -> Optional[AnimalResponse]:
        """
        Obtém animal por ID
        
        Args:
            animal_id: ID do animal
        
        Returns:
            AnimalResponse ou None
        """
        animal = self.repository.get_by_id(animal_id)
        if animal:
            return AnimalResponse.model_validate(animal)
        return None

    def obter_por_rfid(self, rfid: str) -> Optional[AnimalResponse]:
        """
        Obtém animal por RFID
        
        Args:
            rfid: RFID do animal
        
        Returns:
            AnimalResponse ou None
        """
        animal = self.repository.get_by_rfid(rfid)
        if animal:
            return AnimalResponse.model_validate(animal)
        return None

    def listar_animais(self, skip: int = 0, limit: int = 100) -> List[AnimalResponse]:
        """
        Lista todos os animais
        
        Args:
            skip: Paginação
            limit: Limite de registros
        
        Returns:
            Lista de AnimalResponse
        """
        animais = self.repository.list_all(skip, limit)
        return [AnimalResponse.model_validate(animal) for animal in animais]

    def atualizar_animal(self, animal_id: int, animal_data: AnimalUpdate) -> Optional[AnimalResponse]:
        """
        Atualiza animal
        
        Args:
            animal_id: ID do animal
            animal_data: Dados para atualizar
        
        Returns:
            AnimalResponse atualizado ou None
        """
        animal = self.repository.update(animal_id, animal_data)
        if animal:
            return AnimalResponse.model_validate(animal)
        return None

    def deletar_animal(self, animal_id: int) -> bool:
        """
        Deleta animal
        
        Args:
            animal_id: ID do animal
        
        Returns:
            True se deletado
        """
        return self.repository.delete(animal_id)

    def contar_animais(self) -> int:
        """
        Conta total de animais
        
        Returns:
            Total de animais
        """
        return self.repository.count()
