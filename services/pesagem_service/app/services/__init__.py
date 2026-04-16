"""
Business Logic Layer - Cálculos critérios
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.repositories import PesagemRepository
from app.schemas import PesagemCreate, PesagemUpdate, PesagemResponse, GanhoResponse, ValorResponse
from app.models import Pesagem


class PesagemService:
    """Serviço de lógica de negócio para Pesagens"""

    def __init__(self, db: Session):
        self.repository = PesagemRepository(db)

    @staticmethod
    def calcular_arroba(peso_kg: float) -> float:
        """Calcula arroba a partir de kg"""
        return peso_kg / 15

    @staticmethod
    def calcular_valor(peso_arroba: float, preco_arroba: float) -> float:
        """Calcula valor total da pesagem"""
        return peso_arroba * preco_arroba

    def registrar_pesagem(self, pesagem_data: PesagemCreate) -> PesagemResponse:
        """Registra novo pesagem"""
        pesagem = self.repository.create(pesagem_data)
        return PesagemResponse.model_validate(pesagem)

    def obter_pesagem(self, pesagem_id: int) -> Optional[PesagemResponse]:
        """Obtém pesagem por ID"""
        pesagem = self.repository.get_by_id(pesagem_id)
        if pesagem:
            return PesagemResponse.model_validate(pesagem)
        return None

    def obter_historico(self, animal_id: int, skip: int = 0, limit: int = 100) -> List[PesagemResponse]:
        """Obtém histórico de pesagens de um animal"""
        pesagens = self.repository.get_by_animal(animal_id, skip, limit)
        return [PesagemResponse.model_validate(p) for p in pesagens]

    def obter_ultima_pesagem(self, animal_id: int) -> Optional[PesagemResponse]:
        """Obtém última pesagem de um animal"""
        pesagem = self.repository.get_last_pesagem(animal_id)
        if pesagem:
            return PesagemResponse.model_validate(pesagem)
        return None

    def calcular_ganho(self, animal_id: int, data_inicio: date, data_fim: date) -> Optional[GanhoResponse]:
        """Calcula ganho de peso em um período"""
        pesagens = self.repository.get_by_date_range(animal_id, data_inicio, data_fim)
        
        if len(pesagens) < 2:
            return None
        
        primeira = pesagens[0]
        ultima = pesagens[-1]
        
        ganho_kg = ultima.peso_kg - primeira.peso_kg
        ganho_arroba = ultima.peso_arroba - primeira.peso_arroba
        
        return GanhoResponse(
            animal_id=animal_id,
            ganho_kg=ganho_kg,
            ganho_arroba=ganho_arroba,
            data_inicial=primeira.data,
            data_final=ultima.data
        )

    def atualizar_pesagem(self, pesagem_id: int, pesagem_data: PesagemUpdate) -> Optional[PesagemResponse]:
        """Atualiza pesagem"""
        pesagem = self.repository.update(pesagem_id, pesagem_data)
        if pesagem:
            return PesagemResponse.model_validate(pesagem)
        return None

    def deletar_pesagem(self, pesagem_id: int) -> bool:
        """Deleta pesagem"""
        return self.repository.delete(pesagem_id)

    def contar_pesagens_animal(self, animal_id: int) -> int:
        """Conta pesagens de um animal"""
        return self.repository.count_by_animal(animal_id)
