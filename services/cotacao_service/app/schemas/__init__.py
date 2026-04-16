from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional


class CotacaoCreate(BaseModel):
    """Schema para criação de cotação"""
    preco_arroba: float = Field(..., gt=0, description="Preço da arroba em reais")
    data_referencia: date = Field(..., description="Data de referência da cotação")
    
    @field_validator("preco_arroba")
    @classmethod
    def validar_preco(cls, v):
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v


class CotacaoUpdate(BaseModel):
    """Schema para atualização de cotação"""
    preco_arroba: Optional[float] = Field(None, gt=0, description="Preço da arroba em reais")
    data_referencia: Optional[date] = Field(None, description="Data de referência da cotação")


class CotacaoResponse(BaseModel):
    """Schema de resposta para cotação"""
    model_config = ConfigDict(from_attributes=True, ser_json_schema=True)
    
    id: int
    preco_arroba: float
    data_referencia: date
    criada_em: datetime
    atualizada_em: datetime


class CotacaoHistorico(BaseModel):
    """Schema para histórico agregado de cotações"""
    data_referencia: date
    preco_medio: float
    preco_minimo: float
    preco_maximo: float
    quantidade_registros: int


class MediaResponse(BaseModel):
    """Schema para resposta de média de preço"""
    media: float
    dias: int
    data_inicio: date
    data_fim: date
