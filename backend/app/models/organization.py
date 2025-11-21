from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    
    # Relacionamentos
    users = relationship("User", back_populates="organization")
    patients = relationship("Patient", back_populates="organization")
    # Relacionamentos TISS
    tiss_operadoras = relationship("TISSOperadora", back_populates="organization")
    tiss_lotes = relationship("TISSLote", back_populates="organization")
    tiss_guias = relationship("TISSGuia", back_populates="organization")
    tiss_procedimentos = relationship("TISSProcedimento", back_populates="organization")
    tiss_tabelas_referencia = relationship("TISSTabelaReferencia", back_populates="organization")