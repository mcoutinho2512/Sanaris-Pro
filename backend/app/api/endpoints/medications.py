from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List
from app.core.database import get_db
from app.models.medication import Medication
from app.schemas.medication import (
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    MedicationSearchResult
)

router = APIRouter()


@router.get("/search", response_model=List[MedicationSearchResult])
async def search_medications(
    q: str = Query(..., min_length=2, description="Termo de busca"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    db: Session = Depends(get_db)
):
    """Buscar medicamentos (autocomplete)"""
    
    search_term = f"%{q.lower()}%"
    
    medications = db.query(Medication).filter(
        or_(
            func.lower(Medication.commercial_name).like(search_term),
            func.lower(Medication.active_ingredient).like(search_term)
        )
    ).limit(limit).all()
    
    return medications


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate,
    db: Session = Depends(get_db)
):
    """Criar novo medicamento"""
    
    if medication_data.anvisa_registry:
        existing = db.query(Medication).filter(
            Medication.anvisa_registry == medication_data.anvisa_registry
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Medicamento já cadastrado"
            )
    
    new_medication = Medication(**medication_data.dict())
    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)
    
    return new_medication


@router.get("/", response_model=List[MedicationResponse])
async def list_medications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listar medicamentos"""
    medications = db.query(Medication).offset(skip).limit(limit).all()
    return medications


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: str,
    db: Session = Depends(get_db)
):
    """Obter medicamento por ID"""
    medication = db.query(Medication).filter(
        Medication.id == medication_id
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento não encontrado"
        )
    
    return medication


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: str,
    medication_data: MedicationUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar medicamento"""
    medication = db.query(Medication).filter(
        Medication.id == medication_id
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento não encontrado"
        )
    
    for field, value in medication_data.dict(exclude_unset=True).items():
        setattr(medication, field, value)
    
    db.commit()
    db.refresh(medication)
    
    return medication


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: str,
    db: Session = Depends(get_db)
):
    """Deletar medicamento"""
    medication = db.query(Medication).filter(
        Medication.id == medication_id
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento não encontrado"
        )
    
    db.delete(medication)
    db.commit()
    
    return None
