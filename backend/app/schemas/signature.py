from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SignatureTypeEnum(str, Enum):
    ICP_BRASIL = "icp_brasil"
    OTP = "otp"
    SIMPLE = "simple"

class SignatureStatusEnum(str, Enum):
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class SignatureCreate(BaseModel):
    document_type: str
    document_id: str
    signer_cpf: str
    signer_crm: Optional[str] = None
    signature_type: SignatureTypeEnum

class SignatureResponse(BaseModel):
    id: str
    document_type: str
    document_id: str
    signer_name: str
    signer_cpf: str
    signature_type: SignatureTypeEnum
    status: SignatureStatusEnum
    is_valid: bool
    signed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
