"""
Integração com prescricao.cfm.org.br
Sistema Oficial de Prescrição Eletrônica do CFM
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from datetime import datetime
from app.core.database import Base
import uuid


class CFMCredentials(Base):
    """Credenciais de acesso ao sistema CFM do médico"""
    __tablename__ = "cfm_credentials"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação do profissional
    healthcare_professional_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Dados CFM
    crm_number = Column(String(20), nullable=False)
    crm_state = Column(String(2), nullable=False)
    
    # Credenciais de acesso (criptografadas)
    cfm_username = Column(String(255))  # CPF ou login CFM
    cfm_password_encrypted = Column(Text)  # Senha criptografada
    
    # Tokens de sessão
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    
    # Status
    is_connected = Column(Boolean, default=False)
    last_sync_at = Column(DateTime)
    
    # Configurações
    auto_sync = Column(Boolean, default=True)  # Sincronizar automaticamente
    sync_interval_minutes = Column(Integer, default=60)  # Intervalo de sincronia
    
    # Estatísticas
    total_prescriptions_sent = Column(Integer, default=0)
    last_prescription_sent_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CFMCredentials CRM {self.crm_number}/{self.crm_state}>"


class CFMPrescriptionLog(Base):
    """Log de prescrições enviadas ao CFM"""
    __tablename__ = "cfm_prescription_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Referências
    prescription_id = Column(String(36), nullable=False, index=True)
    cfm_credentials_id = Column(String(36), nullable=False, index=True)
    
    # Dados do CFM
    cfm_prescription_id = Column(String(100))  # ID no sistema CFM
    cfm_validation_code = Column(String(100))  # Código de validação
    cfm_url = Column(String(500))  # URL da prescrição no CFM
    
    # Status
    status = Column(String(50), default="pending")  # pending, sent, confirmed, error
    error_message = Column(Text)
    
    # Request/Response
    request_payload = Column(Text)  # JSON do request
    response_payload = Column(Text)  # JSON da response
    
    # Timestamps
    sent_at = Column(DateTime)
    confirmed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CFMPrescriptionLog {self.cfm_validation_code}>"
