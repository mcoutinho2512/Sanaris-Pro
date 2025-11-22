from sqlalchemy import Column, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class Prestador(Base):
    """Prestadores de serviço (médicos, clínicas, laboratórios)"""
    __tablename__ = "prestadores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Tipo
    tipo_prestador = Column(String(20), nullable=False)  # medico, clinica, laboratorio, hospital
    
    # Identificação
    nome = Column(String(200), nullable=False, index=True)
    razao_social = Column(String(200))
    cnpj = Column(String(18), unique=True)
    
    # Médico específico
    cpf = Column(String(14), unique=True)
    crm = Column(String(20))
    uf_crm = Column(String(2))
    especialidade = Column(String(100))
    codigo_cbo = Column(String(10))  # Classificação Brasileira de Ocupações
    
    # Estabelecimento
    cnes = Column(String(20))  # Cadastro Nacional de Estabelecimentos de Saúde
    
    # Contato
    telefone = Column(String(20))
    email = Column(String(100))
    
    # Endereço
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(10))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Dados bancários
    banco_codigo = Column(String(10))
    banco_agencia = Column(String(10))
    banco_conta = Column(String(20))
    
    # Status
    ativo = Column(Boolean, default=True)
    
    # Observações
    observacoes = Column(Text)
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
