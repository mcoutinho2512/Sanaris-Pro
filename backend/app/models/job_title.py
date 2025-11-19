from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class JobTitle(Base):
    __tablename__ = "job_titles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    department = Column(String(50), nullable=False)  # Médico, Administrativo, Enfermagem, etc
    is_healthcare_professional = Column(Boolean, default=False)  # Se pode atender pacientes
    can_schedule_appointments = Column(Boolean, default=True)  # Se pode agendar consultas
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<JobTitle {self.name}>"
