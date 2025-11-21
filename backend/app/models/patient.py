from sqlalchemy import Column, String, Boolean, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Dados pessoais
    full_name = Column(String, nullable=False, index=True)
    cpf = Column(String(14), unique=True, nullable=True, index=True)
    rg = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    
    # Contato
    phone = Column(String(20), nullable=True)
    email = Column(String, nullable=True)
    
    # Endereço
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    # Informações médicas
    blood_type = Column(String(5), nullable=True)
    allergies = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="patients")
    # Relacionamentos TISS
    tiss_guias = relationship("TISSGuia", back_populates="patient")