"""
Schemas Pydantic para Gestão Financeira
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class AccountReceivableBase(BaseModel):
    description: str = Field(..., min_length=3, max_length=500)
    patient_id: str
    healthcare_professional_id: Optional[str] = None
    appointment_id: Optional[str] = None
    original_amount: Decimal = Field(..., gt=0)
    discount_amount: Optional[Decimal] = Field(default=0, ge=0)
    interest_amount: Optional[Decimal] = Field(default=0, ge=0)
    fine_amount: Optional[Decimal] = Field(default=0, ge=0)
    due_date: datetime
    total_installments: Optional[int] = Field(default=1, ge=1, le=12)
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class AccountReceivableCreate(AccountReceivableBase):
    pass

class AccountReceivableUpdate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    discount_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class AccountReceivableResponse(BaseModel):
    id: str
    invoice_number: str
    description: str
    patient_id: str
    patient_name: Optional[str] = None
    healthcare_professional_id: Optional[str] = None
    professional_name: Optional[str] = None
    original_amount: Decimal
    discount_amount: Decimal
    interest_amount: Decimal
    fine_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Optional[Decimal] = None
    issue_date: datetime
    due_date: datetime
    payment_date: Optional[datetime] = None
    status: str
    total_installments: int
    current_installment: int
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    account_id: str
    amount: Decimal = Field(..., gt=0)
    payment_method: str
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None

class FinancialSummary(BaseModel):
    total_receivable: Decimal
    total_received: Decimal
    total_pending: Decimal
    total_overdue: Decimal
    pending_count: int
    overdue_count: int
    paid_count: int
