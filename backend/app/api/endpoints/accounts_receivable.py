"""
Rotas de Contas a Receber
Gestão Financeira Completa
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.models.financial import (
    AccountReceivable, PaymentInstallment, PaymentTransaction,
    PaymentStatus, PaymentMethodType, RecurrenceType
)
from app.models.patient import Patient
from app.schemas.financial import (
    AccountReceivableCreate, AccountReceivableUpdate, AccountReceivableResponse,
    AccountReceivableListResponse, PaymentInstallmentResponse,
    PaymentTransactionCreate, PaymentTransactionResponse,
    ConfirmPaymentRequest, RefundPaymentRequest, CancelAccountRequest,
    FinancialSummary, PaymentMethodSummary, DailyRevenue, MonthlyRevenue,
    PaymentStatusEnum, PaymentMethodEnum
)
from app.services.financial_service import financial_service

router = APIRouter(prefix="/api/v1/financial/receivables", tags=["Contas a Receber"])


# ============================================
# CONTAS A RECEBER - CRUD
# ============================================

@router.post("", response_model=AccountReceivableResponse, status_code=status.HTTP_201_CREATED)
def create_account_receivable(account_data: AccountReceivableCreate, db: Session = Depends(get_db)):
    """Cria nova conta a receber"""
    
    # Valida paciente
    patient = db.query(Patient).filter(Patient.id == account_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Gera número da fatura
    invoice_number = financial_service.generate_invoice_number()
    
    # Calcula valores
    total_amount = financial_service.calculate_total_amount(
        original_amount=account_data.original_amount,
        discount_amount=account_data.discount_amount
    )
    
    remaining_amount = total_amount
    
    # Cria conta
    account = AccountReceivable(
        invoice_number=invoice_number,
        description=account_data.description,
        patient_id=account_data.patient_id,
        healthcare_professional_id=account_data.healthcare_professional_id,
        appointment_id=account_data.appointment_id,
        original_amount=account_data.original_amount,
        discount_amount=account_data.discount_amount,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        due_date=account_data.due_date,
        total_installments=account_data.total_installments,
        is_recurring=account_data.is_recurring,
        recurrence_type=account_data.recurrence_type.value,
        recurrence_day=account_data.recurrence_day,
        charge_interest=account_data.charge_interest,
        interest_rate_daily=account_data.interest_rate_daily,
        charge_fine=account_data.charge_fine,
        fine_rate=account_data.fine_rate,
        notes=account_data.notes
    )
    
    db.add(account)
    db.flush()  # Para ter o ID
    
    # Gera parcelas se necessário
    if account_data.total_installments > 1:
        installments_data = financial_service.generate_installments(
            total_amount=total_amount,
            num_installments=account_data.total_installments,
            first_due_date=account_data.due_date
        )
        
        for inst_data in installments_data:
            installment = PaymentInstallment(
                account_receivable_id=account.id,
                installment_number=inst_data['installment_number'],
                original_amount=inst_data['original_amount'],
                total_amount=inst_data['total_amount'],
                due_date=inst_data['due_date']
            )
            db.add(installment)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.get("", response_model=List[AccountReceivableListResponse])
def list_accounts_receivable(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = None,
    professional_id: Optional[str] = None,
    status: Optional[PaymentStatusEnum] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    is_overdue: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista contas a receber com filtros"""
    
    query = db.query(AccountReceivable).filter(AccountReceivable.is_deleted == False)
    
    if patient_id:
        query = query.filter(AccountReceivable.patient_id == patient_id)
    
    if professional_id:
        query = query.filter(AccountReceivable.healthcare_professional_id == professional_id)
    
    if status:
        query = query.filter(AccountReceivable.status == status.value)
    
    if date_from:
        query = query.filter(AccountReceivable.due_date >= date_from)
    
    if date_to:
        query = query.filter(AccountReceivable.due_date <= date_to)
    
    if is_overdue is not None:
        if is_overdue:
            query = query.filter(
                and_(
                    AccountReceivable.status != PaymentStatus.PAID.value,
                    AccountReceivable.due_date < datetime.utcnow()
                )
            )
        else:
            query = query.filter(AccountReceivable.due_date >= datetime.utcnow())
    
    accounts = query.order_by(desc(AccountReceivable.created_at)).offset(skip).limit(limit).all()
    
    return accounts


@router.get("/{account_id}", response_model=AccountReceivableResponse)
def get_account_receivable(account_id: str, db: Session = Depends(get_db)):
    """Busca conta a receber por ID"""
    
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == account_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    # Atualiza juros e multa se vencida
    if account.status not in [PaymentStatus.PAID.value, PaymentStatus.CANCELLED.value]:
        if datetime.utcnow() > account.due_date:
            charges = financial_service.calculate_overdue_charges(
                original_amount=account.original_amount,
                due_date=account.due_date,
                charge_interest=account.charge_interest,
                interest_rate_daily=account.interest_rate_daily,
                charge_fine=account.charge_fine,
                fine_rate=account.fine_rate
            )
            
            account.interest_amount = charges['interest_amount']
            account.fine_amount = charges['fine_amount']
            account.total_amount = financial_service.calculate_total_amount(
                account.original_amount,
                account.discount_amount,
                account.interest_amount,
                account.fine_amount
            )
            account.remaining_amount = account.total_amount - account.paid_amount
            account.status = PaymentStatus.OVERDUE.value
            
            db.commit()
            db.refresh(account)
    
    return account


@router.put("/{account_id}", response_model=AccountReceivableResponse)
def update_account_receivable(
    account_id: str,
    account_data: AccountReceivableUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza conta a receber"""
    
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == account_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    if account.status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar conta já paga"
        )
    
    update_data = account_data.dict(exclude_unset=True)
    
    # Recalcula total se desconto mudou
    if 'discount_amount' in update_data:
        account.total_amount = financial_service.calculate_total_amount(
            account.original_amount,
            update_data['discount_amount'],
            account.interest_amount,
            account.fine_amount
        )
        account.remaining_amount = account.total_amount - account.paid_amount
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}")
def delete_account_receivable(account_id: str, db: Session = Depends(get_db)):
    """Deleta conta a receber (soft delete)"""
    
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == account_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    if account.status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar conta já paga"
        )
    
    account.is_deleted = True
    account.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Conta deletada com sucesso", "success": True}


@router.post("/{account_id}/cancel")
def cancel_account(account_id: str, cancel_data: CancelAccountRequest, db: Session = Depends(get_db)):
    """Cancela conta a receber"""
    
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == account_id,
        AccountReceivable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    if account.status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar conta já paga"
        )
    
    account.status = PaymentStatus.CANCELLED.value
    account.notes = f"{account.notes or ''}\n[CANCELADO] {cancel_data.reason}"
    
    db.commit()
    
    return {"message": "Conta cancelada com sucesso", "success": True}


# ============================================
# PARCELAS
# ============================================

@router.get("/{account_id}/installments", response_model=List[PaymentInstallmentResponse])
def list_installments(account_id: str, db: Session = Depends(get_db)):
    """Lista parcelas da conta"""
    
    installments = db.query(PaymentInstallment).filter(
        PaymentInstallment.account_receivable_id == account_id
    ).order_by(PaymentInstallment.installment_number).all()
    
    return installments


# ============================================
# TRANSAÇÕES DE PAGAMENTO
# ============================================

@router.post("/payments", response_model=PaymentTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_payment_transaction(payment_data: PaymentTransactionCreate, db: Session = Depends(get_db)):
    """Registra pagamento"""
    
    # Busca conta
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == payment_data.account_receivable_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    if account.status in [PaymentStatus.PAID.value, PaymentStatus.CANCELLED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta já está paga ou cancelada"
        )
    
    # Valida valor
    if payment_data.amount > account.remaining_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor do pagamento ({payment_data.amount}) maior que saldo devedor ({account.remaining_amount})"
        )
    
    # Gera número de transação
    transaction_number = financial_service.generate_transaction_number()
    
    # Cria transação
    transaction = PaymentTransaction(
        account_receivable_id=payment_data.account_receivable_id,
        installment_id=payment_data.installment_id,
        transaction_number=transaction_number,
        payment_method=payment_data.payment_method.value,
        amount=payment_data.amount,
        card_brand=payment_data.card_brand,
        card_last_digits=payment_data.card_last_digits,
        pix_key=payment_data.pix_key,
        pix_txid=payment_data.pix_txid,
        check_number=payment_data.check_number,
        bank_slip_barcode=payment_data.bank_slip_barcode,
        authorization_code=payment_data.authorization_code,
        nsu=payment_data.nsu,
        notes=payment_data.notes,
        payment_date=payment_data.payment_date or datetime.utcnow(),
        is_confirmed=True,  # Por padrão já confirmado
        confirmed_at=datetime.utcnow()
    )
    
    db.add(transaction)
    
    # Atualiza conta
    account.paid_amount += payment_data.amount
    account.remaining_amount = account.total_amount - account.paid_amount
    
    # Atualiza status
    if account.remaining_amount <= 0:
        account.status = PaymentStatus.PAID.value
        account.payment_date = transaction.payment_date
    elif account.paid_amount > 0:
        account.status = PaymentStatus.PARTIALLY_PAID.value
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.get("/payments", response_model=List[PaymentTransactionResponse])
def list_payment_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    account_id: Optional[str] = None,
    payment_method: Optional[PaymentMethodEnum] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista transações de pagamento"""
    
    query = db.query(PaymentTransaction)
    
    if account_id:
        query = query.filter(PaymentTransaction.account_receivable_id == account_id)
    
    if payment_method:
        query = query.filter(PaymentTransaction.payment_method == payment_method.value)
    
    if date_from:
        query = query.filter(PaymentTransaction.payment_date >= date_from)
    
    if date_to:
        query = query.filter(PaymentTransaction.payment_date <= date_to)
    
    transactions = query.order_by(desc(PaymentTransaction.payment_date)).offset(skip).limit(limit).all()
    
    return transactions


@router.post("/payments/{transaction_id}/refund")
def refund_payment(
    transaction_id: str,
    refund_data: RefundPaymentRequest,
    db: Session = Depends(get_db)
):
    """Estorna pagamento"""
    
    transaction = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada"
        )
    
    if transaction.is_refunded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transação já estornada"
        )
    
    # Busca conta
    account = db.query(AccountReceivable).filter(
        AccountReceivable.id == transaction.account_receivable_id
    ).first()
    
    # Estorna transação
    transaction.is_refunded = True
    transaction.refund_date = refund_data.refund_date or datetime.utcnow()
    transaction.refund_reason = refund_data.refund_reason
    
    # Atualiza conta
    account.paid_amount -= transaction.amount
    account.remaining_amount = account.total_amount - account.paid_amount
    
    # Atualiza status
    account.status = financial_service.determine_payment_status(
        account.total_amount,
        account.paid_amount,
        account.due_date
    )
    
    if account.status == PaymentStatus.PAID.value:
        account.payment_date = None
    
    db.commit()
    
    return {"message": "Pagamento estornado com sucesso", "success": True}


# ============================================
# RELATÓRIOS
# ============================================

@router.get("/reports/summary", response_model=FinancialSummary)
def get_financial_summary(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Resumo financeiro geral"""
    
    query = db.query(AccountReceivable).filter(AccountReceivable.is_deleted == False)
    
    if date_from:
        query = query.filter(AccountReceivable.due_date >= date_from)
    if date_to:
        query = query.filter(AccountReceivable.due_date <= date_to)
    
    accounts = query.all()
    
    summary = {
        "total_pending": Decimal(0),
        "total_paid": Decimal(0),
        "total_overdue": Decimal(0),
        "total_cancelled": Decimal(0),
        "count_pending": 0,
        "count_paid": 0,
        "count_overdue": 0,
        "count_cancelled": 0
    }
    
    for account in accounts:
        if account.status == PaymentStatus.PAID.value:
            summary["total_paid"] += account.total_amount
            summary["count_paid"] += 1
        elif account.status == PaymentStatus.OVERDUE.value:
            summary["total_overdue"] += account.remaining_amount
            summary["count_overdue"] += 1
        elif account.status == PaymentStatus.CANCELLED.value:
            summary["total_cancelled"] += account.total_amount
            summary["count_cancelled"] += 1
        elif account.status in [PaymentStatus.PENDING.value, PaymentStatus.PARTIALLY_PAID.value]:
            summary["total_pending"] += account.remaining_amount
            summary["count_pending"] += 1
    
    return FinancialSummary(**summary)


@router.get("/reports/by-payment-method", response_model=List[PaymentMethodSummary])
def get_payment_method_summary(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Resumo por forma de pagamento"""
    
    query = db.query(
        PaymentTransaction.payment_method,
        func.sum(PaymentTransaction.amount).label('total_amount'),
        func.count(PaymentTransaction.id).label('count')
    )
    
    if date_from:
        query = query.filter(PaymentTransaction.payment_date >= date_from)
    if date_to:
        query = query.filter(PaymentTransaction.payment_date <= date_to)
    
    results = query.group_by(PaymentTransaction.payment_method).all()
    
    return [
        PaymentMethodSummary(
            payment_method=result.payment_method,
            total_amount=result.total_amount or Decimal(0),
            count=result.count
        )
        for result in results
    ]
