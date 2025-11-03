"""
Schemas para Agendamento - COMPLETO (com UUID)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


# ============================================
# ENUMS
# ============================================

class AppointmentStatus(str, Enum):
    """Status do agendamento"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(str, Enum):
    """Tipo de consulta"""
    FIRST_TIME = "first_time"
    RETURN = "return"
    EMERGENCY = "emergency"
    TELEMEDICINE = "telemedicine"


class ConfirmationMethod(str, Enum):
    """Método de confirmação"""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    NONE = "none"


# ============================================
# SCHEMAS DE AGENDAMENTO
# ============================================

class AppointmentBase(BaseModel):
    """Schema base de agendamento"""
    patient_id: str
    healthcare_professional_id: str
    scheduled_date: datetime
    duration_minutes: int = Field(default=30, ge=5, le=480)
    appointment_type: AppointmentType = AppointmentType.FIRST_TIME
    
    reason: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)


class AppointmentCreate(AppointmentBase):
    """Schema para criação de agendamento"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema para atualização de agendamento"""
    patient_id: Optional[str] = None
    healthcare_professional_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    
    reason: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    paid: Optional[bool] = None
    payment_method: Optional[str] = None


class AppointmentConfirm(BaseModel):
    """Schema para confirmação de agendamento"""
    confirmation_method: ConfirmationMethod
    confirmed_by: str = "patient"


class AppointmentCancel(BaseModel):
    """Schema para cancelamento"""
    cancellation_reason: str = Field(..., min_length=5)


class AppointmentResponse(AppointmentBase):
    """Schema de resposta de agendamento"""
    id: str
    status: AppointmentStatus
    
    # Confirmação
    confirmation_sent: bool
    confirmation_sent_at: Optional[datetime] = None
    confirmation_method: ConfirmationMethod
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None
    
    # Check-in e atendimento
    checked_in_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Lista de espera
    is_waitlist: bool
    waitlist_priority: int
    
    # Financeiro
    paid: bool
    payment_method: Optional[str] = None
    
    # Cancelamento
    cancellation_reason: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    healthcare_professional_id: str
    scheduled_date: datetime
    duration_minutes: int
    appointment_type: AppointmentType
    status: AppointmentStatus
    confirmed_at: Optional[datetime] = None
    reason: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE LISTA DE ESPERA
# ============================================

class WaitlistCreate(BaseModel):
    """Schema para adicionar à lista de espera"""
    patient_id: str
    healthcare_professional_id: Optional[str] = None
    preferred_date: Optional[datetime] = None
    preferred_period: Optional[str] = Field(None, pattern="^(morning|afternoon|evening)$")
    appointment_type: AppointmentType = AppointmentType.FIRST_TIME
    priority: int = Field(default=0, ge=0, le=10)
    urgency_level: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    reason: Optional[str] = None
    notes: Optional[str] = None


class WaitlistResponse(BaseModel):
    """Schema de resposta da lista de espera"""
    id: str
    patient_id: str
    healthcare_professional_id: Optional[str] = None
    preferred_date: Optional[datetime] = None
    preferred_period: Optional[str] = None
    appointment_type: AppointmentType
    priority: int
    urgency_level: Optional[str] = None
    is_active: bool
    notified: bool
    notified_at: Optional[datetime] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE ESCALA
# ============================================

class ScheduleCreate(BaseModel):
    """Schema para criar horário de trabalho"""
    healthcare_professional_id: str
    day_of_week: int = Field(..., ge=0, le=6)
    start_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    break_start_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    break_end_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    default_appointment_duration: int = Field(default=30, ge=5, le=240)


class ScheduleResponse(BaseModel):
    """Schema de resposta de horário"""
    id: str
    healthcare_professional_id: str
    day_of_week: int
    start_time: str
    end_time: str
    break_start_time: Optional[str] = None
    break_end_time: Optional[str] = None
    default_appointment_duration: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
