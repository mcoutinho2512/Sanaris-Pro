"""
Schemas para Gestão Financeira
Contas a Receber
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================
# ENUMS
# ============================================

class PaymentStatusEnum(str, Enum):
    """Status de pagamento"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethodEnum(str, Enum):
    """Formas de pagamento"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    BANK_SLIP = "bank_slip"
    CHECK = "check"
    TRANSFER = "transfer"
    INSURANCE = "insurance"


class RecurrenceTypeEnum(str, Enum):
    """Tipos de recorrência"""
    NONE = "none"
    MONTHLY = "monthly"
    BIMONTHLY = "bimonthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"


# ============================================
# CONTAS A RECEBER
# ============================================

class AccountReceivableBase(BaseModel):
    """Schema base de conta a receber"""
    description: str = Field(..., min_length=1, max_length=1000)
    patient_id: str
    healthcare_professional_id: Optional[str] = None
    appointment_id: Optional[str] = None
    original_amount: Decimal = Field(..., gt=0)
    discount_amount: Decimal = Field(0, ge=0)
    due_date: datetime
    total_installments: int = Field(1, ge=1, le=12)
    is_recurring: bool = False
    recurrence_type: RecurrenceTypeEnum = RecurrenceTypeEnum.NONE
    recurrence_day: Optional[int] = Field(None, ge=1, le=31)
    charge_interest: bool = True
    interest_rate_daily: Decimal = Field(0.033, ge=0, le=100, decimal_places=3)
    charge_fine: bool = True
    fine_rate: Decimal = Field(2.0, ge=0, le=100)
    notes: Optional[str] = None


class AccountReceivableCreate(AccountReceivableBase):
    """Schema para criação"""
    pass


class AccountReceivableUpdate(BaseModel):
    """Schema para atualização"""
    description: Optional[str] = None
    healthcare_professional_id: Optional[str] = None
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    charge_interest: Optional[bool] = None
    charge_fine: Optional[bool] = None
    notes: Optional[str] = None


class AccountReceivableResponse(BaseModel):
    """Schema de resposta"""
    id: str
    invoice_number: str
    description: str
    patient_id: str
    healthcare_professional_id: Optional[str] = None
    appointment_id: Optional[str] = None
    original_amount: Decimal
    discount_amount: Decimal
    interest_amount: Decimal
    fine_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    issue_date: datetime
    due_date: datetime
    payment_date: Optional[datetime] = None
    status: str
    total_installments: int
    current_installment: int
    is_recurring: bool
    recurrence_type: str
    recurrence_day: Optional[int] = None
    charge_interest: bool
    interest_rate_daily: Decimal
    charge_fine: bool
    fine_rate: Decimal
    invoice_url: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountReceivableListResponse(BaseModel):
    """Schema de lista simplificada"""
    id: str
    invoice_number: str
    description: str
    patient_id: str
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    due_date: datetime
    payment_date: Optional[datetime] = None
    status: str
    total_installments: int
    current_installment: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# PARCELAS
# ============================================

class PaymentInstallmentResponse(BaseModel):
    """Schema de parcela"""
    id: str
    account_receivable_id: str
    installment_number: int
    original_amount: Decimal
    interest_amount: Decimal
    fine_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    due_date: datetime
    payment_date: Optional[datetime] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# TRANSAÇÕES DE PAGAMENTO
# ============================================

class PaymentTransactionBase(BaseModel):
    """Schema base de transação"""
    account_receivable_id: str
    installment_id: Optional[str] = None
    payment_method: PaymentMethodEnum
    amount: Decimal = Field(..., gt=0)
    card_brand: Optional[str] = None
    card_last_digits: Optional[str] = Field(None, min_length=4, max_length=4)
    pix_key: Optional[str] = None
    pix_txid: Optional[str] = None
    check_number: Optional[str] = None
    bank_slip_barcode: Optional[str] = None
    authorization_code: Optional[str] = None
    nsu: Optional[str] = None
    notes: Optional[str] = None


class PaymentTransactionCreate(PaymentTransactionBase):
    """Schema para criação de transação"""
    payment_date: Optional[datetime] = None


class PaymentTransactionResponse(BaseModel):
    """Schema de resposta"""
    id: str
    account_receivable_id: str
    installment_id: Optional[str] = None
    transaction_number: str
    payment_method: str
    amount: Decimal
    card_brand: Optional[str] = None
    card_last_digits: Optional[str] = None
    pix_key: Optional[str] = None
    pix_txid: Optional[str] = None
    check_number: Optional[str] = None
    bank_slip_barcode: Optional[str] = None
    authorization_code: Optional[str] = None
    nsu: Optional[str] = None
    is_confirmed: bool
    confirmed_at: Optional[datetime] = None
    is_refunded: bool
    refund_date: Optional[datetime] = None
    refund_reason: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    payment_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# AÇÕES ESPECIAIS
# ============================================

class ConfirmPaymentRequest(BaseModel):
    """Request para confirmar pagamento"""
    transaction_id: str
    confirmed_at: Optional[datetime] = None


class RefundPaymentRequest(BaseModel):
    """Request para estornar pagamento"""
    transaction_id: str
    refund_reason: str = Field(..., min_length=1)
    refund_date: Optional[datetime] = None


class CancelAccountRequest(BaseModel):
    """Request para cancelar conta"""
    account_id: str
    reason: str = Field(..., min_length=1)


# ============================================
# RELATÓRIOS
# ============================================

class FinancialSummary(BaseModel):
    """Resumo financeiro"""
    total_pending: Decimal
    total_paid: Decimal
    total_overdue: Decimal
    total_cancelled: Decimal
    count_pending: int
    count_paid: int
    count_overdue: int
    count_cancelled: int


class PaymentMethodSummary(BaseModel):
    """Resumo por forma de pagamento"""
    payment_method: str
    total_amount: Decimal
    count: int


class DailyRevenue(BaseModel):
    """Receita diária"""
    date: date
    total_amount: Decimal
    count: int


class MonthlyRevenue(BaseModel):
    """Receita mensal"""
    year: int
    month: int
    total_amount: Decimal
    count: int


# ============================================
# FILTROS
# ============================================

class AccountReceivableFilters(BaseModel):
    """Filtros de busca"""
    patient_id: Optional[str] = None
    professional_id: Optional[str] = None
    status: Optional[PaymentStatusEnum] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    is_overdue: Optional[bool] = None
    payment_method: Optional[PaymentMethodEnum] = None


# ============================================
# LABELS EM PORTUGUÊS
# ============================================

PAYMENT_STATUS_LABELS = {
    "pending": "Pendente",
    "paid": "Pago",
    "overdue": "Vencido",
    "partially_paid": "Parcialmente Pago",
    "cancelled": "Cancelado",
    "refunded": "Estornado"
}

PAYMENT_METHOD_LABELS = {
    "cash": "Dinheiro",
    "credit_card": "Cartão de Crédito",
    "debit_card": "Cartão de Débito",
    "pix": "PIX",
    "bank_slip": "Boleto",
    "check": "Cheque",
    "transfer": "Transferência",
    "insurance": "Convênio"
}

RECURRENCE_TYPE_LABELS = {
    "none": "Sem Recorrência",
    "monthly": "Mensal",
    "bimonthly": "Bimestral",
    "quarterly": "Trimestral",
    "semiannual": "Semestral",
    "annual": "Anual"
}
