from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False)
    professional_id = Column(String(36), nullable=False)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    status = Column(String(20), default="scheduled")
    appointment_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="appointments")
