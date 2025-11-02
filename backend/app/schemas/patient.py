from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class PatientBase(BaseModel):
    full_name: str
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class PatientCreate(PatientBase):
    tenant_id: str

class PatientResponse(PatientBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
