from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    patient_id: str
    professional_id: str
    appointment_date: datetime
    duration_minutes: int = 30
    appointment_type: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    tenant_id: str

class AppointmentResponse(AppointmentBase):
    id: str
    tenant_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
