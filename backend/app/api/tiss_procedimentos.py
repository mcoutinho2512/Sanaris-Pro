from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiss import TISSProcedimento, TISSGuia, TISSLote
from app.schemas.tiss import (
    TISSProcedimentoCreate,
    TISSProcedimentoUpdate,
    TISSProcedimentoResponse
)

router = APIRouter(prefix="/tiss/procedimentos", tags=["TISS - Procedimentos"])


@router.post("/", response_model=TISSProcedimentoResponse, status_code=status.HTTP_201_CREATED)
def criar_procedimento(
    procedimento: TISSProcedimentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adicionar procedimento a uma guia"""
    
    # Verificar se guia existe
    guia = db.query(TISSGuia).filter(
        TISSGuia.id == procedimento.guia_id,
        TISSGuia.organization_id == current_user.organization_id,
        TISSGuia.deleted_at.is_(None)
    ).first()
    
    if not guia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    # Verificar se lote está em rascunho
    lote = db.query(TISSLote).filter(TISSLote.id == guia.lote_id).first()
    if lote and lote.status != "rascunho":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível adicionar procedimentos a guias de lotes que não estão em rascunho"
        )
    
    # Calcular valor total
    valor_total = procedimento.valor_unitario_informado * procedimento.quantidade_executada
    
    # Criar procedimento
    procedimento_data = procedimento.model_dump()
    db_procedimento = TISSProcedimento(
        organization_id=current_user.organization_id,
        valor_total_informado=valor_total,
        **procedimento_data
    )
    
    db.add(db_procedimento)
    
    # Recalcular valor da guia
    procedimentos_guia = db.query(TISSProcedimento).filter(
        TISSProcedimento.guia_id == procedimento.guia_id,
        TISSProcedimento.deleted_at.is_(None)
    ).all()
    
    valor_total_guia = sum(p.valor_total_informado for p in procedimentos_guia) + valor_total
    guia.valor_total_informado = valor_total_guia
    guia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_procedimento)
    
    return db_procedimento


@router.get("/guia/{guia_id}", response_model=List[TISSProcedimentoResponse])
def listar_procedimentos_guia(
    guia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar procedimentos de uma guia"""
    
    # Verificar se guia existe
    guia = db.query(TISSGuia).filter(
        TISSGuia.id == guia_id,
        TISSGuia.organization_id == current_user.organization_id,
        TISSGuia.deleted_at.is_(None)
    ).first()
    
    if not guia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    procedimentos = db.query(TISSProcedimento).filter(
        TISSProcedimento.guia_id == guia_id,
        TISSProcedimento.deleted_at.is_(None)
    ).all()
    
    return procedimentos


@router.get("/{procedimento_id}", response_model=TISSProcedimentoResponse)
def obter_procedimento(
    procedimento_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de um procedimento"""
    
    procedimento = db.query(TISSProcedimento).filter(
        TISSProcedimento.id == procedimento_id,
        TISSProcedimento.organization_id == current_user.organization_id,
        TISSProcedimento.deleted_at.is_(None)
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimento não encontrado"
        )
    
    return procedimento


@router.put("/{procedimento_id}", response_model=TISSProcedimentoResponse)
def atualizar_procedimento(
    procedimento_id: UUID,
    procedimento_update: TISSProcedimentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar dados de um procedimento"""
    
    procedimento = db.query(TISSProcedimento).filter(
        TISSProcedimento.id == procedimento_id,
        TISSProcedimento.organization_id == current_user.organization_id,
        TISSProcedimento.deleted_at.is_(None)
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimento não encontrado"
        )
    
    # Verificar se guia está em lote fechado
    guia = db.query(TISSGuia).filter(TISSGuia.id == procedimento.guia_id).first()
    if guia:
        lote = db.query(TISSLote).filter(TISSLote.id == guia.lote_id).first()
        if lote and lote.status != "rascunho":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível editar procedimentos de lotes que não estão em rascunho"
            )
    
    # Atualizar campos
    update_data = procedimento_update.model_dump(exclude_unset=True)
    
    # Recalcular valor total se quantidade ou valor unitário mudaram
    if "quantidade_executada" in update_data or "valor_unitario_informado" in update_data:
        quantidade = update_data.get("quantidade_executada", procedimento.quantidade_executada)
        valor_unitario = update_data.get("valor_unitario_informado", procedimento.valor_unitario_informado)
        update_data["valor_total_informado"] = quantidade * valor_unitario
    
    for field, value in update_data.items():
        setattr(procedimento, field, value)
    
    procedimento.updated_at = datetime.utcnow()
    
    # Recalcular valor da guia
    if guia:
        procedimentos_guia = db.query(TISSProcedimento).filter(
            TISSProcedimento.guia_id == guia.id,
            TISSProcedimento.deleted_at.is_(None)
        ).all()
        
        valor_total_guia = sum(p.valor_total_informado for p in procedimentos_guia)
        guia.valor_total_informado = valor_total_guia
        guia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(procedimento)
    
    return procedimento


@router.delete("/{procedimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_procedimento(
    procedimento_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar procedimento (soft delete)"""
    
    procedimento = db.query(TISSProcedimento).filter(
        TISSProcedimento.id == procedimento_id,
        TISSProcedimento.organization_id == current_user.organization_id,
        TISSProcedimento.deleted_at.is_(None)
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimento não encontrado"
        )
    
    # Verificar se guia está em lote fechado
    guia = db.query(TISSGuia).filter(TISSGuia.id == procedimento.guia_id).first()
    if guia:
        lote = db.query(TISSLote).filter(TISSLote.id == guia.lote_id).first()
        if lote and lote.status != "rascunho":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível deletar procedimentos de lotes que não estão em rascunho"
            )
    
    # Soft delete
    procedimento.deleted_at = datetime.utcnow()
    
    # Recalcular valor da guia
    if guia:
        procedimentos_guia = db.query(TISSProcedimento).filter(
            TISSProcedimento.guia_id == guia.id,
            TISSProcedimento.deleted_at.is_(None),
            TISSProcedimento.id != procedimento_id
        ).all()
        
        valor_total_guia = sum(p.valor_total_informado for p in procedimentos_guia)
        guia.valor_total_informado = valor_total_guia
        guia.updated_at = datetime.utcnow()
    
    db.commit()
    
    return None
