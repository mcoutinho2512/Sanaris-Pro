"""
Endpoints de Gestão Financeira
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.patient import Patient
from app.models.financial import AccountReceivable, PaymentStatus, PaymentMethodType
from app.schemas.financial import (
    AccountReceivableCreate,
    AccountReceivableUpdate,
    AccountReceivableResponse,
    PaymentCreate,
    FinancialSummary
)
from app.services.financial_service import FinancialService

router = APIRouter()
financial_service = FinancialService()

@router.post("/receivables", response_model=AccountReceivableResponse)
async def create_receivable(
    data: AccountReceivableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova conta a receber"""
    
    # Verificar se paciente existe
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Calcular total
    total_amount = financial_service.calculate_total_amount(
        original_amount=data.original_amount,
        discount_amount=data.discount_amount or Decimal(0),
        interest_amount=data.interest_amount or Decimal(0),
        fine_amount=data.fine_amount or Decimal(0)
    )
    
    # Gerar número de fatura
    invoice_number = financial_service.generate_invoice_number()
    
    # Criar conta
    receivable = AccountReceivable(
        invoice_number=invoice_number,
        description=data.description,
        patient_id=data.patient_id,
        healthcare_professional_id=data.healthcare_professional_id,
        appointment_id=data.appointment_id,
        original_amount=data.original_amount,
        discount_amount=data.discount_amount or Decimal(0),
        interest_amount=data.interest_amount or Decimal(0),
        fine_amount=data.fine_amount or Decimal(0),
        total_amount=total_amount,
        paid_amount=Decimal(0),
        remaining_amount=total_amount,
        due_date=data.due_date,
        status=PaymentStatus.PENDING,
        total_installments=data.total_installments or 1,
        current_installment=1,
        payment_method=data.payment_method,
        notes=data.notes
    )
    
    db.add(receivable)
    db.commit()
    db.refresh(receivable)
    
    # Montar resposta
    return AccountReceivableResponse(
        id=receivable.id,
        invoice_number=receivable.invoice_number,
        description=receivable.description,
        patient_id=receivable.patient_id,
        patient_name=patient.full_name,
        healthcare_professional_id=receivable.healthcare_professional_id,
        original_amount=receivable.original_amount,
        discount_amount=receivable.discount_amount,
        interest_amount=receivable.interest_amount,
        fine_amount=receivable.fine_amount,
        total_amount=receivable.total_amount,
        paid_amount=receivable.paid_amount,
        remaining_amount=receivable.remaining_amount,
        issue_date=receivable.issue_date,
        due_date=receivable.due_date,
        payment_date=receivable.payment_date,
        status=receivable.status.value,
        total_installments=receivable.total_installments,
        current_installment=receivable.current_installment,
        payment_method=receivable.payment_method,
        notes=receivable.notes,
        created_at=receivable.created_at
    )


@router.get("/receivables", response_model=List[AccountReceivableResponse])
async def list_receivables(
    status: Optional[str] = None,
    patient_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar contas a receber"""
    
    query = db.query(AccountReceivable).filter(
        AccountReceivable.is_deleted == False
    )
    
    if status:
        query = query.filter(AccountReceivable.status == status)
    
    if patient_id:
        query = query.filter(AccountReceivable.patient_id == patient_id)
    
    if start_date:
        query = query.filter(AccountReceivable.due_date >= start_date)
    
    if end_date:
        query = query.filter(AccountReceivable.due_date <= end_date)
    
    receivables = query.order_by(AccountReceivable.due_date.desc()).offset(skip).limit(limit).all()
    
    result = []
    for r in receivables:
        patient = db.query(Patient).filter(Patient.id == r.patient_id).first()
        professional = db.query(User).filter(User.id == r.healthcare_professional_id).first() if r.healthcare_professional_id else None
        
        result.append(AccountReceivableResponse(
            id=r.id,
            invoice_number=r.invoice_number,
            description=r.description,
            patient_id=r.patient_id,
            patient_name=patient.full_name if patient else None,
            healthcare_professional_id=r.healthcare_professional_id,
            professional_name=professional.full_name if professional else None,
            original_amount=r.original_amount,
            discount_amount=r.discount_amount,
            interest_amount=r.interest_amount,
            fine_amount=r.fine_amount,
            total_amount=r.total_amount,
            paid_amount=r.paid_amount,
            remaining_amount=r.remaining_amount,
            issue_date=r.issue_date,
            due_date=r.due_date,
            payment_date=r.payment_date,
            status=r.status.value,
            total_installments=r.total_installments,
            current_installment=r.current_installment,
            payment_method=r.payment_method,
            notes=r.notes,
            created_at=r.created_at
        ))
    
    return result


@router.get("/receivables/{receivable_id}", response_model=AccountReceivableResponse)
async def get_receivable(
    receivable_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de conta a receber"""
    
    receivable = db.query(AccountReceivable).filter(
        AccountReceivable.id == receivable_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not receivable:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    patient = db.query(Patient).filter(Patient.id == receivable.patient_id).first()
    professional = db.query(User).filter(User.id == receivable.healthcare_professional_id).first() if receivable.healthcare_professional_id else None
    
    return AccountReceivableResponse(
        id=receivable.id,
        invoice_number=receivable.invoice_number,
        description=receivable.description,
        patient_id=receivable.patient_id,
        patient_name=patient.full_name if patient else None,
        healthcare_professional_id=receivable.healthcare_professional_id,
        professional_name=professional.full_name if professional else None,
        original_amount=receivable.original_amount,
        discount_amount=receivable.discount_amount,
        interest_amount=receivable.interest_amount,
        fine_amount=receivable.fine_amount,
        total_amount=receivable.total_amount,
        paid_amount=receivable.paid_amount,
        remaining_amount=receivable.remaining_amount,
        issue_date=receivable.issue_date,
        due_date=receivable.due_date,
        payment_date=receivable.payment_date,
        status=receivable.status.value,
        total_installments=receivable.total_installments,
        current_installment=receivable.current_installment,
        payment_method=receivable.payment_method,
        notes=receivable.notes,
        created_at=receivable.created_at
    )


@router.post("/receivables/{receivable_id}/pay")
async def register_payment(
    receivable_id: str,
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar pagamento"""
    
    receivable = db.query(AccountReceivable).filter(
        AccountReceivable.id == receivable_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not receivable:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    if receivable.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Conta já paga")
    
    # Atualizar valores
    new_paid = receivable.paid_amount + payment.amount
    receivable.paid_amount = new_paid
    receivable.remaining_amount = receivable.total_amount - new_paid
    
    # Atualizar status
    if receivable.remaining_amount <= 0:
        receivable.status = PaymentStatus.PAID
        receivable.payment_date = payment.payment_date or datetime.utcnow()
    elif receivable.paid_amount > 0:
        receivable.status = PaymentStatus.PARTIALLY_PAID
    
    db.commit()
    
    return {
        "success": True,
        "message": "Pagamento registrado",
        "paid_amount": float(receivable.paid_amount),
        "remaining_amount": float(receivable.remaining_amount),
        "status": receivable.status.value
    }


@router.get("/summary", response_model=FinancialSummary)
async def financial_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resumo financeiro"""
    
    query = db.query(AccountReceivable).filter(
        AccountReceivable.is_deleted == False
    )
    
    if start_date:
        query = query.filter(AccountReceivable.due_date >= start_date)
    if end_date:
        query = query.filter(AccountReceivable.due_date <= end_date)
    
    all_receivables = query.all()
    
    total_receivable = sum(r.total_amount for r in all_receivables)
    total_received = sum(r.paid_amount for r in all_receivables)
    total_pending = sum(r.remaining_amount for r in all_receivables if r.status == PaymentStatus.PENDING)
    total_overdue = sum(r.remaining_amount for r in all_receivables if r.status == PaymentStatus.OVERDUE)
    
    pending_count = len([r for r in all_receivables if r.status == PaymentStatus.PENDING])
    overdue_count = len([r for r in all_receivables if r.status == PaymentStatus.OVERDUE])
    paid_count = len([r for r in all_receivables if r.status == PaymentStatus.PAID])
    
    return FinancialSummary(
        total_receivable=total_receivable,
        total_received=total_received,
        total_pending=total_pending,
        total_overdue=total_overdue,
        pending_count=pending_count,
        overdue_count=overdue_count,
        paid_count=paid_count
    )


@router.put("/receivables/{receivable_id}")
async def update_receivable(
    receivable_id: str,
    data: AccountReceivableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar conta a receber"""
    
    receivable = db.query(AccountReceivable).filter(
        AccountReceivable.id == receivable_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not receivable:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    if data.description:
        receivable.description = data.description
    if data.due_date:
        receivable.due_date = data.due_date
    if data.discount_amount is not None:
        receivable.discount_amount = data.discount_amount
        # Recalcular total
        receivable.total_amount = financial_service.calculate_total_amount(
            receivable.original_amount,
            receivable.discount_amount,
            receivable.interest_amount,
            receivable.fine_amount
        )
        receivable.remaining_amount = receivable.total_amount - receivable.paid_amount
    if data.status:
        receivable.status = data.status
    if data.notes:
        receivable.notes = data.notes
    
    db.commit()
    
    return {"success": True, "message": "Conta atualizada"}


@router.delete("/receivables/{receivable_id}")
async def delete_receivable(
    receivable_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir conta a receber (soft delete)"""
    
    receivable = db.query(AccountReceivable).filter(
        AccountReceivable.id == receivable_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not receivable:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    receivable.is_deleted = True
    db.commit()
    
    return {"success": True, "message": "Conta excluída"}
