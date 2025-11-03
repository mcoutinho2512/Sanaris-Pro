from sqlalchemy import Column, String, Date, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, index=True)
    birth_date = Column(Date)
    phone = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    appointments = relationship("Appointment", back_populates="patient")

    medical_records = relationship("MedicalRecord", back_populates="patient")

    prescriptions = relationship("Prescription", back_populates="patient")

    documents = relationship("PatientDocument", back_populates="patient")
