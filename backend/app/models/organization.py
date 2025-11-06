"""
Modelo de Organização/Clínica
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid


class Organization(Base):
    """Organização/Clínica que usa o sistema"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados básicos
    name = Column(String(255), nullable=False)
    trade_name = Column(String(255))  # Nome fantasia
    
    # Documentos
    cnpj = Column(String(18), unique=True, nullable=True)
    state_registration = Column(String(50))  # Inscrição estadual
    municipal_registration = Column(String(50))  # Inscrição municipal
    
    # Contato
    email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))
    website = Column(String(255))
    
    # Endereço
    address_street = Column(String(255))
    address_number = Column(String(20))
    address_complement = Column(String(100))
    address_neighborhood = Column(String(100))
    address_city = Column(String(100))
    address_state = Column(String(2))
    address_zipcode = Column(String(10))
    
    # Logo e Identidade Visual
    logo_url = Column(String(500))  # Caminho da logo principal
    logo_small_url = Column(String(500))  # Logo pequena (favicon)
    primary_color = Column(String(7))  # Cor primária (hex)
    secondary_color = Column(String(7))  # Cor secundária (hex)
    
    # Informações para documentos
    header_text = Column(Text)  # Texto personalizado para cabeçalho de documentos
    footer_text = Column(Text)  # Texto personalizado para rodapé de documentos
    
    # Configurações
    is_active = Column(Boolean, default=True)
    allow_multiple_users = Column(Boolean, default=True)
    max_users = Column(Integer, default=10)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Organization {self.name}>"
