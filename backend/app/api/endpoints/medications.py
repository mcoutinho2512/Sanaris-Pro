from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class MedicationSearchResponse(BaseModel):
    id: UUID
    commercial_name: str
    active_ingredient: str
    concentration: str | None
    pharmaceutical_form: str | None
    manufacturer: str | None
    
    class Config:
        from_attributes = True

@router.get("/search", response_model=List[MedicationSearchResponse])
def search_medications(
    q: str = Query(..., min_length=2, description="Termo de busca (mínimo 2 caracteres)"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca medicamentos por nome comercial ou princípio ativo
    - Mínimo 2 caracteres
    - Retorna até 10 resultados por padrão
    - Busca case-insensitive
    """
    from app.models.medication import Medication
    
    search_term = f"%{q.lower()}%"
    
    medications = db.query(Medication).filter(
        (Medication.commercial_name.ilike(search_term)) |
        (Medication.active_ingredient.ilike(search_term))
    ).limit(limit).all()
    
    return medications
