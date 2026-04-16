"""
Repository Pattern para acesso à dados
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Pesagem
from app.schemas import PesagemCreate, PesagemUpdate


class PesagemRepository:
    """Repositório para operações de Pesagem no banco"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, pesagem_data: PesagemCreate) -> Pesagem:
        """Cria nova pesagem"""
        # Calcular arroba (peso / 15)
        peso_arroba = pesagem_data.peso_kg / 15
        
        pesagem = Pesagem(
            **pesagem_data.model_dump(),
            peso_arroba=peso_arroba
        )
        self.db.add(pesagem)
        self.db.commit()
        self.db.refresh(pesagem)
        return pesagem

    def get_by_id(self, pesagem_id: int) -> Optional[Pesagem]:
        """Obtém pesagem por ID"""
        return self.db.query(Pesagem).filter(Pesagem.id == pesagem_id).first()

    def get_by_animal(self, animal_id: int, skip: int = 0, limit: int = 100) -> List[Pesagem]:
        """Obtém pesagens de um animal"""
        return (self.db.query(Pesagem)
                .filter(Pesagem.animal_id == animal_id)
                .order_by(Pesagem.data.desc())
                .offset(skip)
                .limit(limit)
                .all())

    def get_last_pesagem(self, animal_id: int) -> Optional[Pesagem]:
        """Obtém última pesagem de um animal"""
        return (self.db.query(Pesagem)
                .filter(Pesagem.animal_id == animal_id)
                .order_by(Pesagem.data.desc())
                .first())

    def get_by_date_range(self, animal_id: int, data_inicio: date, data_fim: date) -> List[Pesagem]:
        """Obtém pesagens em um período"""
        return (self.db.query(Pesagem)
                .filter(and_(
                    Pesagem.animal_id == animal_id,
                    Pesagem.data >= data_inicio,
                    Pesagem.data <= data_fim
                ))
                .order_by(Pesagem.data.asc())
                .all())

    def update(self, pesagem_id: int, pesagem_data: PesagemUpdate) -> Optional[Pesagem]:
        """Atualiza pesagem"""
        pesagem = self.get_by_id(pesagem_id)
        if not pesagem:
            return None
        
        update_data = pesagem_data.model_dump(exclude_unset=True)
        
        # Recalcular arroba se peso foi atualizado
        if 'peso_kg' in update_data:
            update_data['peso_arroba'] = update_data['peso_kg'] / 15
        
        for key, value in update_data.items():
            setattr(pesagem, key, value)
        
        self.db.commit()
        self.db.refresh(pesagem)
        return pesagem

    def delete(self, pesagem_id: int) -> bool:
        """Deleta pesagem"""
        pesagem = self.get_by_id(pesagem_id)
        if not pesagem:
            return False
        
        self.db.delete(pesagem)
        self.db.commit()
        return True

    def count_by_animal(self, animal_id: int) -> int:
        """Conta pesagens de um animal"""
        return self.db.query(Pesagem).filter(Pesagem.animal_id == animal_id).count()
