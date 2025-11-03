"""
Schemas para Documentos e Termos
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class DocumentType(str, Enum):
    """Tipo de documento"""
    TERM = "term"
    CONSENT = "consent"
    CONTRACT = "contract"
    DECLARATION = "declaration"
    ANAMNESIS = "anamnesis"


# ============================================
# SCHEMAS DE TEMPLATES
# ============================================

class DocumentTemplateBase(BaseModel):
    """Schema base de template"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: DocumentType
    category: Optional[str] = None
    content: str = Field(..., min_length=1)
    available_variables: Optional[str] = None
    requires_signature: bool = True
    requires_witness: bool = False


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema para criação de template"""
    pass


class DocumentTemplateUpdate(BaseModel):
    """Schema para atualização de template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    category: Optional[str] = None
    content: Optional[str] = None
    available_variables: Optional[str] = None
    requires_signature: Optional[bool] = None
    requires_witness: Optional[bool] = None
    is_active: Optional[bool] = None


class DocumentTemplateResponse(DocumentTemplateBase):
    """Schema de resposta de template"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE DOCUMENTOS DO PACIENTE
# ============================================

class PatientDocumentBase(BaseModel):
    """Schema base de documento do paciente"""
    patient_id: str
    appointment_id: Optional[str] = None
    template_id: Optional[str] = None
    document_type: DocumentType
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class PatientDocumentCreate(PatientDocumentBase):
    """Schema para criação de documento"""
    pass


class PatientDocumentSign(BaseModel):
    """Schema para assinatura de documento"""
    signature: str = Field(..., min_length=1)
    signer_type: str = Field(..., pattern="^(patient|witness|professional)$")
    witness_name: Optional[str] = None


class PatientDocumentResponse(PatientDocumentBase):
    """Schema de resposta de documento"""
    id: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    
    patient_signature: Optional[str] = None
    patient_signed_at: Optional[datetime] = None
    
    witness_name: Optional[str] = None
    witness_signature: Optional[str] = None
    witness_signed_at: Optional[datetime] = None
    
    professional_signature: Optional[str] = None
    professional_signed_at: Optional[datetime] = None
    
    is_signed: bool
    is_sent: bool
    sent_at: Optional[datetime] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class PatientDocumentListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    document_type: DocumentType
    title: str
    is_signed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE PRÉ-CADASTRO
# ============================================

class QuickPatientRegistrationBase(BaseModel):
    """Schema base de pré-cadastro"""
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    cpf: Optional[str] = Field(None, min_length=11, max_length=14)
    email: Optional[str] = None
    birth_date: Optional[datetime] = None


class QuickPatientRegistrationCreate(QuickPatientRegistrationBase):
    """Schema para criação de pré-cadastro"""
    appointment_id: Optional[str] = None
    created_by: Optional[str] = None


class QuickPatientRegistrationConvert(BaseModel):
    """Schema para conversão em paciente completo"""
    additional_data: Optional[dict] = None


class QuickPatientRegistrationResponse(QuickPatientRegistrationBase):
    """Schema de resposta de pré-cadastro"""
    id: str
    is_converted: bool
    patient_id: Optional[str] = None
    converted_at: Optional[datetime] = None
    created_by: Optional[str] = None
    appointment_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS COMBINADOS
# ============================================

class AppointmentWithDocuments(BaseModel):
    """Schema de agendamento com documentos"""
    appointment_id: str
    documents: List[PatientDocumentResponse] = []


class GenerateDocumentFromTemplate(BaseModel):
    """Schema para gerar documento a partir de template"""
    template_id: str
    patient_id: str
    appointment_id: Optional[str] = None
    variables: Optional[dict] = None  # Variáveis para substituir no template
