from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)

router = APIRouter()

@router.get("/")
def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar organizações (apenas super admin)"""
    if current_user.role != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    orgs = db.query(Organization).all()
    
    # Converter manualmente para dict
    return [
        {
            "id": str(org.id),
            "name": org.name,
            "email": org.email,
            "phone": org.phone,
            "is_active": org.is_active,
            "created_at": org.created_at
        }
        for org in orgs
    ]

@router.post("/", status_code=201)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar organização (apenas super admin)"""
    if current_user.role != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    org = Organization(**org_data.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    
    return {
        "id": str(org.id),
        "name": org.name,
        "email": org.email,
        "phone": org.phone,
        "is_active": org.is_active,
        "created_at": org.created_at
    }

@router.put("/{org_id}")
def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar organização"""
    if current_user.role != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    for key, value in org_data.dict(exclude_unset=True).items():
        setattr(org, key, value)
    
    db.commit()
    db.refresh(org)
    
    return {
        "id": str(org.id),
        "name": org.name,
        "email": org.email,
        "phone": org.phone,
        "is_active": org.is_active,
        "created_at": org.created_at
    }

@router.delete("/{org_id}")
def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar organização"""
    if current_user.role != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    db.delete(org)
    db.commit()
    
    return {"message": "Organização deletada"}
