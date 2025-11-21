from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class TISSOperadora(Base):
    """Cadastro de Operadoras de Planos de Saúde"""
    __tablename__ = "tiss_operadoras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Dados da Operadora
    registro_ans = Column(String(6), nullable=False, unique=True)
    razao_social = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    cnpj = Column(String(18), nullable=False)
    
    # Contatos
    telefone = Column(String(20))
    email = Column(String(100))
    site = Column(String(200))
    
    # Endereço
    cep = Column(String(10))
    logradouro = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Configurações de Faturamento
    padrao_tiss_versao = Column(String(20), default="4.02.01")
    prazo_envio_dias = Column(Integer, default=30)
    prazo_pagamento_dias = Column(Integer, default=30)
    
    # Dados Bancários
    banco_codigo = Column(String(10))
    banco_agencia = Column(String(20))
    banco_conta = Column(String(30))
    
    # Status e Observações
    ativo = Column(Boolean, default=True)
    observacoes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="tiss_operadoras")
    lotes = relationship("TISSLote", back_populates="operadora")


class TISSLote(Base):
    """Lotes de Faturamento TISS"""
    __tablename__ = "tiss_lotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    operadora_id = Column(UUID(as_uuid=True), ForeignKey("tiss_operadoras.id"), nullable=False)
    
    # Identificação do Lote
    numero_lote = Column(String(50), nullable=False)
    competencia = Column(String(7), nullable=False)
    
    # Status do Lote
    status = Column(String(30), nullable=False, default="rascunho")
    
    # Dados de Envio
    data_envio = Column(DateTime)
    protocolo_envio = Column(String(100))
    
    # Dados de Processamento
    data_processamento = Column(DateTime)
    protocolo_processamento = Column(String(100))
    
    # Valores Totais
    valor_total_informado = Column(Float, default=0.0)
    valor_total_processado = Column(Float, default=0.0)
    valor_total_glosa = Column(Float, default=0.0)
    valor_total_liberado = Column(Float, default=0.0)
    
    # Contadores
    quantidade_guias = Column(Integer, default=0)
    quantidade_guias_processadas = Column(Integer, default=0)
    quantidade_guias_rejeitadas = Column(Integer, default=0)
    
    # Arquivos
    arquivo_xml_path = Column(String(500))
    arquivo_retorno_path = Column(String(500))
    
    # Dados de Pagamento
    dados_pagamento = Column(JSON)
    data_pagamento = Column(Date)
    
    # Observações
    observacoes = Column(Text)
    motivo_rejeicao = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="tiss_lotes")
    operadora = relationship("TISSOperadora", back_populates="lotes")
    guias = relationship("TISSGuia", back_populates="lote")


class TISSGuia(Base):
    """Guias TISS"""
    __tablename__ = "tiss_guias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    lote_id = Column(UUID(as_uuid=True), ForeignKey("tiss_lotes.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Tipo de Guia
    tipo_guia = Column(String(50), nullable=False)
    
    # Identificação da Guia
    numero_guia_prestador = Column(String(50), nullable=False)
    numero_guia_operadora = Column(String(50))
    
    # Dados do Atendimento
    data_atendimento = Column(Date, nullable=False)
    hora_inicial = Column(String(5))
    hora_final = Column(String(5))
    
    # Dados do Beneficiário
    numero_carteira = Column(String(50), nullable=False)
    validade_carteira = Column(Date)
    nome_beneficiario = Column(String(200), nullable=False)
    numero_cns = Column(String(20))
    
    # Dados do Contratado
    codigo_prestador_na_operadora = Column(String(50))
    nome_contratado = Column(String(200), nullable=False)
    cnpj_contratado = Column(String(18), nullable=False)
    cnes = Column(String(20))
    
    # Dados do Profissional
    nome_profissional = Column(String(200))
    numero_conselho_profissional = Column(String(20))
    uf_conselho = Column(String(2))
    sigla_conselho = Column(String(10))
    codigo_cbo = Column(String(10))
    
    # Dados Clínicos
    indicacao_clinica = Column(String(10))
    cid10_principal = Column(String(10))
    cid10_secundario = Column(String(10))
    cid10_terciario = Column(String(10))
    observacoes_clinicas = Column(Text)
    
    # Autorização
    numero_autorizacao = Column(String(50))
    data_autorizacao = Column(Date)
    
    # Valores
    valor_total_informado = Column(Float, default=0.0)
    valor_total_processado = Column(Float, default=0.0)
    valor_glosa = Column(Float, default=0.0)
    valor_liberado = Column(Float, default=0.0)
    
    # Status
    status = Column(String(30), nullable=False, default="pendente")
    motivo_glosa = Column(Text)
    observacoes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="tiss_guias")
    lote = relationship("TISSLote", back_populates="guias")
    patient = relationship("Patient", back_populates="tiss_guias")
    procedimentos = relationship("TISSProcedimento", back_populates="guia")


class TISSProcedimento(Base):
    """Procedimentos de uma guia TISS"""
    __tablename__ = "tiss_procedimentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    guia_id = Column(UUID(as_uuid=True), ForeignKey("tiss_guias.id"), nullable=False)
    
    # Dados do Procedimento
    data_realizacao = Column(Date, nullable=False)
    hora_inicial = Column(String(5))
    hora_final = Column(String(5))
    
    # Código do Procedimento
    tabela = Column(String(10), nullable=False)
    codigo_procedimento = Column(String(20), nullable=False)
    descricao_procedimento = Column(String(500), nullable=False)
    
    # Quantidade e Valores
    quantidade_executada = Column(Integer, default=1)
    via_acesso = Column(String(10))
    tecnica_utilizada = Column(String(10))
    
    # Valores Unitários
    valor_unitario_informado = Column(Float, nullable=False)
    valor_total_informado = Column(Float, nullable=False)
    
    # Valores Processados
    quantidade_autorizada = Column(Integer)
    valor_unitario_processado = Column(Float)
    valor_total_processado = Column(Float)
    valor_glosa = Column(Float, default=0.0)
    valor_liberado = Column(Float)
    
    # Glosa
    codigo_glosa = Column(String(10))
    motivo_glosa = Column(String(500))
    
    # Profissional Executante
    nome_profissional_executante = Column(String(200))
    conselho_profissional = Column(String(20))
    numero_conselho = Column(String(20))
    uf_conselho = Column(String(2))
    codigo_cbo = Column(String(10))
    
    # Dados Adicionais
    grau_participacao = Column(String(10))
    observacoes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="tiss_procedimentos")
    guia = relationship("TISSGuia", back_populates="procedimentos")


class TISSTabelaReferencia(Base):
    """Tabelas de Referência TISS"""
    __tablename__ = "tiss_tabelas_referencia"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Tipo de Tabela
    tipo_tabela = Column(String(20), nullable=False)
    codigo_tabela = Column(String(10), nullable=False)
    
    # Dados do Procedimento
    codigo = Column(String(20), nullable=False)
    descricao = Column(String(500), nullable=False)
    
    # Valores de Referência
    valor_referencia = Column(Float)
    valor_minimo = Column(Float)
    valor_maximo = Column(Float)
    
    # Vigência
    data_inicio_vigencia = Column(Date, nullable=False)
    data_fim_vigencia = Column(Date)
    
    # Classificação
    capitulo = Column(String(200))
    grupo = Column(String(200))
    subgrupo = Column(String(200))
    
    # Dados Adicionais
    porte_anestesico = Column(String(10))
    observacoes = Column(Text)
    ativo = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    organization = relationship("Organization", back_populates="tiss_tabelas_referencia")
