from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiss import TISSLote, TISSOperadora, TISSGuia
from app.schemas.tiss import (
    TISSLoteCreate,
    TISSLoteUpdate,
    TISSLoteResponse,
    TISSLoteListResponse
)

router = APIRouter(prefix="/tiss/lotes", tags=["TISS - Lotes"])


def gerar_numero_lote(db: Session, organization_id: UUID, competencia: str) -> str:
    """Gerar número sequencial do lote"""
    # Formato: LOTE-AAAAMM-XXX (Ex: LOTE-202411-001)
    ano_mes = competencia.replace("/", "")
    
    # Contar lotes existentes na competência
    count = db.query(TISSLote).filter(
        TISSLote.organization_id == organization_id,
        TISSLote.competencia == competencia,
        TISSLote.deleted_at.is_(None)
    ).count()
    
    sequencial = str(count + 1).zfill(3)
    return f"LOTE-{ano_mes}-{sequencial}"


@router.post("/", response_model=TISSLoteResponse, status_code=status.HTTP_201_CREATED)
def criar_lote(
    lote: TISSLoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo lote de faturamento"""
    
    # Verificar se operadora existe
    operadora = db.query(TISSOperadora).filter(
        TISSOperadora.id == lote.operadora_id,
        TISSOperadora.organization_id == current_user.organization_id,
        TISSOperadora.deleted_at.is_(None)
    ).first()
    
    if not operadora:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    # Gerar número do lote
    numero_lote = gerar_numero_lote(db, current_user.organization_id, lote.competencia)
    
    # Criar lote
    db_lote = TISSLote(
        organization_id=current_user.organization_id,
        numero_lote=numero_lote,
        **lote.model_dump()
    )
    
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    
    return db_lote


@router.get("/", response_model=List[TISSLoteListResponse])
def listar_lotes(
    skip: int = 0,
    limit: int = 100,
    operadora_id: UUID = None,
    status: str = None,
    competencia: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar lotes de faturamento"""
    
    query = db.query(TISSLote).filter(
        TISSLote.organization_id == current_user.organization_id,
        TISSLote.deleted_at.is_(None)
    )
    
    if operadora_id:
        query = query.filter(TISSLote.operadora_id == operadora_id)
    
    if status:
        query = query.filter(TISSLote.status == status)
    
    if competencia:
        query = query.filter(TISSLote.competencia == competencia)
    
    lotes = query.order_by(TISSLote.created_at.desc()).offset(skip).limit(limit).all()
    return lotes


@router.get("/{lote_id}", response_model=TISSLoteResponse)
def obter_lote(
    lote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de um lote"""
    
    lote = db.query(TISSLote).filter(
        TISSLote.id == lote_id,
        TISSLote.organization_id == current_user.organization_id,
        TISSLote.deleted_at.is_(None)
    ).first()
    
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    return lote


@router.put("/{lote_id}", response_model=TISSLoteResponse)
def atualizar_lote(
    lote_id: UUID,
    lote_update: TISSLoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar dados de um lote"""
    
    lote = db.query(TISSLote).filter(
        TISSLote.id == lote_id,
        TISSLote.organization_id == current_user.organization_id,
        TISSLote.deleted_at.is_(None)
    ).first()
    
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    # Atualizar campos
    update_data = lote_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lote, field, value)
    
    lote.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lote)
    
    return lote


@router.post("/{lote_id}/fechar", response_model=TISSLoteResponse)
def fechar_lote(
    lote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fechar lote e calcular totais"""
    
    lote = db.query(TISSLote).filter(
        TISSLote.id == lote_id,
        TISSLote.organization_id == current_user.organization_id,
        TISSLote.deleted_at.is_(None)
    ).first()
    
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    if lote.status != "rascunho":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas lotes em rascunho podem ser fechados"
        )
    
    # Buscar guias do lote
    guias = db.query(TISSGuia).filter(
        TISSGuia.lote_id == lote_id,
        TISSGuia.deleted_at.is_(None)
    ).all()
    
    if not guias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lote não possui guias vinculadas"
        )
    
    # Calcular totais
    valor_total = sum(guia.valor_total_informado for guia in guias)
    quantidade_guias = len(guias)
    
    # Atualizar lote
    lote.status = "enviado"
    lote.valor_total_informado = valor_total
    lote.quantidade_guias = quantidade_guias
    lote.data_envio = datetime.utcnow()
    lote.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(lote)
    
    return lote


@router.delete("/{lote_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_lote(
    lote_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar lote (soft delete)"""
    
    lote = db.query(TISSLote).filter(
        TISSLote.id == lote_id,
        TISSLote.organization_id == current_user.organization_id,
        TISSLote.deleted_at.is_(None)
    ).first()
    
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    if lote.status != "rascunho":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas lotes em rascunho podem ser deletados"
        )
    
    # Soft delete
    lote.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
