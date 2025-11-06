"""
Modelo de Medicamentos (Base ANVISA)
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime
import uuid


class Medication(Base):
    """Medicamento registrado na ANVISA"""
    __tablename__ = "medications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identificação
    anvisa_registry = Column(String(50), unique=True, nullable=True)
    
    # Nome e composição
    commercial_name = Column(String(500), nullable=False, index=True)
    active_ingredient = Column(String(500), nullable=False, index=True)
    
    # Apresentação
    presentation = Column(String(500))
    concentration = Column(String(100))
    pharmaceutical_form = Column(String(100))
    
    # Fabricante
    manufacturer = Column(String(300), index=True)
    
    # Classificação
    therapeutic_class = Column(String(200))
    requires_prescription = Column(Integer, default=1)
    
    # Informações adicionais
    ean_code = Column(String(20))
    pmc = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Medication {self.commercial_name}>"
