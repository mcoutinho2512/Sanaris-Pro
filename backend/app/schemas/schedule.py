from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, time
from uuid import UUID

# ==========================================
# PROFESSIONAL SCHEDULE SCHEMAS
# ==========================================

class ProfessionalScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Segunda, 6=Domingo")
    start_time: time = Field(..., description="Horário de início")
    end_time: time = Field(..., description="Horário de fim")
    break_start: Optional[time] = Field(None, description="Início do intervalo")
    break_end: Optional[time] = Field(None, description="Fim do intervalo")
    default_duration_minutes: int = Field(30, ge=15, le=180, description="Duração padrão em minutos")
    settings: Dict[str, Any] = Field(default_factory=dict)

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time deve ser maior que start_time')
        return v

    @validator('break_end')
    def validate_break_end(cls, v, values):
        if v and 'break_start' in values:
            if not values['break_start']:
                raise ValueError('break_start é obrigatório quando break_end é definido')
            if v <= values['break_start']:
                raise ValueError('break_end deve ser maior que break_start')
        return v

class ProfessionalScheduleCreate(ProfessionalScheduleBase):
    user_id: UUID

class ProfessionalScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    default_duration_minutes: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ProfessionalScheduleResponse(ProfessionalScheduleBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProfessionalScheduleBulkCreate(BaseModel):
    """Schema para criar horários de vários dias de uma vez"""
    user_id: UUID
    schedules: List[ProfessionalScheduleBase]

# ==========================================
# SCHEDULE BLOCK SCHEMAS
# ==========================================

class ScheduleBlockBase(BaseModel):
    block_date: datetime
    start_time: time
    end_time: time
    reason: Optional[str] = Field(None, max_length=255)
    block_type: str = Field('custom', max_length=50)
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time deve ser maior que start_time')
        return v

class ScheduleBlockCreate(ScheduleBlockBase):
    user_id: UUID

class ScheduleBlockUpdate(BaseModel):
    block_date: Optional[datetime] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None
    block_type: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ScheduleBlockResponse(ScheduleBlockBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# AVAILABILITY SCHEMAS (para consultas)
# ==========================================

class TimeSlot(BaseModel):
    """Representa um horário disponível"""
    start: datetime
    end: datetime
    duration_minutes: int

class AvailabilityRequest(BaseModel):
    """Request para buscar disponibilidade"""
    user_id: UUID
    date: datetime
    duration_minutes: Optional[int] = 30

class AvailabilityResponse(BaseModel):
    """Response com horários disponíveis"""
    date: datetime
    professional_id: UUID
    professional_name: str
    available_slots: List[TimeSlot]
    total_slots: int

class WeekScheduleResponse(BaseModel):
    """Resposta com horários da semana"""
    user_id: UUID
    schedules: List[ProfessionalScheduleResponse]
