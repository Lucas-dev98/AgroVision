"""
Repository Pattern para Animal Service
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from services.animal_service.models import AnimalModel
from shared.schemas import AnimalStatus, AnimalGender, AnimalCreate, AnimalUpdate


class AnimalRepository:
    """Repositório para operações de Animal no banco"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, animal_data: AnimalCreate) -> AnimalModel:
        """
        Cria novo animal
        
        Args:
            animal_data: Dados do animal
        
        Returns:
            AnimalModel criado
        """
        animal = AnimalModel(**animal_data.model_dump())
        self.db.add(animal)
        self.db.commit()
        self.db.refresh(animal)
        return animal

    def get_by_id(self, animal_id: UUID) -> Optional[AnimalModel]:
        """
        Obtém animal por ID
        
        Args:
            animal_id: UUID do animal
        
        Returns:
            AnimalModel ou None
        """
        return self.db.query(AnimalModel).filter(
            AnimalModel.id == animal_id
        ).first()

    def get_by_ear_tag(self, ear_tag: str) -> Optional[AnimalModel]:
        """
        Obtém animal por ear_tag
        
        Args:
            ear_tag: Identificação física do animal
        
        Returns:
            AnimalModel ou None
        """
        return self.db.query(AnimalModel).filter(
            AnimalModel.ear_tag == ear_tag
        ).first()

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AnimalStatus] = None,
        breed: Optional[str] = None
    ) -> tuple[List[AnimalModel], int]:
        """
        Lista animais com filtros opcionais
        
        Args:
            skip: Offset
            limit: Limit de registros
            status: Filtrar por status
            breed: Filtrar por raça
        
        Returns:
            Tupla (lista_animais, total_count)
        """
        query = self.db.query(AnimalModel)

        # Filtros opcionais
        if status:
            query = query.filter(AnimalModel.status == status)
        if breed:
            query = query.filter(AnimalModel.breed == breed)

        total = query.count()
        animals = query.offset(skip).limit(limit).all()

        return animals, total

    def update(self, animal_id: UUID, update_data: AnimalUpdate) -> Optional[AnimalModel]:
        """
        Atualiza animal existente
        
        Args:
            animal_id: UUID do animal
            update_data: Dados para atualizar
        
        Returns:
            AnimalModel atualizado ou None
        """
        animal = self.get_by_id(animal_id)
        if not animal:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(animal, key, value)

        self.db.commit()
        self.db.refresh(animal)
        return animal

    def delete(self, animal_id: UUID) -> bool:
        """
        Deleta animal (soft delete mudando status)
        
        Args:
            animal_id: UUID do animal
        
        Returns:
            True se deletado, False se não encontrado
        """
        animal = self.get_by_id(animal_id)
        if not animal:
            return False

        # Soft delete - mudar status para 'dead' em vez de remover
        animal.status = AnimalStatus.DEAD
        self.db.commit()
        return True

    def list_by_breed(self, breed: str) -> List[AnimalModel]:
        """
        Lista todos animais de uma raça específica
        
        Args:
            breed: Nome da raça
        
        Returns:
            Lista de AnimalModel
        """
        return self.db.query(AnimalModel).filter(
            and_(
                AnimalModel.breed == breed,
                AnimalModel.status == AnimalStatus.ACTIVE
            )
        ).all()

    def list_active(self, skip: int = 0, limit: int = 100) -> tuple[List[AnimalModel], int]:
        """
        Lista apenas animais ativos
        
        Args:
            skip: Offset
            limit: Limit
        
        Returns:
            Tupla (lista_animais, total_count)
        """
        return self.list_all(skip=skip, limit=limit, status=AnimalStatus.ACTIVE)

    def count_by_status(self, status: AnimalStatus) -> int:
        """
        Conta animais por status
        
        Args:
            status: Status para contar
        
        Returns:
            Número de animais com esse status
        """
        return self.db.query(AnimalModel).filter(
            AnimalModel.status == status
        ).count()

    def count_total(self) -> int:
        """Conta total de animais"""
        return self.db.query(AnimalModel).count()

    def search(self, query: str) -> List[AnimalModel]:
        """
        Busca animais por name, ear_tag ou breed
        
        Args:
            query: String de busca
        
        Returns:
            Lista de animais encontrados
        """
        return self.db.query(AnimalModel).filter(
            or_(
                AnimalModel.name.ilike(f"%{query}%"),
                AnimalModel.ear_tag.ilike(f"%{query}%"),
                AnimalModel.breed.ilike(f"%{query}%")
            )
        ).all()
