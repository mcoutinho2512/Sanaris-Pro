from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime, time
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentType(str, Enum):
    FIRST_TIME = "first_time"
    RETURN = "return"
    EMERGENCY = "emergency"
    TELEMEDICINE = "telemedicine"

class ConfirmationMethod(str, Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    NONE = "none"

class AppointmentBase(BaseModel):
    patient_id: UUID4
    healthcare_professional_id: UUID4
    scheduled_date: datetime
    duration_minutes: int = 30
    appointment_type: AppointmentType = AppointmentType.FIRST_TIME
    reason: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[float] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_id: Optional[UUID4] = None
    healthcare_professional_id: Optional[UUID4] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    price: Optional[float] = None
    paid: Optional[bool] = None
    payment_method: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: UUID4
    status: AppointmentStatus
    paid: bool
    payment_method: Optional[str] = None
    confirmation_sent: bool
    confirmation_sent_at: Optional[datetime] = None
    confirmation_method: ConfirmationMethod
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None
    checked_in_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentListResponse(BaseModel):
    id: UUID4
    patient_id: UUID4
    healthcare_professional_id: UUID4
    scheduled_date: datetime
    duration_minutes: int
    appointment_type: AppointmentType
    status: AppointmentStatus
    reason: Optional[str] = None
    confirmation_sent: bool
    confirmed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AppointmentSendConfirmation(BaseModel):
    method: ConfirmationMethod

class AppointmentConfirm(BaseModel):
    confirmation_method: ConfirmationMethod
    confirmed_by: str = "patient"

class AppointmentCancel(BaseModel):
    cancellation_reason: str

# Waitlist schemas
class WaitlistCreate(BaseModel):
    patient_id: UUID4
    healthcare_professional_id: UUID4
    preferred_date: Optional[datetime] = None
    reason: Optional[str] = None
    priority: int = 0

class WaitlistResponse(BaseModel):
    id: UUID4
    patient_id: UUID4
    healthcare_professional_id: UUID4
    preferred_date: Optional[datetime] = None
    reason: Optional[str] = None
    priority: int
    notified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schedule schemas
class ScheduleCreate(BaseModel):
    healthcare_professional_id: UUID4
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool = True

class ScheduleResponse(BaseModel):
    id: UUID4
    healthcare_professional_id: UUID4
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
