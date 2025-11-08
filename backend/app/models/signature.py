from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

def generate_uuid_str():
    import uuid
    return str(uuid.uuid4())

class SignatureType(str, enum.Enum):
    """Tipos de assinatura"""
    ICP_BRASIL = "icp_brasil"  # Certificado digital ICP-Brasil
    OTP = "otp"  # One-Time Password via SMS
    SIMPLE = "simple"  # Assinatura eletrônica simples (senha)

class SignatureStatus(str, enum.Enum):
    """Status da assinatura"""
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"
    EXPIRED = "expired"

class Signature(Base):
    """Modelo de assinatura digital"""
    __tablename__ = "signatures"
    
    id = Column(String(50), primary_key=True, default=generate_uuid_str)
    
    # Documento
    document_type = Column(String(50), nullable=False)
    document_id = Column(String(50), nullable=False)
    document_hash = Column(String(64), nullable=False)
    
    # Signatário
    signer_id = Column(String(50), nullable=False)
    signer_name = Column(String(255), nullable=False)
    signer_cpf = Column(String(14), nullable=False)
    signer_crm = Column(String(20), nullable=True)
    
    # Assinatura
    signature_type = Column(Enum(SignatureType), nullable=False)
    status = Column(Enum(SignatureStatus), default=SignatureStatus.PENDING)
    signature_data = Column(Text, nullable=True)
    
    # Metadados
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Validação
    is_valid = Column(Boolean, default=False)
    validation_message = Column(Text, nullable=True)
    
    # Timestamps
    signed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
