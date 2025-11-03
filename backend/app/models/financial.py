"""
Sistema de Gestão Financeira
Contas a Receber
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid
import enum


class PaymentStatus(enum.Enum):
    """Status de pagamento"""
    PENDING = "pending"  # Pendente
    PAID = "paid"  # Pago
    OVERDUE = "overdue"  # Vencido
    PARTIALLY_PAID = "partially_paid"  # Parcialmente pago
    CANCELLED = "cancelled"  # Cancelado
    REFUNDED = "refunded"  # Estornado


class PaymentMethodType(enum.Enum):
    """Formas de pagamento"""
    CASH = "cash"  # Dinheiro
    CREDIT_CARD = "credit_card"  # Cartão de crédito
    DEBIT_CARD = "debit_card"  # Cartão de débito
    PIX = "pix"  # PIX
    BANK_SLIP = "bank_slip"  # Boleto
    CHECK = "check"  # Cheque
    TRANSFER = "transfer"  # Transferência
    INSURANCE = "insurance"  # Convênio


class RecurrenceType(enum.Enum):
    """Tipos de recorrência"""
    NONE = "none"  # Sem recorrência
    MONTHLY = "monthly"  # Mensal
    BIMONTHLY = "bimonthly"  # Bimestral
    QUARTERLY = "quarterly"  # Trimestral
    SEMIANNUAL = "semiannual"  # Semestral
    ANNUAL = "annual"  # Anual


class AccountReceivable(Base):
    """Conta a receber principal"""
    __tablename__ = "accounts_receivable"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    invoice_number = Column(String(50), unique=True, index=True)  # Número da fatura
    description = Column(Text, nullable=False)  # Descrição do serviço
    
    # Relacionamentos
    patient_id = Column(String(36), nullable=False, index=True)
    healthcare_professional_id = Column(String(36), index=True)
    appointment_id = Column(String(36), index=True)  # Se vier de agendamento
    
    # Valores
    original_amount = Column(Numeric(10, 2), nullable=False)  # Valor original
    discount_amount = Column(Numeric(10, 2), default=0)  # Desconto
    interest_amount = Column(Numeric(10, 2), default=0)  # Juros
    fine_amount = Column(Numeric(10, 2), default=0)  # Multa
    total_amount = Column(Numeric(10, 2), nullable=False)  # Valor total
    paid_amount = Column(Numeric(10, 2), default=0)  # Valor pago
    remaining_amount = Column(Numeric(10, 2))  # Valor restante
    
    # Datas
    issue_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Emissão
    due_date = Column(DateTime, nullable=False)  # Vencimento
    payment_date = Column(DateTime)  # Pagamento
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    
    # Parcelamento
    total_installments = Column(Integer, default=1)  # Total de parcelas
    current_installment = Column(Integer, default=1)  # Parcela atual
    
    # Recorrência
    is_recurring = Column(Boolean, default=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE)
    recurrence_day = Column(Integer)  # Dia do mês para recorrência
    
    # Configurações de cobrança
    charge_interest = Column(Boolean, default=True)  # Cobrar juros
    interest_rate_daily = Column(Numeric(5, 2), default=0.033)  # 1% ao mês (0.033% ao dia)
    charge_fine = Column(Boolean, default=True)  # Cobrar multa
    fine_rate = Column(Numeric(5, 2), default=2.0)  # 2% de multa
    
    # Notas e documentos
    invoice_url = Column(String(500))  # URL da nota fiscal
    receipt_url = Column(String(500))  # URL do comprovante
    notes = Column(Text)  # Observações
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AccountReceivable {self.invoice_number}>"


class PaymentInstallment(Base):
    """Parcelas de pagamento"""
    __tablename__ = "payment_installments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamento
    account_receivable_id = Column(String(36), nullable=False, index=True)
    
    # Identificação
    installment_number = Column(Integer, nullable=False)  # Número da parcela
    
    # Valores
    original_amount = Column(Numeric(10, 2), nullable=False)
    interest_amount = Column(Numeric(10, 2), default=0)
    fine_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    
    # Datas
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PaymentInstallment {self.installment_number}>"


class PaymentTransaction(Base):
    """Transações de pagamento"""
    __tablename__ = "payment_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamentos
    account_receivable_id = Column(String(36), nullable=False, index=True)
    installment_id = Column(String(36), index=True)  # Null se pagamento à vista
    
    # Identificação
    transaction_number = Column(String(100), unique=True)
    
    # Pagamento
    payment_method = Column(SQLEnum(PaymentMethodType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Detalhes específicos do método
    card_brand = Column(String(50))  # Visa, Master, etc
    card_last_digits = Column(String(4))
    pix_key = Column(String(255))
    pix_txid = Column(String(100))
    check_number = Column(String(50))
    bank_slip_barcode = Column(String(100))
    
    # Aprovação
    authorization_code = Column(String(100))
    nsu = Column(String(100))  # Número sequencial único
    
    # Status
    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime)
    
    # Estorno
    is_refunded = Column(Boolean, default=False)
    refund_date = Column(DateTime)
    refund_reason = Column(Text)
    
    # Comprovante
    receipt_url = Column(String(500))
    
    # Metadados
    notes = Column(Text)
    
    # Timestamps
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PaymentTransaction {self.transaction_number}>"
