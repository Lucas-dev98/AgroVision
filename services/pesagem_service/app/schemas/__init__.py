"""
Schemas (Pydantic) para validação de dados
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class PesagemCreate(BaseModel):
    """Schema para criar pesagem"""
    animal_id: int = Field(..., gt=0)
    peso_kg: float = Field(..., gt=0, le=1000)
    data: Optional[date] = None
    hora: Optional[str] = None
    observacoes: Optional[str] = None


class PesagemUpdate(BaseModel):
    """Schema para atualizar pesagem"""
    peso_kg: Optional[float] = Field(None, gt=0, le=1000)
    observacoes: Optional[str] = None


class PesagemResponse(BaseModel):
    """Schema para retornar pesagem"""
    id: int
    animal_id: int
    peso_kg: float
    peso_arroba: float
    data: date
    hora: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GanhoResponse(BaseModel):
    """Schema para retornar ganho de peso"""
    animal_id: int
    ganho_kg: float
    ganho_arroba: float
    data_inicial: date
    data_final: date


class ValorResponse(BaseModel):
    """Schema para retornar valor calculado"""
    animal_id: int
    peso_arroba: float
    preco_arroba: float
    valor_total: float
    data_pesagem: date
