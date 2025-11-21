from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiss import TISSGuia, TISSLote, TISSProcedimento
from app.models.patient import Patient
from app.schemas.tiss import (
    TISSGuiaCreate,
    TISSGuiaUpdate,
    TISSGuiaResponse,
    TISSGuiaListResponse,
    TISSGuiaComProcedimentos
)

router = APIRouter(prefix="/tiss/guias", tags=["TISS - Guias"])


def gerar_numero_guia(db: Session, organization_id: UUID) -> str:
    """Gerar número sequencial da guia"""
    # Formato: GUIA-AAAA-XXXXXX (Ex: GUIA-2024-000001)
    ano_atual = datetime.utcnow().year
    
    # Contar guias do ano
    count = db.query(TISSGuia).filter(
        TISSGuia.organization_id == organization_id,
        TISSGuia.numero_guia_prestador.like(f"GUIA-{ano_atual}-%"),
        TISSGuia.deleted_at.is_(None)
    ).count()
    
    sequencial = str(count + 1).zfill(6)
    return f"GUIA-{ano_atual}-{sequencial}"


@router.post("/", response_model=TISSGuiaResponse, status_code=status.HTTP_201_CREATED)
def criar_guia(
    guia: TISSGuiaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova guia TISS"""
    
    # Verificar se lote existe
    lote = db.query(TISSLote).filter(
        TISSLote.id == guia.lote_id,
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
            detail="Não é possível adicionar guias a um lote que não está em rascunho"
        )
    
    # Verificar se paciente existe
    paciente = db.query(Patient).filter(
        Patient.id == guia.patient_id,
        Patient.organization_id == current_user.organization_id
    ).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Gerar número da guia
    numero_guia = gerar_numero_guia(db, current_user.organization_id)
    
    # Criar guia
    guia_data = guia.model_dump()
    db_guia = TISSGuia(
        organization_id=current_user.organization_id,
        numero_guia_prestador=numero_guia,
        **guia_data
    )
    
    db.add(db_guia)
    db.commit()
    db.refresh(db_guia)
    
    return db_guia


@router.get("/", response_model=List[TISSGuiaListResponse])
def listar_guias(
    skip: int = 0,
    limit: int = 100,
    lote_id: UUID = None,
    patient_id: UUID = None,
    status: str = None,
    tipo_guia: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar guias TISS"""
    
    query = db.query(TISSGuia).filter(
        TISSGuia.organization_id == current_user.organization_id,
        TISSGuia.deleted_at.is_(None)
    )
    
    if lote_id:
        query = query.filter(TISSGuia.lote_id == lote_id)
    
    if patient_id:
        query = query.filter(TISSGuia.patient_id == patient_id)
    
    if status:
        query = query.filter(TISSGuia.status == status)
    
    if tipo_guia:
        query = query.filter(TISSGuia.tipo_guia == tipo_guia)
    
    guias = query.order_by(TISSGuia.created_at.desc()).offset(skip).limit(limit).all()
    return guias


@router.get("/{guia_id}", response_model=TISSGuiaComProcedimentos)
def obter_guia(
    guia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de uma guia com procedimentos"""
    
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
    
    # Buscar procedimentos
    procedimentos = db.query(TISSProcedimento).filter(
        TISSProcedimento.guia_id == guia_id,
        TISSProcedimento.deleted_at.is_(None)
    ).all()
    
    # Montar resposta
    guia_dict = {
        **guia.__dict__,
        "procedimentos": procedimentos
    }
    
    return guia_dict


@router.put("/{guia_id}", response_model=TISSGuiaResponse)
def atualizar_guia(
    guia_id: UUID,
    guia_update: TISSGuiaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar dados de uma guia"""
    
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
    
    # Verificar se guia está em lote fechado
    lote = db.query(TISSLote).filter(TISSLote.id == guia.lote_id).first()
    if lote and lote.status != "rascunho":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível editar guias de lotes que não estão em rascunho"
        )
    
    # Atualizar campos
    update_data = guia_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guia, field, value)
    
    guia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(guia)
    
    return guia


@router.post("/{guia_id}/calcular-valor", response_model=TISSGuiaResponse)
def calcular_valor_guia(
    guia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calcular valor total da guia baseado nos procedimentos"""
    
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
    
    # Buscar procedimentos
    procedimentos = db.query(TISSProcedimento).filter(
        TISSProcedimento.guia_id == guia_id,
        TISSProcedimento.deleted_at.is_(None)
    ).all()
    
    if not procedimentos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guia não possui procedimentos para calcular o valor"
        )
    
    # Calcular valor total
    valor_total = sum(proc.valor_total_informado for proc in procedimentos)
    
    # Atualizar guia
    guia.valor_total_informado = valor_total
    guia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(guia)
    
    return guia


@router.delete("/{guia_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_guia(
    guia_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar guia (soft delete)"""
    
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
    
    # Verificar se guia está em lote fechado
    lote = db.query(TISSLote).filter(TISSLote.id == guia.lote_id).first()
    if lote and lote.status != "rascunho":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar guias de lotes que não estão em rascunho"
        )
    
    # Soft delete
    guia.deleted_at = datetime.utcnow()
    db.commit()
    
    return None
