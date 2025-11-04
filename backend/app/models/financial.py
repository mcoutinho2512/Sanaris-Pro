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


# ============================================
# FORNECEDORES
# ============================================

class Supplier(Base):
    """Fornecedores e prestadores de serviço"""
    __tablename__ = "suppliers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255))  # Razão social
    document_type = Column(String(10), nullable=False)  # CPF ou CNPJ
    document_number = Column(String(18), nullable=False, unique=True)
    
    # Contato
    contact_person = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    
    # Endereço
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))
    zipcode = Column(String(10))
    
    # Dados bancários
    bank_name = Column(String(100))
    bank_code = Column(String(10))
    agency = Column(String(20))
    account_number = Column(String(30))
    account_type = Column(String(20))  # corrente, poupança
    pix_key = Column(String(255))
    
    # Categoria
    category = Column(String(100))  # laboratório, material, serviço, etc
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Notas
    notes = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Supplier {self.name}>"


class ExpenseCategory(Base):
    """Categorias de despesas"""
    __tablename__ = "expense_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Hierarquia
    parent_id = Column(String(36))  # Categoria pai para subcategorias
    
    # Configuração
    is_active = Column(Boolean, default=True)
    color = Column(String(7))  # Cor hexadecimal para gráficos
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExpenseCategory {self.name}>"


class CostCenter(Base):
    """Centros de custo"""
    __tablename__ = "cost_centers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Responsável
    manager_id = Column(String(36))  # ID do profissional responsável
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CostCenter {self.code} - {self.name}>"


class AccountPayable(Base):
    """Conta a pagar"""
    __tablename__ = "accounts_payable"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    bill_number = Column(String(50), unique=True, index=True)  # Número da conta
    description = Column(Text, nullable=False)
    
    # Fornecedor
    supplier_id = Column(String(36), nullable=False, index=True)
    
    # Categorização
    expense_category_id = Column(String(36), nullable=False, index=True)
    cost_center_id = Column(String(36), index=True)
    
    # Valores
    original_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    interest_amount = Column(Numeric(10, 2), default=0)
    fine_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)
    remaining_amount = Column(Numeric(10, 2))
    
    # Datas
    issue_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    
    # Aprovação
    requires_approval = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String(36))  # ID do aprovador
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Parcelamento
    total_installments = Column(Integer, default=1)
    current_installment = Column(Integer, default=1)
    
    # Recorrência
    is_recurring = Column(Boolean, default=False)
    recurrence_type = Column(SQLEnum(RecurrenceType), default=RecurrenceType.NONE)
    
    # Documentos
    invoice_url = Column(String(500))
    receipt_url = Column(String(500))
    
    # Notas
    notes = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AccountPayable {self.bill_number}>"


class PayableTransaction(Base):
    """Transações de pagamento de contas a pagar"""
    __tablename__ = "payable_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamento
    account_payable_id = Column(String(36), nullable=False, index=True)
    
    # Identificação
    transaction_number = Column(String(100), unique=True)
    
    # Pagamento
    payment_method = Column(SQLEnum(PaymentMethodType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    
    # Detalhes específicos
    pix_key = Column(String(255))
    pix_txid = Column(String(100))
    bank_slip_barcode = Column(String(100))
    transfer_code = Column(String(100))
    
    # Aprovação
    authorization_code = Column(String(100))
    
    # Status
    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime)
    
    # Comprovante
    receipt_url = Column(String(500))
    
    # Notas
    notes = Column(Text)
    
    # Timestamps
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PayableTransaction {self.transaction_number}>"


# ============================================
# REPASSE PROFISSIONAIS
# ============================================

class ProfessionalFeeType(enum.Enum):
    """Tipo de repasse"""
    PERCENTAGE = "percentage"  # Percentual sobre receita
    FIXED = "fixed"  # Valor fixo por atendimento


class ProfessionalFeeConfiguration(Base):
    """Configuração de repasse por profissional"""
    __tablename__ = "professional_fee_configurations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Profissional
    healthcare_professional_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Tipo de repasse
    fee_type = Column(SQLEnum(ProfessionalFeeType), nullable=False, default=ProfessionalFeeType.PERCENTAGE)
    
    # Valores
    percentage = Column(Numeric(5, 2))  # Ex: 40.00 para 40%
    fixed_amount = Column(Numeric(10, 2))  # Valor fixo por atendimento
    
    # Retenções
    apply_inss = Column(Boolean, default=False)
    inss_rate = Column(Numeric(5, 2), default=11.0)  # 11%
    
    apply_ir = Column(Boolean, default=False)
    ir_rate = Column(Numeric(5, 2), default=0)  # Variável
    
    apply_iss = Column(Boolean, default=False)
    iss_rate = Column(Numeric(5, 2), default=0)  # Variável por cidade
    
    other_deductions = Column(Numeric(10, 2), default=0)  # Outras deduções
    
    # Configuração
    minimum_amount = Column(Numeric(10, 2))  # Valor mínimo para gerar repasse
    payment_day = Column(Integer)  # Dia do mês para pagamento (1-31)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Notas
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalFeeConfig {self.healthcare_professional_id}>"


class ProfessionalFee(Base):
    """Repasse gerado para profissional"""
    __tablename__ = "professional_fees"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    fee_number = Column(String(50), unique=True, index=True)
    
    # Profissional
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Período
    reference_month = Column(Integer, nullable=False)  # 1-12
    reference_year = Column(Integer, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Valores
    gross_amount = Column(Numeric(10, 2), nullable=False)  # Valor bruto
    inss_amount = Column(Numeric(10, 2), default=0)
    ir_amount = Column(Numeric(10, 2), default=0)
    iss_amount = Column(Numeric(10, 2), default=0)
    other_deductions = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)  # Valor líquido
    
    # Estatísticas
    total_appointments = Column(Integer, default=0)  # Total de atendimentos
    total_revenue = Column(Numeric(10, 2), default=0)  # Receita total gerada
    
    # Status
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Pagamento
    payment_date = Column(DateTime)
    payment_method = Column(SQLEnum(PaymentMethodType))
    payment_reference = Column(String(100))  # Referência do pagamento
    
    # Documentos
    receipt_url = Column(String(500))
    
    # Notas
    notes = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalFee {self.fee_number}>"


class ProfessionalFeeItem(Base):
    """Itens do repasse (detalhamento por atendimento)"""
    __tablename__ = "professional_fee_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relacionamento
    professional_fee_id = Column(String(36), nullable=False, index=True)
    
    # Referência
    account_receivable_id = Column(String(36), index=True)  # Conta que gerou o repasse
    appointment_id = Column(String(36), index=True)  # Atendimento relacionado
    
    # Descrição
    description = Column(Text)
    
    # Valores
    service_amount = Column(Numeric(10, 2), nullable=False)  # Valor do serviço
    fee_amount = Column(Numeric(10, 2), nullable=False)  # Valor do repasse
    
    # Data
    service_date = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalFeeItem {self.id}>"
