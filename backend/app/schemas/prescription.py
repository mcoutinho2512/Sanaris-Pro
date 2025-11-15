from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PrescriptionType(str, Enum):
    REGULAR = "regular"
    CONTROLLED = "controlled"
    SPECIAL = "special"

class PrescriptionItemBase(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    is_generic: bool = True
    is_controlled: bool = False

class PrescriptionItemCreate(PrescriptionItemBase):
    pass

class PrescriptionItemUpdate(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None

class PrescriptionItemResponse(PrescriptionItemBase):
    id: UUID4
    prescription_id: UUID4
    
    class Config:
        from_attributes = True

class PrescriptionBase(BaseModel):
    patient_id: UUID4
    healthcare_professional_id: UUID4
    prescription_type: PrescriptionType
    general_instructions: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    items: List[PrescriptionItemCreate]

class PrescriptionUpdate(BaseModel):
    general_instructions: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    id: UUID4
    prescription_date: datetime
    is_signed: bool
    items: List[PrescriptionItemResponse] = []
    
    class Config:
        from_attributes = True

class PrescriptionListResponse(BaseModel):
    id: UUID4
    patient_id: UUID4
    healthcare_professional_id: UUID4
    prescription_date: datetime
    prescription_type: PrescriptionType
    general_instructions: Optional[str] = None
    is_signed: bool
    
    class Config:
        from_attributes = True

class PrescriptionSendEmail(BaseModel):
    prescription_id: UUID4
    recipient_email: str

class PrescriptionSendWhatsApp(BaseModel):
    prescription_id: UUID4
    phone_number: str
    
class PrescriptionSendSMS(BaseModel):
    prescription_id: UUID4
    phone_number: str

class PrescriptionSign(BaseModel):
    prescription_id: UUID4
    professional_signature: str
    crm_number: str
    crm_state: str

class PrescriptionDispense(BaseModel):
    prescription_id: UUID4
    pharmacy_name: str
    pharmacist_name: str
    notes: Optional[str] = None

class PrescriptionPrint(BaseModel):
    prescription_id: UUID4

# ============================================
# PRESCRIPTION TEMPLATES
# ============================================
class PrescriptionTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    prescription_type: PrescriptionType
    general_instructions: Optional[str] = None

class PrescriptionTemplateCreate(PrescriptionTemplateBase):
    items: List[PrescriptionItemCreate]

class PrescriptionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    general_instructions: Optional[str] = None

class PrescriptionTemplateResponse(PrescriptionTemplateBase):
    id: UUID4
    healthcare_professional_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True
