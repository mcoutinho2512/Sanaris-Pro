"""
Rotas de Faturamento TISS
Padrão ANS para Planos de Saúde
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, extract
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.tiss import (
    HealthInsuranceOperator, TussProcedure, Beneficiary,
    TissGuide, TissGuideProcedure, TissBatch,
    GuideStatus, BatchStatus
)
from app.schemas.tiss import (
    HealthInsuranceOperatorCreate, HealthInsuranceOperatorUpdate, HealthInsuranceOperatorResponse,
    TussProcedureCreate, TussProcedureUpdate, TussProcedureResponse,
    BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryResponse,
    TissGuideCreate, TissGuideUpdate, TissGuideResponse, TissGuideListResponse,
    TissGuideProcedureResponse,
    TissBatchCreate, TissBatchUpdate, TissBatchResponse, TissBatchListResponse,
    AddGuideToBatchRequest, CloseBatchRequest, GlossGuideRequest,
    TissSummaryByOperator, TissSummaryByPeriod,
    GuideStatusEnum, BatchStatusEnum
)
from app.services.financial_service import financial_service

router = APIRouter(prefix="/api/v1/tiss", tags=["Faturamento TISS"])


# ============================================
# OPERADORAS
# ============================================

@router.post("/operators", response_model=HealthInsuranceOperatorResponse, status_code=status.HTTP_201_CREATED)
def create_operator(operator_data: HealthInsuranceOperatorCreate, db: Session = Depends(get_db)):
    """Cadastra operadora de plano de saúde"""
    
    # Verifica duplicidade
    existing = db.query(HealthInsuranceOperator).filter(
        HealthInsuranceOperator.ans_code == operator_data.ans_code,
        HealthInsuranceOperator.is_deleted == False
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operadora com este código ANS já cadastrada"
        )
    
    operator = HealthInsuranceOperator(**operator_data.dict())
    db.add(operator)
    db.commit()
    db.refresh(operator)
    
    return operator


@router.get("/operators", response_model=List[HealthInsuranceOperatorResponse])
def list_operators(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista operadoras"""
    
    query = db.query(HealthInsuranceOperator).filter(HealthInsuranceOperator.is_deleted == False)
    
    if is_active is not None:
        query = query.filter(HealthInsuranceOperator.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (HealthInsuranceOperator.name.ilike(search_term)) |
            (HealthInsuranceOperator.ans_code.ilike(search_term))
        )
    
    operators = query.order_by(HealthInsuranceOperator.name).offset(skip).limit(limit).all()
    
    return operators


@router.get("/operators/{operator_id}", response_model=HealthInsuranceOperatorResponse)
def get_operator(operator_id: str, db: Session = Depends(get_db)):
    """Busca operadora por ID"""
    
    operator = db.query(HealthInsuranceOperator).filter(
        HealthInsuranceOperator.id == operator_id,
        HealthInsuranceOperator.is_deleted == False
    ).first()
    
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    return operator


@router.put("/operators/{operator_id}", response_model=HealthInsuranceOperatorResponse)
def update_operator(
    operator_id: str,
    operator_data: HealthInsuranceOperatorUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza operadora"""
    
    operator = db.query(HealthInsuranceOperator).filter(
        HealthInsuranceOperator.id == operator_id,
        HealthInsuranceOperator.is_deleted == False
    ).first()
    
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    update_data = operator_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(operator, field, value)
    
    db.commit()
    db.refresh(operator)
    
    return operator


@router.delete("/operators/{operator_id}")
def delete_operator(operator_id: str, db: Session = Depends(get_db)):
    """Deleta operadora (soft delete)"""
    
    operator = db.query(HealthInsuranceOperator).filter(
        HealthInsuranceOperator.id == operator_id,
        HealthInsuranceOperator.is_deleted == False
    ).first()
    
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operadora não encontrada"
        )
    
    operator.is_deleted = True
    operator.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Operadora deletada com sucesso", "success": True}


# ============================================
# PROCEDIMENTOS TUSS
# ============================================

@router.post("/procedures", response_model=TussProcedureResponse, status_code=status.HTTP_201_CREATED)
def create_procedure(procedure_data: TussProcedureCreate, db: Session = Depends(get_db)):
    """Cadastra procedimento TUSS"""
    
    # Verifica duplicidade
    existing = db.query(TussProcedure).filter(TussProcedure.code == procedure_data.code).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Procedimento com este código já cadastrado"
        )
    
    procedure = TussProcedure(**procedure_data.dict())
    db.add(procedure)
    db.commit()
    db.refresh(procedure)
    
    return procedure


@router.get("/procedures", response_model=List[TussProcedureResponse])
def list_procedures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista procedimentos TUSS"""
    
    query = db.query(TussProcedure)
    
    if is_active is not None:
        query = query.filter(TussProcedure.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (TussProcedure.code.ilike(search_term)) |
            (TussProcedure.description.ilike(search_term))
        )
    
    procedures = query.order_by(TussProcedure.code).offset(skip).limit(limit).all()
    
    return procedures


@router.get("/procedures/{procedure_id}", response_model=TussProcedureResponse)
def get_procedure(procedure_id: str, db: Session = Depends(get_db)):
    """Busca procedimento por ID"""
    
    procedure = db.query(TussProcedure).filter(TussProcedure.id == procedure_id).first()
    
    if not procedure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimento não encontrado"
        )
    
    return procedure


@router.put("/procedures/{procedure_id}", response_model=TussProcedureResponse)
def update_procedure(
    procedure_id: str,
    procedure_data: TussProcedureUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza procedimento"""
    
    procedure = db.query(TussProcedure).filter(TussProcedure.id == procedure_id).first()
    
    if not procedure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Procedimento não encontrado"
        )
    
    update_data = procedure_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(procedure, field, value)
    
    db.commit()
    db.refresh(procedure)
    
    return procedure


# ============================================
# BENEFICIÁRIOS
# ============================================

@router.post("/beneficiaries", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(beneficiary_data: BeneficiaryCreate, db: Session = Depends(get_db)):
    """Cadastra beneficiário"""
    
    beneficiary = Beneficiary(**beneficiary_data.dict())
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    
    return beneficiary


@router.get("/beneficiaries", response_model=List[BeneficiaryResponse])
def list_beneficiaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = None,
    operator_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista beneficiários"""
    
    query = db.query(Beneficiary).filter(Beneficiary.is_deleted == False)
    
    if patient_id:
        query = query.filter(Beneficiary.patient_id == patient_id)
    
    if operator_id:
        query = query.filter(Beneficiary.operator_id == operator_id)
    
    if is_active is not None:
        query = query.filter(Beneficiary.is_active == is_active)
    
    beneficiaries = query.offset(skip).limit(limit).all()
    
    return beneficiaries


@router.get("/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    """Busca beneficiário por ID"""
    
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id,
        Beneficiary.is_deleted == False
    ).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiário não encontrado"
        )
    
    return beneficiary


@router.put("/beneficiaries/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(
    beneficiary_id: str,
    beneficiary_data: BeneficiaryUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza beneficiário"""
    
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id,
        Beneficiary.is_deleted == False
    ).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiário não encontrado"
        )
    
    update_data = beneficiary_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(beneficiary, field, value)
    
    db.commit()
    db.refresh(beneficiary)
    
    return beneficiary


@router.delete("/beneficiaries/{beneficiary_id}")
def delete_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    """Deleta beneficiário (soft delete)"""
    
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id,
        Beneficiary.is_deleted == False
    ).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiário não encontrado"
        )
    
    beneficiary.is_deleted = True
    beneficiary.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Beneficiário deletado com sucesso", "success": True}


# ============================================
# GUIAS TISS
# ============================================

@router.post("/guides", response_model=TissGuideResponse, status_code=status.HTTP_201_CREATED)
def create_guide(guide_data: TissGuideCreate, db: Session = Depends(get_db)):
    """Cria guia TISS"""
    
    # Gera número da guia
    guide_number = financial_service.generate_invoice_number(prefix="GUIA")
    
    # Calcula valor total
    total_value = sum(
        proc.unit_value * proc.quantity 
        for proc in guide_data.procedures
    )
    
    # Cria guia
    guide = TissGuide(
        guide_number=guide_number,
        guide_type=guide_data.guide_type.value,
        operator_id=guide_data.operator_id,
        beneficiary_id=guide_data.beneficiary_id,
        healthcare_professional_id=guide_data.healthcare_professional_id,
        appointment_id=guide_data.appointment_id,
        medical_record_id=guide_data.medical_record_id,
        service_date=guide_data.service_date,
        authorization_number=guide_data.authorization_number,
        authorization_date=guide_data.authorization_date,
        total_value=total_value,
        cid_code=guide_data.cid_code,
        clinical_indication=guide_data.clinical_indication,
        observations=guide_data.observations
    )
    
    db.add(guide)
    db.flush()  # Para obter o ID
    
    # Cria procedimentos
    for proc_data in guide_data.procedures:
        total_proc_value = proc_data.unit_value * proc_data.quantity
        
        procedure = TissGuideProcedure(
            guide_id=guide.id,
            procedure_id=proc_data.procedure_id,
            procedure_code=proc_data.procedure_code,
            procedure_description=proc_data.procedure_description,
            quantity=proc_data.quantity,
            unit_value=proc_data.unit_value,
            total_value=total_proc_value,
            execution_date=proc_data.execution_date,
            access_route=proc_data.access_route,
            technique=proc_data.technique
        )
        db.add(procedure)
    
    db.commit()
    db.refresh(guide)
    
    return guide


@router.get("/guides", response_model=List[TissGuideListResponse])
def list_guides(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    operator_id: Optional[str] = None,
    beneficiary_id: Optional[str] = None,
    professional_id: Optional[str] = None,
    status: Optional[GuideStatusEnum] = None,
    batch_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista guias TISS"""
    
    query = db.query(TissGuide).filter(TissGuide.is_deleted == False)
    
    if operator_id:
        query = query.filter(TissGuide.operator_id == operator_id)
    
    if beneficiary_id:
        query = query.filter(TissGuide.beneficiary_id == beneficiary_id)
    
    if professional_id:
        query = query.filter(TissGuide.healthcare_professional_id == professional_id)
    
    if status:
        query = query.filter(TissGuide.status == status.value)
    
    if batch_id:
        query = query.filter(TissGuide.batch_id == batch_id)
    
    if date_from:
        query = query.filter(TissGuide.service_date >= date_from)
    
    if date_to:
        query = query.filter(TissGuide.service_date <= date_to)
    
    guides = query.order_by(desc(TissGuide.created_at)).offset(skip).limit(limit).all()
    
    return guides


@router.get("/guides/{guide_id}", response_model=TissGuideResponse)
def get_guide(guide_id: str, db: Session = Depends(get_db)):
    """Busca guia por ID"""
    
    guide = db.query(TissGuide).filter(
        TissGuide.id == guide_id,
        TissGuide.is_deleted == False
    ).first()
    
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    return guide


@router.get("/guides/{guide_id}/procedures", response_model=List[TissGuideProcedureResponse])
def list_guide_procedures(guide_id: str, db: Session = Depends(get_db)):
    """Lista procedimentos da guia"""
    
    procedures = db.query(TissGuideProcedure).filter(
        TissGuideProcedure.guide_id == guide_id
    ).all()
    
    return procedures


@router.put("/guides/{guide_id}", response_model=TissGuideResponse)
def update_guide(
    guide_id: str,
    guide_data: TissGuideUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza guia"""
    
    guide = db.query(TissGuide).filter(
        TissGuide.id == guide_id,
        TissGuide.is_deleted == False
    ).first()
    
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    if guide.status == GuideStatus.SENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar guia já enviada"
        )
    
    update_data = guide_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(guide, field, value)
    
    db.commit()
    db.refresh(guide)
    
    return guide


@router.delete("/guides/{guide_id}")
def delete_guide(guide_id: str, db: Session = Depends(get_db)):
    """Deleta guia (soft delete)"""
    
    guide = db.query(TissGuide).filter(
        TissGuide.id == guide_id,
        TissGuide.is_deleted == False
    ).first()
    
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    if guide.status == GuideStatus.SENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar guia já enviada"
        )
    
    guide.is_deleted = True
    guide.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Guia deletada com sucesso", "success": True}


# ============================================
# LOTES TISS
# ============================================

@router.post("/batches", response_model=TissBatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch_data: TissBatchCreate, db: Session = Depends(get_db)):
    """Cria lote TISS"""
    
    # Gera número do lote
    batch_number = financial_service.generate_invoice_number(prefix="LOTE")
    
    batch = TissBatch(
        batch_number=batch_number,
        operator_id=batch_data.operator_id,
        reference_month=batch_data.reference_month,
        reference_year=batch_data.reference_year,
        notes=batch_data.notes
    )
    
    db.add(batch)
    db.commit()
    db.refresh(batch)
    
    return batch


@router.get("/batches", response_model=List[TissBatchListResponse])
def list_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    operator_id: Optional[str] = None,
    status: Optional[BatchStatusEnum] = None,
    reference_year: Optional[int] = None,
    reference_month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista lotes TISS"""
    
    query = db.query(TissBatch).filter(TissBatch.is_deleted == False)
    
    if operator_id:
        query = query.filter(TissBatch.operator_id == operator_id)
    
    if status:
        query = query.filter(TissBatch.status == status.value)
    
    if reference_year:
        query = query.filter(TissBatch.reference_year == reference_year)
    
    if reference_month:
        query = query.filter(TissBatch.reference_month == reference_month)
    
    batches = query.order_by(desc(TissBatch.created_at)).offset(skip).limit(limit).all()
    
    return batches


@router.get("/batches/{batch_id}", response_model=TissBatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Busca lote por ID"""
    
    batch = db.query(TissBatch).filter(
        TissBatch.id == batch_id,
        TissBatch.is_deleted == False
    ).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    return batch


@router.post("/batches/add-guide")
def add_guide_to_batch(request: AddGuideToBatchRequest, db: Session = Depends(get_db)):
    """Adiciona guia ao lote"""
    
    guide = db.query(TissGuide).filter(TissGuide.id == request.guide_id).first()
    batch = db.query(TissBatch).filter(TissBatch.id == request.batch_id).first()
    
    if not guide or not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia ou lote não encontrado"
        )
    
    if batch.status != BatchStatus.OPEN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lote não está aberto para receber guias"
        )
    
    guide.batch_id = batch.id
    guide.status = GuideStatus.PENDING.value
    
    # Atualiza totais do lote
    batch.total_guides += 1
    batch.total_value += guide.total_value
    
    db.commit()
    
    return {"message": "Guia adicionada ao lote com sucesso", "success": True}


@router.post("/batches/close")
def close_batch(request: CloseBatchRequest, db: Session = Depends(get_db)):
    """Fecha lote para envio"""
    
    batch = db.query(TissBatch).filter(TissBatch.id == request.batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    if batch.status != BatchStatus.OPEN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lote já está fechado"
        )
    
    if batch.total_guides == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lote não possui guias"
        )
    
    batch.status = BatchStatus.CLOSED.value
    batch.closed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Lote fechado com sucesso", "success": True}


@router.post("/guides/gloss")
def gloss_guide(request: GlossGuideRequest, db: Session = Depends(get_db)):
    """Glosa (nega) guia"""
    
    guide = db.query(TissGuide).filter(TissGuide.id == request.guide_id).first()
    
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guia não encontrada"
        )
    
    guide.status = GuideStatus.GLOSS.value
    guide.gloss_value = request.gloss_value
    guide.gloss_reason = request.gloss_reason
    guide.gloss_date = datetime.utcnow()
    guide.accepted_value = guide.total_value - request.gloss_value
    
    db.commit()
    
    return {"message": "Guia glosada com sucesso", "success": True}


# ============================================
# RELATÓRIOS
# ============================================

@router.get("/reports/by-operator", response_model=List[TissSummaryByOperator])
def get_summary_by_operator(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Resumo por operadora"""
    
    query = db.query(
        HealthInsuranceOperator.id,
        HealthInsuranceOperator.name,
        func.count(TissGuide.id).label('total_guides'),
        func.sum(TissGuide.total_value).label('total_value'),
        func.sum(TissGuide.accepted_value).label('accepted_value'),
        func.sum(TissGuide.gloss_value).label('gloss_value')
    ).join(
        TissGuide, TissGuide.operator_id == HealthInsuranceOperator.id
    ).filter(
        TissGuide.is_deleted == False
    )
    
    if year:
        query = query.filter(extract('year', TissGuide.service_date) == year)
    if month:
        query = query.filter(extract('month', TissGuide.service_date) == month)
    
    results = query.group_by(HealthInsuranceOperator.id, HealthInsuranceOperator.name).all()
    
    return [
        TissSummaryByOperator(
            operator_id=r.id,
            operator_name=r.name,
            total_guides=r.total_guides,
            total_value=r.total_value or Decimal(0),
            accepted_value=r.accepted_value or Decimal(0),
            gloss_value=r.gloss_value or Decimal(0)
        )
        for r in results
    ]
