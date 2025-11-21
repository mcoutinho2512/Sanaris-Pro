from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiss import TISSOperadora
from app.schemas.tiss import (
    TISSOperadoraCreate,
    TISSOperadoraUpdate,
    TISSOperadoraResponse
)

router = APIRouter(prefix="/tiss/operadoras", tags=["TISS - Operadoras"])


@router.post("/", response_model=TISSOperadoraResponse, status_code=status.HTTP_201_CREATED)
def criar_operadora(
    operadora: TISSOperadoraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova operadora de plano de saúde"""
    
    # Verificar se já existe operadora com esse registro ANS
    existing = db.query(TISSOperadora).filter(
        TISSOperadora.registro_ans == operadora.registro_ans,
        TISSOperadora.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma operadora cadastrada com o registro ANS {operadora.registro_ans}"
        )
    
    # Criar operadora
    db_operadora = TISSOperadora(
        organization_id=current_user.organization_id,
        **operadora.model_dump()
    )
    
    db.add(db_operadora)
    db.commit()
    db.refresh(db_operadora)
    
    return db_operadora


@router.get("/", response_model=List[TISSOperadoraResponse])
def listar_operadoras(
    skip: int = 0,
    limit: int = 100,
    ativo: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar operadoras da organização"""
    
    query = db.query(TISSOperadora).filter(
        TISSOperadora.organization_id == current_user.organization_id,
        TISSOperadora.deleted_at.is_(None)
    )
    
    if ativo is not None:
        query = query.filter(TISSOperadora.ativo == ativo)
    
    operadoras = query.offset(skip).limit(limit).all()
    return operadoras


@router.get("/{operadora_id}", response_model=TISSOperadoraResponse)
def obter_operadora(
    operadora_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de uma operadora"""
    
    operadora = db.query(TISSOperadora).filter(
        TISSOperadora.id == operadora_id,
        TISSOperadora.organization_id == current_user.organization_id,
        TISSOperadora.deleted_at.is_(None)
    ).first()
    
    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    return operadora


@router.put("/{operadora_id}", response_model=TISSOperadoraResponse)
def atualizar_operadora(
    operadora_id: UUID,
    operadora_update: TISSOperadoraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar dados de uma operadora"""
    
    operadora = db.query(TISSOperadora).filter(
        TISSOperadora.id == operadora_id,
        TISSOperadora.organization_id == current_user.organization_id,
        TISSOperadora.deleted_at.is_(None)
    ).first()
    
    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    # Atualizar campos
    update_data = operadora_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(operadora, field, value)
    
    operadora.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(operadora)
    
    return operadora


@router.delete("/{operadora_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_operadora(
    operadora_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar operadora (soft delete)"""
    
    operadora = db.query(TISSOperadora).filter(
        TISSOperadora.id == operadora_id,
        TISSOperadora.organization_id == current_user.organization_id,
        TISSOperadora.deleted_at.is_(None)
    ).first()
    
    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    # Soft delete
    operadora.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
