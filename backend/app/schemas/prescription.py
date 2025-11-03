"""
Schemas para Prescrição Digital - COMPLETO
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class PrescriptionType(str, Enum):
    """Tipo de prescrição"""
    REGULAR = "regular"
    CONTROLLED = "controlled"
    SPECIAL = "special"


class PharmaceuticalForm(str, Enum):
    """Forma farmacêutica"""
    TABLET = "comprimido"
    CAPSULE = "cápsula"
    SYRUP = "xarope"
    SUSPENSION = "suspensão"
    DROPS = "gotas"
    OINTMENT = "pomada"
    CREAM = "creme"
    INJECTION = "injetável"
    SUPPOSITORY = "supositório"
    OTHER = "outro"


class RouteOfAdministration(str, Enum):
    """Via de administração"""
    ORAL = "oral"
    TOPICAL = "tópica"
    INTRAVENOUS = "intravenosa"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutânea"
    RECTAL = "retal"
    OPHTHALMIC = "oftálmica"
    NASAL = "nasal"
    OTHER = "outra"


# ============================================
# SCHEMAS DE ITENS DA PRESCRIÇÃO
# ============================================

class PrescriptionItemBase(BaseModel):
    """Schema base de item da prescrição"""
    medication_name: str = Field(..., min_length=1, max_length=255)
    active_ingredient: Optional[str] = Field(None, max_length=255)
    concentration: Optional[str] = Field(None, max_length=100)
    pharmaceutical_form: Optional[str] = None
    
    dosage: str = Field(..., min_length=1)
    frequency: str = Field(..., min_length=1)
    duration: Optional[str] = None
    route_of_administration: Optional[str] = None
    
    quantity: Optional[int] = Field(None, ge=0)
    quantity_unit: Optional[str] = None
    
    instructions: Optional[str] = None
    
    is_generic: bool = False
    is_controlled: bool = False
    
    display_order: int = 0


class PrescriptionItemCreate(PrescriptionItemBase):
    """Schema para criação de item"""
    pass


class PrescriptionItemUpdate(BaseModel):
    """Schema para atualização de item"""
    medication_name: Optional[str] = Field(None, min_length=1, max_length=255)
    active_ingredient: Optional[str] = None
    concentration: Optional[str] = None
    pharmaceutical_form: Optional[str] = None
    
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    route_of_administration: Optional[str] = None
    
    quantity: Optional[int] = Field(None, ge=0)
    quantity_unit: Optional[str] = None
    
    instructions: Optional[str] = None
    
    is_generic: Optional[bool] = None
    is_controlled: Optional[bool] = None
    
    display_order: Optional[int] = None


class PrescriptionItemResponse(PrescriptionItemBase):
    """Schema de resposta de item"""
    id: str
    prescription_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE PRESCRIÇÃO
# ============================================

class PrescriptionBase(BaseModel):
    """Schema base de prescrição"""
    patient_id: str
    medical_record_id: Optional[str] = None
    healthcare_professional_id: str
    prescription_type: PrescriptionType = PrescriptionType.REGULAR
    
    valid_until: Optional[datetime] = None
    general_instructions: Optional[str] = None
    
    crm_number: Optional[str] = None
    crm_state: Optional[str] = None
    
    notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    """Schema para criação de prescrição"""
    prescription_date: Optional[datetime] = None
    items: List[PrescriptionItemCreate] = []


class PrescriptionUpdate(BaseModel):
    """Schema para atualização de prescrição"""
    prescription_type: Optional[PrescriptionType] = None
    valid_until: Optional[datetime] = None
    general_instructions: Optional[str] = None
    notes: Optional[str] = None


class PrescriptionResponse(PrescriptionBase):
    """Schema de resposta de prescrição"""
    id: str
    prescription_date: datetime
    
    is_printed: bool
    printed_at: Optional[datetime] = None
    
    is_signed: bool
    signed_at: Optional[datetime] = None
    professional_signature: Optional[str] = None
    
    is_dispensed: bool
    dispensed_at: Optional[datetime] = None
    pharmacy_name: Optional[str] = None
    pharmacist_name: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    items: List[PrescriptionItemResponse] = []
    
    class Config:
        from_attributes = True


class PrescriptionListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    healthcare_professional_id: str
    prescription_date: datetime
    prescription_type: PrescriptionType
    is_signed: bool
    is_dispensed: bool
    items_count: int = 0
    
    class Config:
        from_attributes = True


class PrescriptionSign(BaseModel):
    """Schema para assinatura digital"""
    crm_number: str = Field(..., min_length=1)
    crm_state: str = Field(..., min_length=2, max_length=2)
    signature: Optional[str] = None


class PrescriptionDispense(BaseModel):
    """Schema para registro de dispensação"""
    pharmacy_name: str = Field(..., min_length=1)
    pharmacist_name: str = Field(..., min_length=1)


# ============================================
# SCHEMAS DE TEMPLATES
# ============================================

class PrescriptionTemplateBase(BaseModel):
    """Schema base de template"""
    template_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: bool = False


class PrescriptionTemplateCreate(PrescriptionTemplateBase):
    """Schema para criação de template"""
    healthcare_professional_id: str
    template_data: str  # JSON com os medicamentos


class PrescriptionTemplateUpdate(BaseModel):
    """Schema para atualização de template"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    template_data: Optional[str] = None


class PrescriptionTemplateResponse(PrescriptionTemplateBase):
    """Schema de resposta de template"""
    id: str
    healthcare_professional_id: str
    is_active: bool
    usage_count: int
    template_data: str
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
