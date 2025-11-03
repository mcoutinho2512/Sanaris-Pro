"""
Sistema de Assinatura Digital Avançada
ICP-Brasil e OTP
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum as SQLEnum
from datetime import datetime
from app.core.database import Base
import uuid
import enum


class SignatureType(enum.Enum):
    """Tipos de assinatura"""
    BASIC_CRM = "basic_crm"  # Assinatura simples com CRM
    ICP_BRASIL = "icp_brasil"  # Certificado digital ICP-Brasil
    OTP = "otp"  # One-Time Password


class SignatureStatus(enum.Enum):
    """Status da assinatura"""
    PENDING = "pending"
    SIGNED = "signed"
    FAILED = "failed"
    EXPIRED = "expired"


class DigitalCertificate(Base):
    """Certificado Digital ICP-Brasil do profissional"""
    __tablename__ = "digital_certificates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Profissional
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Dados do certificado
    certificate_type = Column(String(50), nullable=False)  # A1, A3, etc
    certificate_data = Column(Text)  # Certificado em base64
    certificate_password_encrypted = Column(Text)  # Senha criptografada
    
    # Dados do titular
    holder_name = Column(String(255), nullable=False)
    holder_cpf = Column(String(14), nullable=False)
    holder_crm = Column(String(20))
    holder_email = Column(String(255))
    
    # Validade
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_expired = Column(Boolean, default=False)
    
    # Emissor
    issuer_name = Column(String(255))  # Autoridade Certificadora
    serial_number = Column(String(100))
    
    # Uso
    total_signatures = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DigitalCertificate {self.holder_name}>"


class OTPConfiguration(Base):
    """Configuração de OTP do profissional"""
    __tablename__ = "otp_configurations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Profissional
    healthcare_professional_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Configurações OTP
    secret_key_encrypted = Column(Text, nullable=False)  # Chave secreta criptografada
    phone_number = Column(String(20), nullable=False)  # Telefone para envio
    email = Column(String(255), nullable=False)  # Email backup
    
    # Preferências
    otp_method = Column(String(20), default="sms")  # sms, email, app
    otp_length = Column(Integer, default=6)
    otp_validity_minutes = Column(Integer, default=5)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Estatísticas
    total_otps_sent = Column(Integer, default=0)
    total_signatures = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<OTPConfiguration {self.healthcare_professional_id}>"


class SignatureLog(Base):
    """Log de assinaturas digitais"""
    __tablename__ = "signature_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Referências
    document_type = Column(String(50), nullable=False)  # prescription, medical_record, etc
    document_id = Column(String(36), nullable=False, index=True)
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Tipo de assinatura
    signature_type = Column(SQLEnum(SignatureType), nullable=False)
    
    # Dados da assinatura
    signature_data = Column(Text)  # Hash, certificado, etc
    signature_hash = Column(String(255))  # Hash SHA-256
    
    # Certificado (se ICP-Brasil)
    certificate_id = Column(String(36))
    certificate_serial = Column(String(100))
    
    # OTP (se OTP)
    otp_code = Column(String(10))  # Não armazenar em produção
    otp_sent_to = Column(String(255))
    otp_verified_at = Column(DateTime)
    
    # Status
    status = Column(SQLEnum(SignatureStatus), default=SignatureStatus.PENDING)
    
    # Metadados
    ip_address = Column(String(50))
    user_agent = Column(Text)
    geolocation = Column(String(255))
    
    # Timestamps
    signed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SignatureLog {self.document_type} - {self.signature_type.value}>"
