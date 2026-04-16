"""
Repository Pattern para acesso à dados
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Animal
from app.schemas import AnimalCreate, AnimalUpdate, AnimalResponse


class AnimalRepository:
    """Repositório para operações de Animal no banco"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, animal_data: AnimalCreate) -> Animal:
        """
        Cria novo animal
        
        Args:
            animal_data: Dados do animal
        
        Returns:
            Animal criado
        """
        animal = Animal(**animal_data.model_dump())
        self.db.add(animal)
        self.db.commit()
        self.db.refresh(animal)
        return animal

    def get_by_id(self, animal_id: int) -> Optional[Animal]:
        """
        Obtém animal por ID
        
        Args:
            animal_id: ID do animal
        
        Returns:
            Animal ou None
        """
        return self.db.query(Animal).filter(Animal.id == animal_id).first()

    def get_by_rfid(self, rfid: str) -> Optional[Animal]:
        """
        Obtém animal por RFID
        
        Args:
            rfid: RFID do animal
        
        Returns:
            Animal ou None
        """
        return self.db.query(Animal).filter(Animal.rfid == rfid).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Animal]:
        """
        Lista todos os animais com paginação
        
        Args:
            skip: Quantos registros pular
            limit: Quantos registros retornar
        
        Returns:
            Lista de animais
        """
        return self.db.query(Animal).offset(skip).limit(limit).all()

    def update(self, animal_id: int, animal_data: AnimalUpdate) -> Optional[Animal]:
        """
        Atualiza animal
        
        Args:
            animal_id: ID do animal
            animal_data: Dados para atualizar
        
        Returns:
            Animal atualizado ou None
        """
        animal = self.get_by_id(animal_id)
        if not animal:
            return None
        
        update_data = animal_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(animal, key, value)
        
        self.db.commit()
        self.db.refresh(animal)
        return animal

    def delete(self, animal_id: int) -> bool:
        """
        Deleta animal
        
        Args:
            animal_id: ID do animal
        
        Returns:
            True se deletado, False se não encontrado
        """
        animal = self.get_by_id(animal_id)
        if not animal:
            return False
        
        self.db.delete(animal)
        self.db.commit()
        return True

    def count(self) -> int:
        """
        Conta total de animais
        
        Returns:
            Total de animais
        """
        return self.db.query(Animal).count()
