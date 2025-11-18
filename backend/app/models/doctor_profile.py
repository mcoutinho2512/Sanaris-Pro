from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    
    # Dados profissionais
    crm = Column(String(20), nullable=False)
    crm_state = Column(String(2), nullable=False)
    specialty = Column(String(200))
    
    # Identidade visual
    clinic_name = Column(String(200))
    logo_url = Column(String(500))
    primary_color = Column(String(7), default="#2563eb")
    secondary_color = Column(String(7), default="#1e40af")
    
    # Dados de contato
    phone = Column(String(20))
    email = Column(String(200))
    address = Column(Text)
    
    # Rodapé personalizado
    footer_text = Column(Text)
    
    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    organization = relationship("Organization")
