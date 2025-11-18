from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class DoctorProfileBase(BaseModel):
    crm: str
    crm_state: str
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#2563eb"
    secondary_color: Optional[str] = "#1e40af"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    footer_text: Optional[str] = None

    @validator('crm_state')
    def validate_crm_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('CRM state must be 2 characters')
        return v.upper()

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must start with #')
        if v and len(v) != 7:
            raise ValueError('Color must be in format #RRGGBB')
        return v

class DoctorProfileCreate(DoctorProfileBase):
    pass

class DoctorProfileUpdate(BaseModel):
    crm: Optional[str] = None
    crm_state: Optional[str] = None
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    footer_text: Optional[str] = None

    @validator('crm_state')
    def validate_crm_state(cls, v):
        if v and len(v) != 2:
            raise ValueError('CRM state must be 2 characters')
        return v.upper() if v else None

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must start with #')
        if v and len(v) != 7:
            raise ValueError('Color must be in format #RRGGBB')
        return v

class DoctorProfileResponse(DoctorProfileBase):
    id: UUID
    user_id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
