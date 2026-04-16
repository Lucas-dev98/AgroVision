"""
Schemas (Pydantic) para validação de dados
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class AnimalStatus(str, Enum):
    """Status do animal"""
    ATIVO = "ativo"
    VENDIDO = "vendido"
    FALECIDO = "falecido"


class AnimalCreate(BaseModel):
    """Schema para criar animal"""
    nome: str = Field(..., min_length=1, max_length=100)
    raca: str = Field(..., max_length=50)
    data_nascimento: Optional[date] = None
    rfid: Optional[str] = Field(None, max_length=50)
    lote_id: Optional[int] = None
    peso_inicial: Optional[float] = None


class AnimalUpdate(BaseModel):
    """Schema para atualizar animal"""
    nome: Optional[str] = None
    raca: Optional[str] = None
    rfid: Optional[str] = None
    status: Optional[AnimalStatus] = None


class AnimalResponse(BaseModel):
    """Schema para retornar animal"""
    id: int
    nome: str
    raca: str
    data_nascimento: Optional[date]
    rfid: Optional[str]
    lote_id: Optional[int]
    status: AnimalStatus
    peso_inicial: Optional[float]
    data_entrada: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnimalListResponse(BaseModel):
    """Schema para retornar lista de animais"""
    total: int
    animais: list[AnimalResponse]
