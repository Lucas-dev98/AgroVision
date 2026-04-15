from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== ENUMS ====================

class AnimalStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    DEAD = "dead"


class AnimalGender(str, Enum):
    MALE = "M"
    FEMALE = "F"


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class VaccineStatus(str, Enum):
    APPLIED = "applied"
    PENDING = "pending"
    OVERDUE = "overdue"


# ==================== BASE MODELS ====================

class TimestampedModel(BaseModel):
    """Base model com timestamps"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UUIDModel(BaseModel):
    """Base model com UUID"""
    id: UUID

    class Config:
        from_attributes = True


# ==================== ANIMAL SCHEMAS ====================

class AnimalBase(BaseModel):
    """Schema base para Animal"""
    ear_tag: Optional[str] = None
    name: Optional[str] = None
    breed: str
    birth_date: Optional[datetime] = None
    gender: AnimalGender
    status: AnimalStatus = AnimalStatus.ACTIVE
    mother_id: Optional[UUID] = None
    father_id: Optional[UUID] = None
    detected_by_yolo: bool = False
    notes: Optional[str] = None


class AnimalCreate(AnimalBase):
    """Schema para criar Animal"""
    pass


class AnimalUpdate(BaseModel):
    """Schema para atualizar Animal"""
    name: Optional[str] = None
    status: Optional[AnimalStatus] = None
    notes: Optional[str] = None


class AnimalResponse(AnimalBase, UUIDModel, TimestampedModel):
    """Schema para resposta de Animal"""
    pass


class AnimalListResponse(BaseModel):
    """Schema para lista de Animals"""
    total: int
    items: list[AnimalResponse]
    page: int
    page_size: int


# ==================== WEIGHING SCHEMAS ====================

class WeighingRecordBase(BaseModel):
    """Schema base para WeighingRecord"""
    animal_id: UUID
    weight_kg: float = Field(gt=0, description="Peso em quilos")
    weight_arrobas: float = Field(gt=0, description="Peso em arrobas")
    recorded_at: datetime
    notes: Optional[str] = None


class WeighingRecordCreate(BaseModel):
    """Schema para criar WeighingRecord (apenas kg, calcula arrobas)"""
    animal_id: UUID
    weight_kg: float = Field(gt=0)
    recorded_at: datetime
    notes: Optional[str] = None


class WeighingRecordResponse(WeighingRecordBase, UUIDModel, TimestampedModel):
    """Schema para resposta de WeighingRecord"""
    pass


# ==================== VACCINE SCHEMAS ====================

class VaccineBase(BaseModel):
    """Schema base para Vaccine"""
    animal_id: UUID
    vaccine_name: str
    application_date: datetime
    next_dose_date: Optional[datetime] = None
    status: VaccineStatus = VaccineStatus.APPLIED
    veterinarian: Optional[str] = None
    notes: Optional[str] = None


class VaccineCreate(VaccineBase):
    """Schema para criar Vaccine"""
    pass


class VaccineResponse(VaccineBase, UUIDModel, TimestampedModel):
    """Schema para resposta de Vaccine"""
    pass


# ==================== ERROR SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Schema de resposta de erro"""
    detail: str
    error_code: Optional[str] = None
    status_code: int
