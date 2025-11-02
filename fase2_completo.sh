#!/bin/bash

##############################################
# SANARIS PRO - FASE 2 COMPLETA
# Instalação Automática dos Módulos Essenciais
##############################################

BACKEND="/home/administrador/sanaris-pro/sanaris/backend"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     SANARIS PRO - FASE 2: MÓDULOS ESSENCIAIS              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Agenda Inteligente"
echo "📋 Prontuário Eletrônico"  
echo "💊 Prescrição Digital"
echo ""
echo "Pressione ENTER para continuar..."
read

cd "$BACKEND"

# Criar diretórios
mkdir -p app/{models,schemas,services,api/endpoints,core}

echo "1/5 - Criando dependências do banco..."

# Core - Database
cat > app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sanaris_admin@localhost:5432/sanaris_pro")

# Converter asyncpg para psycopg2 para funcionar com Alembic
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

echo "2/5 - Criando Models..."

# Models - Patients
cat > app/models/patient.py << 'EOF'
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
EOF

# Models - Appointments
cat > app/models/appointment.py << 'EOF'
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
EOF

# Models __init__
cat > app/models/__init__.py << 'EOF'
from app.core.database import Base
from app.models.patient import Patient
from app.models.appointment import Appointment
EOF

echo "3/5 - Criando Schemas..."

# Schemas - Patient
cat > app/schemas/patient.py << 'EOF'
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class PatientBase(BaseModel):
    full_name: str
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class PatientCreate(PatientBase):
    tenant_id: str

class PatientResponse(PatientBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
EOF

# Schemas - Appointment
cat > app/schemas/appointment.py << 'EOF'
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    patient_id: str
    professional_id: str
    appointment_date: datetime
    duration_minutes: int = 30
    appointment_type: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    tenant_id: str

class AppointmentResponse(AppointmentBase):
    id: str
    tenant_id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
EOF

echo "4/5 - Criando Endpoints..."

# Endpoints - Patients
cat > app/api/endpoints/patients.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
EOF

# Endpoints - Appointments
cat > app/api/endpoints/appointments.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment
EOF

echo "5/5 - Atualizando main.py..."

# Atualizar main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import patients, appointments

app = FastAPI(
    title="Sanaris Pro API",
    description="Sistema de Gestão de Clínicas e Consultórios",
    version="1.0.0 - Fase 2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patients.router)
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {
        "message": "🏥 Sanaris Pro API - Fase 2",
        "version": "1.0.0",
        "status": "online",
        "modules": {
            "patients": "✅ Active",
            "appointments": "✅ Active",
            "medical_records": "⏳ Coming soon",
            "prescriptions": "⏳ Coming soon"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "phase": "2"}
EOF

echo ""
echo "✅ Código criado com sucesso!"
echo ""
echo "Próximo passo: Criar tabelas no banco de dados"
echo ""
echo "Execute:"
echo "  cd $BACKEND"
echo "  python3 create_tables.py"
echo ""
