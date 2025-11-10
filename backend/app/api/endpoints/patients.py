from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.database import get_db
from app.models.patient import Patient
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()

class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    cpf: Optional[str] = None
    rg: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    observations: Optional[str] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    observations: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(BaseModel):
    id: UUID
    organization_id: Optional[UUID] = None
    organization_name: Optional[str] = None
    full_name: str
    cpf: Optional[str] = None
    rg: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    observations: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar pacientes:
    - Super admin vê todos (pode filtrar por organização)
    - Admin/User vê apenas da própria organização
    """
    
    query = db.query(Patient)
    
    # Super admin vê todos
    if current_user.role == 'super_admin':
        if organization_id:
            query = query.filter(Patient.organization_id == organization_id)
    # Admin e User veem só da própria organização
    else:
        if not current_user.organization_id:
            raise HTTPException(status_code=403, detail="Usuário sem organização")
        query = query.filter(Patient.organization_id == current_user.organization_id)
    
    # Filtros
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Patient.full_name.ilike(search_filter)) |
            (Patient.cpf.ilike(search_filter)) |
            (Patient.phone.ilike(search_filter))
        )
    
    patients = query.order_by(Patient.full_name).offset(skip).limit(limit).all()
    
    # Adicionar nome da organização
    result = []
    for patient in patients:
        org = db.query(Organization).filter(Organization.id == patient.organization_id).first()
        result.append(PatientResponse(
            id=patient.id,
            organization_id=patient.organization_id,
            organization_name=org.name if org else None,
            full_name=patient.full_name,
            cpf=patient.cpf,
            rg=patient.rg,
            birth_date=patient.birth_date.isoformat() if patient.birth_date else None,
            gender=patient.gender,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            city=patient.city,
            state=patient.state,
            zip_code=patient.zip_code,
            blood_type=patient.blood_type,
            allergies=patient.allergies,
            observations=patient.observations,
            is_active=patient.is_active,
            created_at=patient.created_at.isoformat() if isinstance(patient.created_at, datetime) else patient.created_at
        ))
    
    return result

@router.post("/", response_model=PatientResponse)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo paciente na organização do usuário"""
    
    if not current_user.organization_id:
        raise HTTPException(status_code=403, detail="Usuário sem organização")
    
    # Verificar CPF duplicado
    if patient_data.cpf:
        existing = db.query(Patient).filter(Patient.cpf == patient_data.cpf).first()
        if existing:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Criar paciente
    new_patient = Patient(
        organization_id=current_user.organization_id,
        **patient_data.dict()
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    org = db.query(Organization).filter(Organization.id == new_patient.organization_id).first()
    
    return PatientResponse(
        id=new_patient.id,
        organization_id=new_patient.organization_id,
        organization_name=org.name if org else None,
        full_name=new_patient.full_name,
        cpf=new_patient.cpf,
        rg=new_patient.rg,
        birth_date=new_patient.birth_date,
        gender=new_patient.gender,
        phone=new_patient.phone,
        email=new_patient.email,
        address=new_patient.address,
        city=new_patient.city,
        state=new_patient.state,
        zip_code=new_patient.zip_code,
        blood_type=new_patient.blood_type,
        allergies=new_patient.allergies,
        observations=new_patient.observations,
        is_active=new_patient.is_active,
        created_at=new_patient.created_at
    )

@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estatísticas de pacientes por organização"""
    
    from sqlalchemy import func, case
    
    # Super admin vê todas
    if current_user.role == 'super_admin':
        stats = db.query(
            Organization.id,
            Organization.name,
            func.count(Patient.id).label('total_patients'),
            func.sum(case((Patient.is_active == True, 1), else_=0)).label('active_patients')
        ).outerjoin(
            Patient, Patient.organization_id == Organization.id
        ).group_by(Organization.id, Organization.name).all()
    else:
        # Admin/User vê só sua org
        if not current_user.organization_id:
            raise HTTPException(status_code=403, detail="Usuário sem organização")
        
        stats = db.query(
            Organization.id,
            Organization.name,
            func.count(Patient.id).label('total_patients'),
            func.sum(case((Patient.is_active == True, 1), else_=0)).label('active_patients')
        ).outerjoin(
            Patient, Patient.organization_id == Organization.id
        ).filter(
            Organization.id == current_user.organization_id
        ).group_by(Organization.id, Organization.name).all()
    
    result = []
    for org_id, org_name, total, active in stats:
        result.append({
            "organization_id": str(org_id),
            "organization_name": org_name,
            "total_patients": total or 0,
            "active_patients": active or 0,
            "inactive_patients": (total or 0) - (active or 0)
        })
    
    return result
