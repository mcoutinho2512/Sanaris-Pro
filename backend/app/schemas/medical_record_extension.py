"""
Schemas para extensões do Prontuário
Templates por Especialidade, Exames e Evolução Fotográfica
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# TEMPLATES DE PRONTUÁRIO
# ============================================

class MedicalRecordTemplateBase(BaseModel):
    """Schema base de template"""
    name: str = Field(..., min_length=1, max_length=255)
    specialty: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    anamnesis_fields: Optional[str] = None
    physical_exam_fields: Optional[str] = None
    specialty_fields: Optional[str] = None
    field_order: Optional[str] = None
    required_fields: Optional[str] = None
    hidden_fields: Optional[str] = None
    default_values: Optional[str] = None


class MedicalRecordTemplateCreate(MedicalRecordTemplateBase):
    """Schema para criação de template"""
    pass


class MedicalRecordTemplateUpdate(BaseModel):
    """Schema para atualização de template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    specialty: Optional[str] = None
    description: Optional[str] = None
    anamnesis_fields: Optional[str] = None
    physical_exam_fields: Optional[str] = None
    specialty_fields: Optional[str] = None
    field_order: Optional[str] = None
    required_fields: Optional[str] = None
    hidden_fields: Optional[str] = None
    default_values: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class MedicalRecordTemplateResponse(MedicalRecordTemplateBase):
    """Schema de resposta de template"""
    id: str
    is_active: bool
    is_default: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# RESULTADOS DE EXAMES
# ============================================

class ExamResultBase(BaseModel):
    """Schema base de resultado de exame"""
    patient_id: str
    medical_record_id: Optional[str] = None
    exam_type: str = Field(..., min_length=1, max_length=100)
    exam_name: str = Field(..., min_length=1, max_length=255)
    exam_date: datetime
    results: str  # JSON string
    reference_values: Optional[str] = None  # JSON string
    is_normal: Optional[bool] = None
    has_alert: bool = False
    alert_message: Optional[str] = None
    observations: Optional[str] = None


class ExamResultCreate(ExamResultBase):
    """Schema para criação de resultado"""
    pass


class ExamResultUpdate(BaseModel):
    """Schema para atualização de resultado"""
    exam_type: Optional[str] = None
    exam_name: Optional[str] = None
    exam_date: Optional[datetime] = None
    results: Optional[str] = None
    reference_values: Optional[str] = None
    is_normal: Optional[bool] = None
    has_alert: Optional[bool] = None
    alert_message: Optional[str] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    observations: Optional[str] = None


class ExamResultResponse(ExamResultBase):
    """Schema de resposta de resultado"""
    id: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExamResultListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    exam_type: str
    exam_name: str
    exam_date: datetime
    is_normal: Optional[bool] = None
    has_alert: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# EVOLUÇÃO FOTOGRÁFICA
# ============================================

class PhotoEvolutionBase(BaseModel):
    """Schema base de evolução fotográfica"""
    patient_id: str
    medical_record_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    photo_date: datetime
    body_part: Optional[str] = Field(None, max_length=100)
    angle: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    treatment_phase: Optional[str] = Field(None, max_length=100)
    session_number: Optional[int] = None
    observations: Optional[str] = None


class PhotoEvolutionCreate(PhotoEvolutionBase):
    """Schema para criação de foto"""
    file_path: str = Field(..., min_length=1, max_length=500)


class PhotoEvolutionUpdate(BaseModel):
    """Schema para atualização de foto"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    photo_date: Optional[datetime] = None
    body_part: Optional[str] = None
    angle: Optional[str] = None
    category: Optional[str] = None
    treatment_phase: Optional[str] = None
    session_number: Optional[int] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    observations: Optional[str] = None


class PhotoEvolutionResponse(PhotoEvolutionBase):
    """Schema de resposta de foto"""
    id: str
    file_path: str
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PhotoEvolutionListResponse(BaseModel):
    """Schema simplificado para listagem"""
    id: str
    patient_id: str
    title: str
    photo_date: datetime
    body_part: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE GRÁFICOS
# ============================================

class ExamChartData(BaseModel):
    """Dados para gráfico de exames"""
    exam_type: str
    dates: List[str]
    values: List[float]
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    unit: Optional[str] = None


class ExamChartRequest(BaseModel):
    """Request para gerar gráfico"""
    patient_id: str
    exam_type: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class PhotoComparisonRequest(BaseModel):
    """Request para comparar fotos"""
    patient_id: str
    body_part: Optional[str] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
