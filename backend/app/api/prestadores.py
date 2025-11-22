from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.prestador import Prestador
from app.schemas.prestador import PrestadorCreate, PrestadorUpdate, PrestadorResponse
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=PrestadorResponse, status_code=201)
def criar_prestador(
    prestador: PrestadorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo prestador"""
    db_prestador = Prestador(
        **prestador.dict(),
        organization_id=current_user.organization_id
    )
    db.add(db_prestador)
    db.commit()
    db.refresh(db_prestador)
    return db_prestador

@router.get("/", response_model=List[PrestadorResponse])
def listar_prestadores(
    tipo_prestador: str = None,
    ativo: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar prestadores"""
    query = db.query(Prestador).filter(
        Prestador.organization_id == current_user.organization_id,
        Prestador.deleted_at.is_(None)
    )
    
    if tipo_prestador:
        query = query.filter(Prestador.tipo_prestador == tipo_prestador)
    
    if ativo is not None:
        query = query.filter(Prestador.ativo == ativo)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{prestador_id}", response_model=PrestadorResponse)
def obter_prestador(
    prestador_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter prestador por ID"""
    prestador = db.query(Prestador).filter(
        Prestador.id == prestador_id,
        Prestador.organization_id == current_user.organization_id,
        Prestador.deleted_at.is_(None)
    ).first()
    
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    
    return prestador

@router.put("/{prestador_id}", response_model=PrestadorResponse)
def atualizar_prestador(
    prestador_id: UUID,
    prestador_update: PrestadorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar prestador"""
    prestador = db.query(Prestador).filter(
        Prestador.id == prestador_id,
        Prestador.organization_id == current_user.organization_id,
        Prestador.deleted_at.is_(None)
    ).first()
    
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    
    for key, value in prestador_update.dict(exclude_unset=True).items():
        setattr(prestador, key, value)
    
    db.commit()
    db.refresh(prestador)
    return prestador

@router.delete("/{prestador_id}", status_code=204)
def deletar_prestador(
    prestador_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar prestador (soft delete)"""
    prestador = db.query(Prestador).filter(
        Prestador.id == prestador_id,
        Prestador.organization_id == current_user.organization_id,
        Prestador.deleted_at.is_(None)
    ).first()
    
    if not prestador:
        raise HTTPException(status_code=404, detail="Prestador não encontrado")
    
    from datetime import datetime
    prestador.deleted_at = datetime.utcnow()
    db.commit()
    return None
