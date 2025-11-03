"""
Schemas para Prontuário Eletrônico - COMPLETO
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================
# ENUMS
# ============================================

class RecordType(str, Enum):
    """Tipo de atendimento"""
    CONSULTATION = "consultation"
    EMERGENCY = "emergency"
    FOLLOWUP = "followup"
    TELEMEDICINE = "telemedicine"


class AttachmentType(str, Enum):
    """Tipo de anexo"""
    EXAM = "exam"
    IMAGE = "image"
    DOCUMENT = "document"
    PRESCRIPTION = "prescription"
    OTHER = "other"


# ============================================
# SCHEMAS DE SINAIS VITAIS
# ============================================

class VitalSignsBase(BaseModel):
    """Schema base de sinais vitais"""
    systolic_pressure: Optional[int] = Field(None, ge=50, le=300)
    diastolic_pressure: Optional[int] = Field(None, ge=30, le=200)
    heart_rate: Optional[int] = Field(None, ge=30, le=250)
    respiratory_rate: Optional[int] = Field(None, ge=8, le=60)
    temperature: Optional[Decimal] = Field(None, ge=35.0, le=42.0)
    oxygen_saturation: Optional[int] = Field(None, ge=0, le=100)
    
    weight: Optional[Decimal] = Field(None, ge=0, le=500)
    height: Optional[Decimal] = Field(None, ge=0, le=250)
    bmi: Optional[Decimal] = None
    
    glucose: Optional[int] = Field(None, ge=0, le=1000)
    
    notes: Optional[str] = None
    measured_by: Optional[str] = None


class VitalSignsCreate(VitalSignsBase):
    """Schema para criação de sinais vitais"""
    measured_at: Optional[datetime] = None


class VitalSignsUpdate(VitalSignsBase):
    """Schema para atualização de sinais vitais"""
    pass


class VitalSignsResponse(VitalSignsBase):
    """Schema de resposta de sinais vitais"""
    id: str
    medical_record_id: str
    measured_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE ANEXOS
# ============================================

class AttachmentBase(BaseModel):
    """Schema base de anexo"""
    file_name: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    attachment_type: AttachmentType = AttachmentType.OTHER
    description: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    """Schema para criação de anexo"""
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None


class AttachmentResponse(AttachmentBase):
    """Schema de resposta de anexo"""
    id: str
    medical_record_id: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE PRONTUÁRIO ELETRÔNICO
# ============================================

class MedicalRecordBase(BaseModel):
    """Schema base de prontuário"""
    patient_id: str
    appointment_id: Optional[str] = None
    healthcare_professional_id: str
    record_type: RecordType = RecordType.CONSULTATION
    
    # Triagem
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    
    # Anamnese
    past_medical_history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    review_of_systems: Optional[str] = None
    
    # Exame Físico
    general_appearance: Optional[str] = None
    head_neck: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    abdomen: Optional[str] = None
    extremities: Optional[str] = None
    neurological: Optional[str] = None
    skin: Optional[str] = None
    additional_findings: Optional[str] = None
    
    # Diagnóstico e Conduta
    diagnosis: Optional[str] = None
    icd10_codes: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescriptions: Optional[str] = None
    exams_requested: Optional[str] = None
    referrals: Optional[str] = None
    observations: Optional[str] = None
    
    # Retorno
    followup_date: Optional[date] = None
    followup_notes: Optional[str] = None
    
    # Assinatura
    professional_signature: Optional[str] = None
    crm_number: Optional[str] = None
    crm_state: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    """Schema para criação de prontuário"""
    record_date: Optional[datetime] = None


class MedicalRecordUpdate(BaseModel):
    """Schema para atualização de prontuário"""
    record_type: Optional[RecordType] = None
    
    # Triagem
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    
    # Anamnese
    past_medical_history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    review_of_systems: Optional[str] = None
    
    # Exame Físico
    general_appearance: Optional[str] = None
    head_neck: Optional[str] = None
    cardiovascular: Optional[str] = None
    respiratory: Optional[str] = None
    abdomen: Optional[str] = None
    extremities: Optional[str] = None
    neurological: Optional[str] = None
    skin: Optional[str] = None
    additional_findings: Optional[str] = None
    
    # Diagnóstico e Conduta
    diagnosis: Optional[str] = None
    icd10_codes: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescriptions: Optional[str] = None
    exams_requested: Optional[str] = None
    referrals: Optional[str] = None
    observations: Optional[str] = None
    
    # Retorno
    followup_date: Optional[date] = None
    followup_notes: Optional[str] = None
    
    # Assinatura
    professional_signature: Optional[str] = None
    crm_number: Optional[str] = None
    crm_state: Optional[str] = None
    
    # Controle
    is_completed: Optional[bool] = None


class MedicalRecordResponse(MedicalRecordBase):
    """Schema de resposta de prontuário"""
    id: str
    record_date: datetime
    is_completed: bool
    completed_at: Optional[datetime] = None
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    
    # Relacionamentos
    vital_signs: List[VitalSignsResponse] = []
    attachments: List[AttachmentResponse] = []
    
    class Config:
        from_attributes = True


class MedicalRecordListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    healthcare_professional_id: str
    record_date: datetime
    record_type: RecordType
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    is_completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
