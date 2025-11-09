from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organização
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=True)
    
    # Dados básicos
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Autenticação tradicional
    hashed_password = Column(String(255), nullable=True)  # Null se login via Google
    
    # Google OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    picture = Column(String(500), nullable=True)  # URL da foto do Google
    
    # Status
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    crm = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Soft delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", backref="users")
    
    def __repr__(self):
        return f"<User {self.email}>"
