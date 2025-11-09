from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationSimple
)
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova organização (apenas admin)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar organizações")
    
    # Verificar se CNPJ já existe
    if org_data.cnpj:
        existing = db.query(Organization).filter(Organization.cnpj == org_data.cnpj).first()
        if existing:
            raise HTTPException(status_code=400, detail="CNPJ já cadastrado")
    
    new_org = Organization(**org_data.model_dump())
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return new_org

@router.get("/", response_model=List[OrganizationSimple])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar organizações"""
    
    query = db.query(Organization)
    
    if not include_inactive:
        query = query.filter(Organization.is_active == True)
    
    orgs = query.offset(skip).limit(limit).all()
    return orgs

@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de uma organização"""
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    # Se não for admin, só pode ver sua própria organização
    if current_user.role != 'admin' and org.id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Sem permissão para ver esta organização")
    
    return org

@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar organização"""
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    # Apenas admin pode editar
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar organizações")
    
    # Atualizar campos
    for field, value in org_data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    
    db.commit()
    db.refresh(org)
    
    return org

@router.delete("/{organization_id}")
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar organização (soft delete)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem desativar organizações")
    
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    # Soft delete
    org.is_active = False
    from datetime import datetime
    org.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Organização desativada com sucesso"}
