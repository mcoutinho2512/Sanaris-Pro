"""
Modelos para Faturamento TISS
Padrão ANS (Agência Nacional de Saúde Suplementar)
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Numeric, Integer, Enum as SQLEnum, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.core.database import Base
import uuid
import enum


# ============================================
# ENUMS
# ============================================

class HealthInsuranceType(enum.Enum):
    """Tipo de operadora"""
    MEDICAL = "medical"  # Medicina de grupo
    COOPERATIVE = "cooperative"  # Cooperativa médica
    PHILANTHROPIC = "philanthropic"  # Filantropia
    SELF_MANAGEMENT = "self_management"  # Autogestão


class GuideType(enum.Enum):
    """Tipo de guia TISS"""
    CONSULTATION = "consultation"  # Consulta
    SADT = "sadt"  # SP/SADT (Serviços Profissionais / Serviços Auxiliares de Diagnose e Terapia)
    HOSPITALIZATION = "hospitalization"  # Internação
    HONORARIUM = "honorarium"  # Honorários Individuais
    RESUME = "resume"  # Resumo de Internação


class GuideStatus(enum.Enum):
    """Status da guia"""
    DRAFT = "draft"  # Em digitação
    PENDING = "pending"  # Pendente de envio
    SENT = "sent"  # Enviada
    ACCEPTED = "accepted"  # Aceita pela operadora
    REJECTED = "rejected"  # Rejeitada
    PAID = "paid"  # Paga
    GLOSS = "gloss"  # Glosada (negada)


class BatchStatus(enum.Enum):
    """Status do lote"""
    OPEN = "open"  # Aberto (em digitação)
    CLOSED = "closed"  # Fechado (pronto para envio)
    SENT = "sent"  # Enviado
    PROCESSED = "processed"  # Processado pela operadora


class ProcedureType(enum.Enum):
    """Tipo de procedimento TUSS"""
    CONSULTATION = "consultation"  # Consulta
    EXAM = "exam"  # Exame
    THERAPY = "therapy"  # Terapia
    SURGERY = "surgery"  # Cirurgia
    HOSPITALIZATION = "hospitalization"  # Internação
    OTHER = "other"  # Outros


# ============================================
# OPERADORAS
# ============================================

class HealthInsuranceOperator(Base):
    """Operadoras de planos de saúde"""
    __tablename__ = "health_insurance_operators"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    name = Column(String(255), nullable=False)
    commercial_name = Column(String(255))
    ans_code = Column(String(6), nullable=False, unique=True)  # Registro ANS (6 dígitos)
    
    # Tipo
    operator_type = Column(SQLEnum(HealthInsuranceType), nullable=False)
    
    # Contato
    cnpj = Column(String(18))
    phone = Column(String(20))
    email = Column(String(255))
    
    # Endereço
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(2))
    zipcode = Column(String(10))
    
    # Configurações TISS
    tiss_version = Column(String(10), default="4.03.00")  # Versão do padrão TISS
    accepts_electronic_guide = Column(Boolean, default=True)
    requires_authorization = Column(Boolean, default=False)
    
    # Dados bancários
    bank_code = Column(String(10))
    agency = Column(String(20))
    account_number = Column(String(30))
    
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
        return f"<HealthInsuranceOperator {self.name}>"


# ============================================
# PROCEDIMENTOS TUSS
# ============================================

class TussProcedure(Base):
    """Tabela TUSS - Procedimentos"""
    __tablename__ = "tuss_procedures"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    code = Column(String(10), nullable=False, unique=True, index=True)  # Código TUSS
    description = Column(Text, nullable=False)
    
    # Tipo
    procedure_type = Column(SQLEnum(ProcedureType), nullable=False)
    
    # Valores
    default_value = Column(Numeric(10, 2))  # Valor padrão
    
    # Configurações
    requires_authorization = Column(Boolean, default=False)
    quantity_limit = Column(Integer)  # Limite de quantidade por período
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TussProcedure {self.code}>"


# ============================================
# BENEFICIÁRIOS
# ============================================

class Beneficiary(Base):
    """Beneficiários de planos de saúde"""
    __tablename__ = "beneficiaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Paciente
    patient_id = Column(String(36), nullable=False, index=True)
    
    # Operadora
    operator_id = Column(String(36), nullable=False, index=True)
    
    # Carteirinha
    card_number = Column(String(20), nullable=False, index=True)  # Número da carteirinha
    registration_number = Column(String(20))  # Número de matrícula/inscrição
    
    # Plano
    plan_name = Column(String(255))
    plan_code = Column(String(20))
    
    # Validade
    validity_start = Column(Date)
    validity_end = Column(Date)
    
    # Titular
    is_holder = Column(Boolean, default=True)  # É titular ou dependente
    holder_name = Column(String(255))  # Nome do titular (se dependente)
    holder_cpf = Column(String(14))
    
    # CNS (Cartão Nacional de Saúde)
    cns = Column(String(15))
    
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
        return f"<Beneficiary {self.card_number}>"


# ============================================
# LOTES TISS
# ============================================

class TissBatch(Base):
    """Lotes de guias TISS"""
    __tablename__ = "tiss_batches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    batch_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Operadora
    operator_id = Column(String(36), nullable=False, index=True)
    
    # Período
    reference_month = Column(Integer, nullable=False)
    reference_year = Column(Integer, nullable=False)
    
    # Sequencial ANS
    ans_sequence = Column(String(12))  # Número sequencial do prestador na ANS
    
    # Valores
    total_value = Column(Numeric(10, 2), default=0)
    total_guides = Column(Integer, default=0)
    
    # Status
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.OPEN)
    
    # Datas
    closed_at = Column(DateTime)  # Data de fechamento
    sent_at = Column(DateTime)  # Data de envio
    processed_at = Column(DateTime)  # Data de processamento
    
    # Arquivo XML
    xml_file_url = Column(String(500))
    
    # Notas
    notes = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TissBatch {self.batch_number}>"


# ============================================
# GUIAS TISS
# ============================================

class TissGuide(Base):
    """Guias TISS"""
    __tablename__ = "tiss_guides"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Identificação
    guide_number = Column(String(20), unique=True, nullable=False, index=True)
    guide_type = Column(SQLEnum(GuideType), nullable=False)
    
    # Lote
    batch_id = Column(String(36), index=True)
    
    # Operadora e Beneficiário
    operator_id = Column(String(36), nullable=False, index=True)
    beneficiary_id = Column(String(36), nullable=False, index=True)
    
    # Prestador
    healthcare_professional_id = Column(String(36), nullable=False, index=True)
    
    # Atendimento
    appointment_id = Column(String(36), index=True)
    medical_record_id = Column(String(36), index=True)
    
    # Datas
    service_date = Column(DateTime, nullable=False)  # Data do atendimento
    issue_date = Column(DateTime, default=datetime.utcnow)  # Data de emissão
    
    # Autorização
    authorization_number = Column(String(20))  # Número da autorização prévia
    authorization_date = Column(Date)
    
    # Valores
    total_value = Column(Numeric(10, 2), nullable=False)
    accepted_value = Column(Numeric(10, 2))  # Valor aceito pela operadora
    gloss_value = Column(Numeric(10, 2), default=0)  # Valor glosado
    
    # Status
    status = Column(SQLEnum(GuideStatus), default=GuideStatus.DRAFT)
    
    # Glosa
    gloss_reason = Column(Text)  # Motivo da glosa
    gloss_date = Column(DateTime)
    
    # CID (Classificação Internacional de Doenças)
    cid_code = Column(String(10))  # CID-10
    
    # Indicação clínica
    clinical_indication = Column(Text)
    
    # Observações
    observations = Column(Text)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TissGuide {self.guide_number}>"


# ============================================
# PROCEDIMENTOS DA GUIA
# ============================================

class TissGuideProcedure(Base):
    """Procedimentos de uma guia TISS"""
    __tablename__ = "tiss_guide_procedures"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Guia
    guide_id = Column(String(36), nullable=False, index=True)
    
    # Procedimento
    procedure_id = Column(String(36), nullable=False, index=True)  # ID do TussProcedure
    procedure_code = Column(String(10), nullable=False)  # Código TUSS
    procedure_description = Column(Text)
    
    # Quantidade
    quantity = Column(Integer, default=1)
    
    # Valores
    unit_value = Column(Numeric(10, 2), nullable=False)
    total_value = Column(Numeric(10, 2), nullable=False)
    
    # Glosa
    gloss_value = Column(Numeric(10, 2), default=0)
    gloss_reason = Column(Text)
    
    # Data de execução
    execution_date = Column(Date)
    
    # Via de acesso (para cirurgias)
    access_route = Column(String(2))  # Código da via de acesso
    
    # Técnica utilizada (para cirurgias)
    technique = Column(String(2))  # Código da técnica
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TissGuideProcedure {self.procedure_code}>"
