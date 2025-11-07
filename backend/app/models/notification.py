"""
Modelo de Notificações
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
import enum


class NotificationType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class Notification(Base):
    """Histórico de notificações enviadas"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tipo e status
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Destinatário
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255))
    recipient_phone = Column(String(20))
    
    # Conteúdo
    subject = Column(String(500))
    message = Column(Text, nullable=False)
    template_used = Column(String(100))
    
    # Relacionamentos - SEM foreign key por enquanto
    appointment_id = Column(String(50), nullable=True)
    patient_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Resultado
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    error_message = Column(Text)
    provider_response = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Notification {self.notification_type} to {self.recipient_name}>"
