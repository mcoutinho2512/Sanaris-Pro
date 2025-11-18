from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    email = Column(String, unique=True, index=True, nullable=False)
    recovery_email = Column(String, unique=True, index=True, nullable=False)  # Email para recuperação de senha
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    
    # OAuth
    google_id = Column(String, unique=True, nullable=True, index=True)
    picture = Column(String, nullable=True)
    
    # Status e verificação
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Role: super_admin, admin, user
    role = Column(String(20), default='user')
    
    # Permissões granulares (apenas para role='user')
    # Lista de módulos permitidos em formato JSON
    # Ex: ["dashboard","pacientes","agenda","prontuarios"]
    allowed_modules = Column(Text, default='["dashboard","pacientes","agenda","prontuarios","prescricoes","cfm","relatorios","chat"]')
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    last_login = Column(String, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="users")
    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
