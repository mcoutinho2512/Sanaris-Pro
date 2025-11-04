"""
Rotas de Contas a Pagar
Gestão de Fornecedores e Despesas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.financial import (
    Supplier, ExpenseCategory, CostCenter,
    AccountPayable, PayableTransaction,
    PaymentStatus, PaymentMethodType, RecurrenceType
)
from app.schemas.financial import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    ExpenseCategoryCreate, ExpenseCategoryResponse,
    CostCenterCreate, CostCenterResponse,
    AccountPayableCreate, AccountPayableUpdate, AccountPayableResponse,
    AccountPayableListResponse,
    PayableTransactionCreate, PayableTransactionResponse,
    ApproveAccountRequest,
    PaymentStatusEnum, PaymentMethodEnum
)
from app.services.financial_service import financial_service

router = APIRouter(prefix="/api/v1/financial/payables", tags=["Contas a Pagar"])


# ============================================
# FORNECEDORES
# ============================================

@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier_data: SupplierCreate, db: Session = Depends(get_db)):
    """Cadastra fornecedor"""
    
    # Verifica duplicidade
    existing = db.query(Supplier).filter(
        Supplier.document_number == supplier_data.document_number,
        Supplier.is_deleted == False
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fornecedor com este documento já cadastrado"
        )
    
    supplier = Supplier(**supplier_data.dict())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    return supplier


@router.get("/suppliers", response_model=List[SupplierResponse])
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista fornecedores"""
    
    query = db.query(Supplier).filter(Supplier.is_deleted == False)
    
    if category:
        query = query.filter(Supplier.category == category)
    
    if is_active is not None:
        query = query.filter(Supplier.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Supplier.name.ilike(search_term)) |
            (Supplier.document_number.ilike(search_term))
        )
    
    suppliers = query.order_by(Supplier.name).offset(skip).limit(limit).all()
    
    return suppliers


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    """Busca fornecedor por ID"""
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.is_deleted == False
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza fornecedor"""
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.is_deleted == False
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    update_data = supplier_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    db.commit()
    db.refresh(supplier)
    
    return supplier


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: str, db: Session = Depends(get_db)):
    """Deleta fornecedor (soft delete)"""
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.is_deleted == False
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    supplier.is_deleted = True
    supplier.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Fornecedor deletado com sucesso", "success": True}


# ============================================
# CATEGORIAS DE DESPESAS
# ============================================

@router.post("/categories", response_model=ExpenseCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_expense_category(category_data: ExpenseCategoryCreate, db: Session = Depends(get_db)):
    """Cria categoria de despesa"""
    
    # Verifica duplicidade
    existing = db.query(ExpenseCategory).filter(ExpenseCategory.name == category_data.name).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria já existe"
        )
    
    category = ExpenseCategory(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.get("/categories", response_model=List[ExpenseCategoryResponse])
def list_expense_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista categorias de despesas"""
    
    query = db.query(ExpenseCategory)
    
    if is_active is not None:
        query = query.filter(ExpenseCategory.is_active == is_active)
    
    categories = query.order_by(ExpenseCategory.name).offset(skip).limit(limit).all()
    
    return categories


@router.get("/categories/{category_id}", response_model=ExpenseCategoryResponse)
def get_expense_category(category_id: str, db: Session = Depends(get_db)):
    """Busca categoria por ID"""
    
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    return category


# ============================================
# CENTROS DE CUSTO
# ============================================

@router.post("/cost-centers", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED)
def create_cost_center(cost_center_data: CostCenterCreate, db: Session = Depends(get_db)):
    """Cria centro de custo"""
    
    # Verifica duplicidade
    existing = db.query(CostCenter).filter(CostCenter.code == cost_center_data.code).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Centro de custo com este código já existe"
        )
    
    cost_center = CostCenter(**cost_center_data.dict())
    db.add(cost_center)
    db.commit()
    db.refresh(cost_center)
    
    return cost_center


@router.get("/cost-centers", response_model=List[CostCenterResponse])
def list_cost_centers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista centros de custo"""
    
    query = db.query(CostCenter)
    
    if is_active is not None:
        query = query.filter(CostCenter.is_active == is_active)
    
    cost_centers = query.order_by(CostCenter.code).offset(skip).limit(limit).all()
    
    return cost_centers


# ============================================
# CONTAS A PAGAR - CRUD
# ============================================

@router.post("", response_model=AccountPayableResponse, status_code=status.HTTP_201_CREATED)
def create_account_payable(account_data: AccountPayableCreate, db: Session = Depends(get_db)):
    """Cria conta a pagar"""
    
    # Valida fornecedor
    supplier = db.query(Supplier).filter(
        Supplier.id == account_data.supplier_id,
        Supplier.is_deleted == False
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    # Valida categoria
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.id == account_data.expense_category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada"
        )
    
    # Gera número da conta
    bill_number = financial_service.generate_invoice_number(prefix="DESP")
    
    # Calcula valores
    total_amount = financial_service.calculate_total_amount(
        original_amount=account_data.original_amount,
        discount_amount=account_data.discount_amount
    )
    
    remaining_amount = total_amount
    
    # Cria conta
    account = AccountPayable(
        bill_number=bill_number,
        description=account_data.description,
        supplier_id=account_data.supplier_id,
        expense_category_id=account_data.expense_category_id,
        cost_center_id=account_data.cost_center_id,
        original_amount=account_data.original_amount,
        discount_amount=account_data.discount_amount,
        total_amount=total_amount,
        remaining_amount=remaining_amount,
        due_date=account_data.due_date,
        total_installments=account_data.total_installments,
        is_recurring=account_data.is_recurring,
        recurrence_type=account_data.recurrence_type.value,
        requires_approval=account_data.requires_approval,
        notes=account_data.notes
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.get("", response_model=List[AccountPayableListResponse])
def list_accounts_payable(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    supplier_id: Optional[str] = None,
    category_id: Optional[str] = None,
    cost_center_id: Optional[str] = None,
    status: Optional[PaymentStatusEnum] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    pending_approval: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista contas a pagar com filtros"""
    
    query = db.query(AccountPayable).filter(AccountPayable.is_deleted == False)
    
    if supplier_id:
        query = query.filter(AccountPayable.supplier_id == supplier_id)
    
    if category_id:
        query = query.filter(AccountPayable.expense_category_id == category_id)
    
    if cost_center_id:
        query = query.filter(AccountPayable.cost_center_id == cost_center_id)
    
    if status:
        query = query.filter(AccountPayable.status == status.value)
    
    if date_from:
        query = query.filter(AccountPayable.due_date >= date_from)
    
    if date_to:
        query = query.filter(AccountPayable.due_date <= date_to)
    
    if pending_approval is not None:
        if pending_approval:
            query = query.filter(
                AccountPayable.requires_approval == True,
                AccountPayable.is_approved == False
            )
    
    accounts = query.order_by(desc(AccountPayable.created_at)).offset(skip).limit(limit).all()
    
    return accounts


@router.get("/{account_id}", response_model=AccountPayableResponse)
def get_account_payable(account_id: str, db: Session = Depends(get_db)):
    """Busca conta a pagar por ID"""
    
    account = db.query(AccountPayable).filter(
        AccountPayable.id == account_id,
        AccountPayable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    return account


@router.put("/{account_id}", response_model=AccountPayableResponse)
def update_account_payable(
    account_id: str,
    account_data: AccountPayableUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza conta a pagar"""
    
    account = db.query(AccountPayable).filter(
        AccountPayable.id == account_id,
        AccountPayable.is_deleted == False
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
            update_data['discount_amount']
        )
        account.remaining_amount = account.total_amount - account.paid_amount
    
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}")
def delete_account_payable(account_id: str, db: Session = Depends(get_db)):
    """Deleta conta a pagar (soft delete)"""
    
    account = db.query(AccountPayable).filter(
        AccountPayable.id == account_id,
        AccountPayable.is_deleted == False
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


# ============================================
# APROVAÇÃO DE CONTAS
# ============================================

@router.post("/approve")
def approve_account(approve_data: ApproveAccountRequest, db: Session = Depends(get_db)):
    """Aprova ou rejeita conta a pagar"""
    
    account = db.query(AccountPayable).filter(
        AccountPayable.id == approve_data.account_id,
        AccountPayable.is_deleted == False
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conta não encontrada"
        )
    
    if not account.requires_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta conta não requer aprovação"
        )
    
    account.is_approved = approve_data.approved
    account.approved_at = datetime.utcnow()
    account.approval_notes = approve_data.approval_notes
    
    if not approve_data.approved:
        account.status = PaymentStatus.CANCELLED.value
    
    db.commit()
    
    message = "Conta aprovada" if approve_data.approved else "Conta rejeitada"
    
    return {"message": f"{message} com sucesso", "success": True}


# ============================================
# TRANSAÇÕES DE PAGAMENTO
# ============================================

@router.post("/payments", response_model=PayableTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_payable_transaction(payment_data: PayableTransactionCreate, db: Session = Depends(get_db)):
    """Registra pagamento de conta"""
    
    # Busca conta
    account = db.query(AccountPayable).filter(
        AccountPayable.id == payment_data.account_payable_id
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
    
    if account.requires_approval and not account.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conta precisa ser aprovada antes do pagamento"
        )
    
    # Valida valor
    if payment_data.amount > account.remaining_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor do pagamento ({payment_data.amount}) maior que saldo devedor ({account.remaining_amount})"
        )
    
    # Gera número de transação
    transaction_number = financial_service.generate_transaction_number(prefix="PGTO")
    
    # Cria transação
    transaction = PayableTransaction(
        account_payable_id=payment_data.account_payable_id,
        transaction_number=transaction_number,
        payment_method=payment_data.payment_method.value,
        amount=payment_data.amount,
        pix_key=payment_data.pix_key,
        pix_txid=payment_data.pix_txid,
        bank_slip_barcode=payment_data.bank_slip_barcode,
        transfer_code=payment_data.transfer_code,
        authorization_code=payment_data.authorization_code,
        notes=payment_data.notes,
        payment_date=payment_data.payment_date or datetime.utcnow(),
        is_confirmed=True,
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


@router.get("/payments", response_model=List[PayableTransactionResponse])
def list_payable_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    account_id: Optional[str] = None,
    payment_method: Optional[PaymentMethodEnum] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Lista transações de pagamento"""
    
    query = db.query(PayableTransaction)
    
    if account_id:
        query = query.filter(PayableTransaction.account_payable_id == account_id)
    
    if payment_method:
        query = query.filter(PayableTransaction.payment_method == payment_method.value)
    
    if date_from:
        query = query.filter(PayableTransaction.payment_date >= date_from)
    
    if date_to:
        query = query.filter(PayableTransaction.payment_date <= date_to)
    
    transactions = query.order_by(desc(PayableTransaction.payment_date)).offset(skip).limit(limit).all()
    
    return transactions
