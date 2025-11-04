from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse

router = APIRouter()


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os pacientes com paginação e busca opcional"""
    query = db.query(Patient).filter(Patient.is_active == True)
    
    # Busca por nome, email ou CPF
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.full_name.ilike(search_term),
                Patient.email.ilike(search_term),
                Patient.cpf.ilike(search_term)
            )
        )
    
    total = query.count()
    patients = query.offset(skip).limit(limit).all()
    
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Busca um paciente por ID"""
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    return patient


@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Cria um novo paciente"""
    
    # Verificar se CPF já existe
    if patient_data.cpf:
        existing = db.query(Patient).filter(
            Patient.cpf == patient_data.cpf,
            Patient.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Verificar se email já existe
    if patient_data.email:
        existing = db.query(Patient).filter(
            Patient.email == patient_data.email,
            Patient.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar paciente
    patient = Patient(**patient_data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um paciente"""
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Verificar CPF duplicado (se alterado)
    if patient_data.cpf and patient_data.cpf != patient.cpf:
        existing = db.query(Patient).filter(
            Patient.cpf == patient_data.cpf,
            Patient.is_active == True,
            Patient.id != patient_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    # Atualizar campos
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Deleta (soft delete) um paciente"""
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Soft delete
    patient.is_active = False
    db.commit()
    
    return {"message": "Paciente removido com sucesso"}


@router.get("/stats/summary")
def get_patients_summary(db: Session = Depends(get_db)):
    """Retorna estatísticas de pacientes"""
    total = db.query(func.count(Patient.id)).filter(Patient.is_active == True).scalar()
    
    return {
        "total_patients": total
    }
