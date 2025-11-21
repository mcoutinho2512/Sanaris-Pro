from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tiss import TISSTabelaReferencia
from app.schemas.tiss import (
    TISSTabelaReferenciaCreate,
    TISSTabelaReferenciaUpdate,
    TISSTabelaReferenciaResponse
)

router = APIRouter(prefix="/tiss/tabelas", tags=["TISS - Tabelas de Referência"])


@router.post("/", response_model=TISSTabelaReferenciaResponse, status_code=status.HTTP_201_CREATED)
def criar_tabela_referencia(
    tabela: TISSTabelaReferenciaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cadastrar procedimento em tabela de referência (TUSS/CBHPM)"""
    
    # Verificar se já existe código na mesma tabela
    existing = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.tipo_tabela == tabela.tipo_tabela,
        TISSTabelaReferencia.codigo == tabela.codigo,
        TISSTabelaReferencia.deleted_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código {tabela.codigo} já existe na tabela {tabela.tipo_tabela}"
        )
    
    # Criar registro
    db_tabela = TISSTabelaReferencia(
        organization_id=current_user.organization_id,
        **tabela.model_dump()
    )
    
    db.add(db_tabela)
    db.commit()
    db.refresh(db_tabela)
    
    return db_tabela


@router.get("/", response_model=List[TISSTabelaReferenciaResponse])
def listar_tabelas_referencia(
    skip: int = 0,
    limit: int = 100,
    tipo_tabela: str = None,
    codigo_tabela: str = None,
    ativo: bool = None,
    busca: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar procedimentos das tabelas de referência"""
    
    query = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.deleted_at.is_(None)
    )
    
    if tipo_tabela:
        query = query.filter(TISSTabelaReferencia.tipo_tabela == tipo_tabela)
    
    if codigo_tabela:
        query = query.filter(TISSTabelaReferencia.codigo_tabela == codigo_tabela)
    
    if ativo is not None:
        query = query.filter(TISSTabelaReferencia.ativo == ativo)
    
    if busca:
        query = query.filter(
            (TISSTabelaReferencia.codigo.ilike(f"%{busca}%")) |
            (TISSTabelaReferencia.descricao.ilike(f"%{busca}%"))
        )
    
    tabelas = query.order_by(TISSTabelaReferencia.codigo).offset(skip).limit(limit).all()
    return tabelas


@router.get("/buscar/{codigo}", response_model=TISSTabelaReferenciaResponse)
def buscar_por_codigo(
    codigo: str,
    tipo_tabela: str = "TUSS",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buscar procedimento por código"""
    
    tabela = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.tipo_tabela == tipo_tabela,
        TISSTabelaReferencia.codigo == codigo,
        TISSTabelaReferencia.ativo == True,
        TISSTabelaReferencia.deleted_at.is_(None)
    ).first()
    
    if not tabela:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Código {codigo} não encontrado na tabela {tipo_tabela}"
        )
    
    return tabela


@router.get("/{tabela_id}", response_model=TISSTabelaReferenciaResponse)
def obter_tabela_referencia(
    tabela_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de um procedimento da tabela"""
    
    tabela = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.id == tabela_id,
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.deleted_at.is_(None)
    ).first()
    
    if not tabela:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado"
        )
    
    return tabela


@router.put("/{tabela_id}", response_model=TISSTabelaReferenciaResponse)
def atualizar_tabela_referencia(
    tabela_id: UUID,
    tabela_update: TISSTabelaReferenciaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar procedimento da tabela de referência"""
    
    tabela = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.id == tabela_id,
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.deleted_at.is_(None)
    ).first()
    
    if not tabela:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado"
        )
    
    # Atualizar campos
    update_data = tabela_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tabela, field, value)
    
    tabela.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(tabela)
    
    return tabela


@router.delete("/{tabela_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_tabela_referencia(
    tabela_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletar procedimento da tabela (soft delete)"""
    
    tabela = db.query(TISSTabelaReferencia).filter(
        TISSTabelaReferencia.id == tabela_id,
        TISSTabelaReferencia.organization_id == current_user.organization_id,
        TISSTabelaReferencia.deleted_at.is_(None)
    ).first()
    
    if not tabela:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado"
        )
    
    # Soft delete
    tabela.deleted_at = datetime.utcnow()
    db.commit()
    
    return None


@router.post("/importar-tuss", status_code=status.HTTP_201_CREATED)
def importar_tuss(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importar procedimentos básicos da tabela TUSS"""
    
    # Alguns procedimentos TUSS comuns como exemplo
    procedimentos_tuss = [
        {
            "tipo_tabela": "TUSS",
            "codigo_tabela": "22",
            "codigo": "10101012",
            "descricao": "CONSULTA EM CONSULTÓRIO",
            "valor_referencia": 100.00,
            "data_inicio_vigencia": "2024-01-01",
            "capitulo": "PROCEDIMENTOS CLÍNICOS",
            "grupo": "CONSULTAS"
        },
        {
            "tipo_tabela": "TUSS",
            "codigo_tabela": "22",
            "codigo": "10101020",
            "descricao": "CONSULTA EM PRONTO-SOCORRO",
            "valor_referencia": 150.00,
            "data_inicio_vigencia": "2024-01-01",
            "capitulo": "PROCEDIMENTOS CLÍNICOS",
            "grupo": "CONSULTAS"
        },
        {
            "tipo_tabela": "TUSS",
            "codigo_tabela": "22",
            "codigo": "20101015",
            "descricao": "ELETROCARDIOGRAMA",
            "valor_referencia": 80.00,
            "data_inicio_vigencia": "2024-01-01",
            "capitulo": "PROCEDIMENTOS DIAGNÓSTICOS",
            "grupo": "EXAMES"
        }
    ]
    
    importados = 0
    for proc in procedimentos_tuss:
        # Verificar se já existe
        existing = db.query(TISSTabelaReferencia).filter(
            TISSTabelaReferencia.organization_id == current_user.organization_id,
            TISSTabelaReferencia.codigo == proc["codigo"],
            TISSTabelaReferencia.deleted_at.is_(None)
        ).first()
        
        if not existing:
            db_proc = TISSTabelaReferencia(
                organization_id=current_user.organization_id,
                **proc
            )
            db.add(db_proc)
            importados += 1
    
    db.commit()
    
    return {
        "message": f"{importados} procedimentos TUSS importados com sucesso",
        "total_importados": importados
    }
