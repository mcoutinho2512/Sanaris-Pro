"""
Schemas para Faturamento TISS
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================
# ENUMS
# ============================================

class HealthInsuranceTypeEnum(str, Enum):
    """Tipo de operadora"""
    MEDICAL = "medical"
    COOPERATIVE = "cooperative"
    PHILANTHROPIC = "philanthropic"
    SELF_MANAGEMENT = "self_management"


class GuideTypeEnum(str, Enum):
    """Tipo de guia"""
    CONSULTATION = "consultation"
    SADT = "sadt"
    HOSPITALIZATION = "hospitalization"
    HONORARIUM = "honorarium"
    RESUME = "resume"


class GuideStatusEnum(str, Enum):
    """Status da guia"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PAID = "paid"
    GLOSS = "gloss"


class BatchStatusEnum(str, Enum):
    """Status do lote"""
    OPEN = "open"
    CLOSED = "closed"
    SENT = "sent"
    PROCESSED = "processed"


class ProcedureTypeEnum(str, Enum):
    """Tipo de procedimento"""
    CONSULTATION = "consultation"
    EXAM = "exam"
    THERAPY = "therapy"
    SURGERY = "surgery"
    HOSPITALIZATION = "hospitalization"
    OTHER = "other"


# ============================================
# OPERADORAS
# ============================================

class HealthInsuranceOperatorBase(BaseModel):
    """Schema base de operadora"""
    name: str = Field(..., min_length=1, max_length=255)
    commercial_name: Optional[str] = None
    ans_code: str = Field(..., min_length=6, max_length=6)
    operator_type: HealthInsuranceTypeEnum
    cnpj: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zipcode: Optional[str] = None
    tiss_version: str = Field("4.03.00", max_length=10)
    accepts_electronic_guide: bool = True
    requires_authorization: bool = False
    notes: Optional[str] = None


class HealthInsuranceOperatorCreate(HealthInsuranceOperatorBase):
    """Schema para criação"""
    pass


class HealthInsuranceOperatorUpdate(BaseModel):
    """Schema para atualização"""
    name: Optional[str] = None
    commercial_name: Optional[str] = None
    operator_type: Optional[HealthInsuranceTypeEnum] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    accepts_electronic_guide: Optional[bool] = None
    requires_authorization: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class HealthInsuranceOperatorResponse(BaseModel):
    """Schema de resposta"""
    id: str
    name: str
    commercial_name: Optional[str] = None
    ans_code: str
    operator_type: str
    cnpj: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    tiss_version: str
    accepts_electronic_guide: bool
    requires_authorization: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# PROCEDIMENTOS TUSS
# ============================================

class TussProcedureBase(BaseModel):
    """Schema base de procedimento"""
    code: str = Field(..., min_length=1, max_length=10)
    description: str = Field(..., min_length=1)
    procedure_type: ProcedureTypeEnum
    default_value: Optional[Decimal] = Field(None, ge=0)
    requires_authorization: bool = False
    quantity_limit: Optional[int] = Field(None, ge=1)


class TussProcedureCreate(TussProcedureBase):
    """Schema para criação"""
    pass


class TussProcedureUpdate(BaseModel):
    """Schema para atualização"""
    description: Optional[str] = None
    procedure_type: Optional[ProcedureTypeEnum] = None
    default_value: Optional[Decimal] = Field(None, ge=0)
    requires_authorization: Optional[bool] = None
    quantity_limit: Optional[int] = None
    is_active: Optional[bool] = None


class TussProcedureResponse(BaseModel):
    """Schema de resposta"""
    id: str
    code: str
    description: str
    procedure_type: str
    default_value: Optional[Decimal] = None
    requires_authorization: bool
    quantity_limit: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# BENEFICIÁRIOS
# ============================================

class BeneficiaryBase(BaseModel):
    """Schema base de beneficiário"""
    patient_id: str
    operator_id: str
    card_number: str = Field(..., min_length=1, max_length=20)
    registration_number: Optional[str] = None
    plan_name: Optional[str] = None
    plan_code: Optional[str] = None
    validity_start: Optional[date] = None
    validity_end: Optional[date] = None
    is_holder: bool = True
    holder_name: Optional[str] = None
    holder_cpf: Optional[str] = None
    cns: Optional[str] = Field(None, min_length=15, max_length=15)
    notes: Optional[str] = None


class BeneficiaryCreate(BeneficiaryBase):
    """Schema para criação"""
    pass


class BeneficiaryUpdate(BaseModel):
    """Schema para atualização"""
    card_number: Optional[str] = None
    registration_number: Optional[str] = None
    plan_name: Optional[str] = None
    plan_code: Optional[str] = None
    validity_start: Optional[date] = None
    validity_end: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class BeneficiaryResponse(BaseModel):
    """Schema de resposta"""
    id: str
    patient_id: str
    operator_id: str
    card_number: str
    registration_number: Optional[str] = None
    plan_name: Optional[str] = None
    plan_code: Optional[str] = None
    validity_start: Optional[date] = None
    validity_end: Optional[date] = None
    is_holder: bool
    holder_name: Optional[str] = None
    cns: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# PROCEDIMENTOS DA GUIA
# ============================================

class TissGuideProcedureCreate(BaseModel):
    """Schema para criação de procedimento da guia"""
    procedure_id: str
    procedure_code: str
    procedure_description: Optional[str] = None
    quantity: int = Field(1, ge=1)
    unit_value: Decimal = Field(..., ge=0)
    execution_date: Optional[date] = None
    access_route: Optional[str] = Field(None, max_length=2)
    technique: Optional[str] = Field(None, max_length=2)


class TissGuideProcedureResponse(BaseModel):
    """Schema de resposta"""
    id: str
    guide_id: str
    procedure_id: str
    procedure_code: str
    procedure_description: Optional[str] = None
    quantity: int
    unit_value: Decimal
    total_value: Decimal
    gloss_value: Decimal
    gloss_reason: Optional[str] = None
    execution_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# GUIAS TISS
# ============================================

class TissGuideCreate(BaseModel):
    """Schema para criação de guia"""
    guide_type: GuideTypeEnum
    operator_id: str
    beneficiary_id: str
    healthcare_professional_id: str
    appointment_id: Optional[str] = None
    medical_record_id: Optional[str] = None
    service_date: datetime
    authorization_number: Optional[str] = None
    authorization_date: Optional[date] = None
    cid_code: Optional[str] = Field(None, max_length=10)
    clinical_indication: Optional[str] = None
    observations: Optional[str] = None
    procedures: List[TissGuideProcedureCreate]


class TissGuideUpdate(BaseModel):
    """Schema para atualização"""
    authorization_number: Optional[str] = None
    authorization_date: Optional[date] = None
    cid_code: Optional[str] = None
    clinical_indication: Optional[str] = None
    observations: Optional[str] = None
    status: Optional[GuideStatusEnum] = None


class TissGuideResponse(BaseModel):
    """Schema de resposta"""
    id: str
    guide_number: str
    guide_type: str
    batch_id: Optional[str] = None
    operator_id: str
    beneficiary_id: str
    healthcare_professional_id: str
    appointment_id: Optional[str] = None
    medical_record_id: Optional[str] = None
    service_date: datetime
    issue_date: datetime
    authorization_number: Optional[str] = None
    authorization_date: Optional[date] = None
    total_value: Decimal
    accepted_value: Optional[Decimal] = None
    gloss_value: Decimal
    status: str
    gloss_reason: Optional[str] = None
    cid_code: Optional[str] = None
    clinical_indication: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TissGuideListResponse(BaseModel):
    """Schema de lista simplificada"""
    id: str
    guide_number: str
    guide_type: str
    operator_id: str
    beneficiary_id: str
    service_date: datetime
    total_value: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# LOTES TISS
# ============================================

class TissBatchCreate(BaseModel):
    """Schema para criação de lote"""
    operator_id: str
    reference_month: int = Field(..., ge=1, le=12)
    reference_year: int = Field(..., ge=2020, le=2100)
    notes: Optional[str] = None


class TissBatchUpdate(BaseModel):
    """Schema para atualização"""
    status: Optional[BatchStatusEnum] = None
    notes: Optional[str] = None


class TissBatchResponse(BaseModel):
    """Schema de resposta"""
    id: str
    batch_number: str
    operator_id: str
    reference_month: int
    reference_year: int
    ans_sequence: Optional[str] = None
    total_value: Decimal
    total_guides: int
    status: str
    closed_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    xml_file_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TissBatchListResponse(BaseModel):
    """Schema de lista simplificada"""
    id: str
    batch_number: str
    operator_id: str
    reference_month: int
    reference_year: int
    total_value: Decimal
    total_guides: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# AÇÕES ESPECIAIS
# ============================================

class AddGuideToBatchRequest(BaseModel):
    """Request para adicionar guia ao lote"""
    guide_id: str
    batch_id: str


class CloseBatchRequest(BaseModel):
    """Request para fechar lote"""
    batch_id: str


class GenerateTissXmlRequest(BaseModel):
    """Request para gerar XML TISS"""
    batch_id: str


class GlossGuideRequest(BaseModel):
    """Request para glosar guia"""
    guide_id: str
    gloss_value: Decimal = Field(..., ge=0)
    gloss_reason: str = Field(..., min_length=1)


# ============================================
# RELATÓRIOS
# ============================================

class TissSummaryByOperator(BaseModel):
    """Resumo por operadora"""
    operator_id: str
    operator_name: str
    total_guides: int
    total_value: Decimal
    accepted_value: Decimal
    gloss_value: Decimal


class TissSummaryByPeriod(BaseModel):
    """Resumo por período"""
    year: int
    month: int
    month_name: str
    total_guides: int
    total_value: Decimal
    total_batches: int


# ============================================
# LABELS EM PORTUGUÊS
# ============================================

OPERATOR_TYPE_LABELS = {
    "medical": "Medicina de Grupo",
    "cooperative": "Cooperativa Médica",
    "philanthropic": "Filantropia",
    "self_management": "Autogestão"
}

GUIDE_TYPE_LABELS = {
    "consultation": "Consulta",
    "sadt": "SP/SADT",
    "hospitalization": "Internação",
    "honorarium": "Honorários Individuais",
    "resume": "Resumo de Internação"
}

GUIDE_STATUS_LABELS = {
    "draft": "Em Digitação",
    "pending": "Pendente",
    "sent": "Enviada",
    "accepted": "Aceita",
    "rejected": "Rejeitada",
    "paid": "Paga",
    "gloss": "Glosada"
}

BATCH_STATUS_LABELS = {
    "open": "Aberto",
    "closed": "Fechado",
    "sent": "Enviado",
    "processed": "Processado"
}

PROCEDURE_TYPE_LABELS = {
    "consultation": "Consulta",
    "exam": "Exame",
    "therapy": "Terapia",
    "surgery": "Cirurgia",
    "hospitalization": "Internação",
    "other": "Outros"
}
