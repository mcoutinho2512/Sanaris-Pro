"""
Schemas para Assinatura Digital Avançada
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class SignatureTypeEnum(str, Enum):
    """Tipos de assinatura"""
    BASIC_CRM = "basic_crm"
    ICP_BRASIL = "icp_brasil"
    OTP = "otp"


class OTPMethodEnum(str, Enum):
    """Método de envio OTP"""
    SMS = "sms"
    EMAIL = "email"
    APP = "app"


# ============================================
# CERTIFICADO DIGITAL ICP-BRASIL
# ============================================

class DigitalCertificateBase(BaseModel):
    """Schema base de certificado"""
    healthcare_professional_id: str
    certificate_type: str = Field(..., max_length=50)
    holder_name: str = Field(..., min_length=1, max_length=255)
    holder_cpf: str = Field(..., min_length=11, max_length=14)
    holder_crm: Optional[str] = None
    holder_email: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    issuer_name: Optional[str] = None
    serial_number: Optional[str] = None


class DigitalCertificateCreate(DigitalCertificateBase):
    """Schema para upload de certificado"""
    certificate_data: str  # Base64
    certificate_password: str  # Será criptografada


class DigitalCertificateUpdate(BaseModel):
    """Schema para atualização"""
    certificate_password: Optional[str] = None
    is_active: Optional[bool] = None


class DigitalCertificateResponse(BaseModel):
    """Schema de resposta"""
    id: str
    healthcare_professional_id: str
    certificate_type: str
    holder_name: str
    holder_cpf: str
    holder_crm: Optional[str] = None
    holder_email: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    is_expired: bool
    issuer_name: Optional[str] = None
    serial_number: Optional[str] = None
    total_signatures: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# CONFIGURAÇÃO OTP
# ============================================

class OTPConfigurationBase(BaseModel):
    """Schema base de OTP"""
    healthcare_professional_id: str
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    otp_method: OTPMethodEnum = OTPMethodEnum.SMS
    otp_length: int = Field(6, ge=4, le=8)
    otp_validity_minutes: int = Field(5, ge=1, le=30)


class OTPConfigurationCreate(OTPConfigurationBase):
    """Schema para criação"""
    pass


class OTPConfigurationUpdate(BaseModel):
    """Schema para atualização"""
    phone_number: Optional[str] = None
    email: Optional[str] = None
    otp_method: Optional[OTPMethodEnum] = None
    otp_length: Optional[int] = Field(None, ge=4, le=8)
    otp_validity_minutes: Optional[int] = Field(None, ge=1, le=30)
    is_active: Optional[bool] = None


class OTPConfigurationResponse(BaseModel):
    """Schema de resposta"""
    id: str
    healthcare_professional_id: str
    phone_number: str
    email: str
    otp_method: str
    otp_length: int
    otp_validity_minutes: int
    is_active: bool
    is_verified: bool
    total_otps_sent: int
    total_signatures: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# ASSINATURA DE DOCUMENTOS
# ============================================

class SignDocumentRequest(BaseModel):
    """Request para assinar documento"""
    document_type: str = Field(..., max_length=50)
    document_id: str
    healthcare_professional_id: str
    signature_type: SignatureTypeEnum


class SignWithICPBrasil(SignDocumentRequest):
    """Assinatura com ICP-Brasil"""
    certificate_id: str
    certificate_password: str


class SignWithOTP(SignDocumentRequest):
    """Assinatura com OTP"""
    otp_code: str = Field(..., min_length=4, max_length=8)


class SignWithBasicCRM(SignDocumentRequest):
    """Assinatura básica com CRM"""
    crm_number: str
    crm_state: str
    signature_data: str  # Assinatura desenhada em base64


class GenerateOTPRequest(BaseModel):
    """Request para gerar OTP"""
    healthcare_professional_id: str
    document_type: str
    document_id: str


class GenerateOTPResponse(BaseModel):
    """Response de geração OTP"""
    success: bool
    message: str
    otp_sent_to: str
    otp_method: str
    expires_at: datetime


class SignatureResponse(BaseModel):
    """Response de assinatura"""
    success: bool
    message: str
    signature_id: str
    signature_type: str
    signed_at: datetime
    signature_hash: Optional[str] = None


# ============================================
# LOG DE ASSINATURAS
# ============================================

class SignatureLogResponse(BaseModel):
    """Schema de log"""
    id: str
    document_type: str
    document_id: str
    healthcare_professional_id: str
    signature_type: str
    signature_hash: Optional[str] = None
    certificate_serial: Optional[str] = None
    status: str
    ip_address: Optional[str] = None
    signed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# VALIDAÇÃO
# ============================================

class ValidateSignatureRequest(BaseModel):
    """Request para validar assinatura"""
    signature_hash: str


class ValidateSignatureResponse(BaseModel):
    """Response de validação"""
    valid: bool
    signature_type: str
    signed_at: datetime
    professional_name: str
    crm_number: Optional[str] = None
    certificate_issuer: Optional[str] = None
