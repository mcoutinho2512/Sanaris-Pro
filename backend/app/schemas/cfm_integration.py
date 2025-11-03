"""
Schemas para Integração CFM
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class CFMPrescriptionStatus(str, Enum):
    """Status da prescrição no CFM"""
    PENDING = "pending"
    SENT = "sent"
    CONFIRMED = "confirmed"
    ERROR = "error"


# ============================================
# CREDENCIAIS CFM
# ============================================

class CFMCredentialsBase(BaseModel):
    """Schema base de credenciais"""
    crm_number: str = Field(..., min_length=4, max_length=20)
    crm_state: str = Field(..., min_length=2, max_length=2)
    cfm_username: str = Field(..., min_length=3)
    auto_sync: bool = True
    sync_interval_minutes: int = Field(60, ge=15, le=1440)


class CFMCredentialsCreate(CFMCredentialsBase):
    """Schema para criação de credenciais"""
    healthcare_professional_id: str
    cfm_password: str = Field(..., min_length=6)  # Será criptografada


class CFMCredentialsUpdate(BaseModel):
    """Schema para atualização de credenciais"""
    cfm_username: Optional[str] = None
    cfm_password: Optional[str] = None
    auto_sync: Optional[bool] = None
    sync_interval_minutes: Optional[int] = Field(None, ge=15, le=1440)


class CFMCredentialsResponse(BaseModel):
    """Schema de resposta de credenciais"""
    id: str
    healthcare_professional_id: str
    crm_number: str
    crm_state: str
    cfm_username: str
    is_connected: bool
    last_sync_at: Optional[datetime] = None
    auto_sync: bool
    sync_interval_minutes: int
    total_prescriptions_sent: int
    last_prescription_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# AUTENTICAÇÃO CFM
# ============================================

class CFMLoginRequest(BaseModel):
    """Request de login no CFM"""
    healthcare_professional_id: str


class CFMLoginResponse(BaseModel):
    """Response de login"""
    success: bool
    message: str
    is_connected: bool
    expires_at: Optional[datetime] = None


class CFMLogoutRequest(BaseModel):
    """Request de logout"""
    healthcare_professional_id: str


# ============================================
# ENVIO DE PRESCRIÇÃO PARA CFM
# ============================================

class CFMPrescriptionSend(BaseModel):
    """Schema para enviar prescrição ao CFM"""
    prescription_id: str
    healthcare_professional_id: str


class CFMPrescriptionSendResponse(BaseModel):
    """Response de envio"""
    success: bool
    message: str
    cfm_prescription_id: Optional[str] = None
    cfm_validation_code: Optional[str] = None
    cfm_url: Optional[str] = None
    sent_at: Optional[datetime] = None


# ============================================
# LOG DE PRESCRIÇÕES CFM
# ============================================

class CFMPrescriptionLogResponse(BaseModel):
    """Schema de log de prescrição"""
    id: str
    prescription_id: str
    cfm_prescription_id: Optional[str] = None
    cfm_validation_code: Optional[str] = None
    cfm_url: Optional[str] = None
    status: CFMPrescriptionStatus
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SINCRONIZAÇÃO
# ============================================

class CFMSyncRequest(BaseModel):
    """Request de sincronização manual"""
    healthcare_professional_id: str
    sync_prescriptions: bool = True


class CFMSyncResponse(BaseModel):
    """Response de sincronização"""
    success: bool
    message: str
    synced_at: datetime
    prescriptions_synced: int


# ============================================
# STATUS
# ============================================

class CFMConnectionStatus(BaseModel):
    """Status de conexão com CFM"""
    healthcare_professional_id: str
    is_connected: bool
    crm_number: str
    crm_state: str
    last_sync_at: Optional[datetime] = None
    total_prescriptions_sent: int
    token_expires_at: Optional[datetime] = None
