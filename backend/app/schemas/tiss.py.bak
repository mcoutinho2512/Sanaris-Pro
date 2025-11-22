"""
Schemas para Faturamento TISS - Alinhado com models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum


# ============================================
# ENUMS
# ============================================

class TipoOperadoraEnum(str, Enum):
    """Tipo de operadora"""
    MEDICINA_GRUPO = "medicina_grupo"
    COOPERATIVA = "cooperativa"
    FILANTROPIA = "filantropia"
    AUTOGESTAO = "autogestao"


class TipoGuiaEnum(str, Enum):
    """Tipo de guia"""
    CONSULTA = "consulta"
    SP_SADT = "sp_sadt"
    INTERNACAO = "internacao"
    HONORARIOS = "honorarios"


class StatusGuiaEnum(str, Enum):
    """Status da guia"""
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    PROCESSADO = "processado"
    PAGO = "pago"
    GLOSADO = "glosado"
    REJEITADO = "rejeitado"


class StatusLoteEnum(str, Enum):
    """Status do lote"""
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    PROCESSADO = "processado"
    PAGO = "pago"
    REJEITADO = "rejeitado"
    CANCELADO = "cancelado"


# ============================================
# OPERADORAS
# ============================================

class TISSOperadoraBase(BaseModel):
    """Schema base de operadora"""
    registro_ans: str = Field(..., min_length=6, max_length=6, description="Código ANS")
    razao_social: str = Field(..., max_length=200)
    nome_fantasia: Optional[str] = Field(None, max_length=200)
    cnpj: str = Field(..., pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    padrao_tiss_versao: str = Field(default="4.02.01", max_length=20)
    prazo_envio_dias: int = Field(default=30, ge=1)
    prazo_pagamento_dias: int = Field(default=30, ge=1)
    banco_codigo: Optional[str] = None
    banco_agencia: Optional[str] = None
    banco_conta: Optional[str] = None
    ativo: bool = True
    observacoes: Optional[str] = None


class TISSOperadoraCreate(TISSOperadoraBase):
    """Schema para criação"""
    pass


class TISSOperadoraUpdate(BaseModel):
    """Schema para atualização"""
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    padrao_tiss_versao: Optional[str] = None
    prazo_envio_dias: Optional[int] = None
    prazo_pagamento_dias: Optional[int] = None
    banco_codigo: Optional[str] = None
    banco_agencia: Optional[str] = None
    banco_conta: Optional[str] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None


class TISSOperadoraResponse(TISSOperadoraBase):
    """Schema de resposta"""
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# LOTES TISS
# ============================================

class TISSLoteBase(BaseModel):
    """Schema base de lote"""
    operadora_id: UUID
    competencia: str = Field(..., pattern=r'^\d{2}/\d{4}$', description="Formato MM/AAAA")
    observacoes: Optional[str] = None


class TISSLoteCreate(TISSLoteBase):
    """Schema para criação"""
    pass


class TISSLoteUpdate(BaseModel):
    """Schema para atualização"""
    status: Optional[StatusLoteEnum] = None
    data_envio: Optional[datetime] = None
    protocolo_envio: Optional[str] = None
    data_processamento: Optional[datetime] = None
    protocolo_processamento: Optional[str] = None
    valor_total_processado: Optional[float] = None
    valor_total_glosa: Optional[float] = None
    valor_total_liberado: Optional[float] = None
    quantidade_guias_processadas: Optional[int] = None
    quantidade_guias_rejeitadas: Optional[int] = None
    arquivo_retorno_path: Optional[str] = None
    data_pagamento: Optional[date] = None
    observacoes: Optional[str] = None
    motivo_rejeicao: Optional[str] = None


class TISSLoteResponse(TISSLoteBase):
    """Schema de resposta"""
    id: UUID
    organization_id: UUID
    numero_lote: str
    status: str
    data_envio: Optional[datetime]
    protocolo_envio: Optional[str]
    data_processamento: Optional[datetime]
    protocolo_processamento: Optional[str]
    valor_total_informado: float
    valor_total_processado: float
    valor_total_glosa: float
    valor_total_liberado: float
    quantidade_guias: int
    quantidade_guias_processadas: int
    quantidade_guias_rejeitadas: int
    arquivo_xml_path: Optional[str]
    arquivo_retorno_path: Optional[str]
    data_pagamento: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TISSLoteListResponse(BaseModel):
    """Schema de lista simplificada"""
    id: UUID
    numero_lote: str
    competencia: str
    status: str
    valor_total_informado: float
    quantidade_guias: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# GUIAS TISS
# ============================================

class TISSGuiaBase(BaseModel):
    """Schema base de guia"""
    patient_id: UUID
    tipo_guia: TipoGuiaEnum
    data_atendimento: date
    hora_inicial: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    hora_final: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    numero_carteira: str = Field(..., max_length=50)
    validade_carteira: Optional[date] = None
    nome_beneficiario: str = Field(..., max_length=200)
    numero_cns: Optional[str] = Field(None, min_length=15, max_length=20)
    codigo_prestador_na_operadora: Optional[str] = None
    nome_contratado: str = Field(..., max_length=200)
    cnpj_contratado: str = Field(..., pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    cnes: Optional[str] = Field(None, max_length=20)
    nome_profissional: Optional[str] = Field(None, max_length=200)
    numero_conselho_profissional: Optional[str] = Field(None, max_length=20)
    uf_conselho: Optional[str] = Field(None, min_length=2, max_length=2)
    sigla_conselho: Optional[str] = Field(None, max_length=10)
    codigo_cbo: Optional[str] = Field(None, max_length=10)
    indicacao_clinica: str = Field(..., pattern=r'^(C|U|E)$', description="C=Clínica, U=Urgência, E=Eletiva")
    cid10_principal: Optional[str] = Field(None, max_length=10)
    cid10_secundario: Optional[str] = Field(None, max_length=10)
    cid10_terciario: Optional[str] = Field(None, max_length=10)
    observacoes_clinicas: Optional[str] = None
    numero_autorizacao: Optional[str] = Field(None, max_length=50)
    data_autorizacao: Optional[date] = None
    observacoes: Optional[str] = None


class TISSGuiaCreate(TISSGuiaBase):
    """Schema para criação"""
    lote_id: UUID


class TISSGuiaUpdate(BaseModel):
    """Schema para atualização"""
    data_atendimento: Optional[date] = None
    hora_inicial: Optional[str] = None
    hora_final: Optional[str] = None
    numero_carteira: Optional[str] = None
    validade_carteira: Optional[date] = None
    nome_beneficiario: Optional[str] = None
    numero_cns: Optional[str] = None
    indicacao_clinica: Optional[str] = None
    cid10_principal: Optional[str] = None
    cid10_secundario: Optional[str] = None
    cid10_terciario: Optional[str] = None
    observacoes_clinicas: Optional[str] = None
    numero_autorizacao: Optional[str] = None
    data_autorizacao: Optional[date] = None
    status: Optional[StatusGuiaEnum] = None
    numero_guia_operadora: Optional[str] = None
    valor_total_processado: Optional[float] = None
    valor_glosa: Optional[float] = None
    valor_liberado: Optional[float] = None
    motivo_glosa: Optional[str] = None
    observacoes: Optional[str] = None


class TISSGuiaResponse(TISSGuiaBase):
    """Schema de resposta"""
    id: UUID
    organization_id: UUID
    lote_id: UUID
    numero_guia_prestador: str
    numero_guia_operadora: Optional[str]
    valor_total_informado: float
    valor_total_processado: float
    valor_glosa: float
    valor_liberado: float
    status: str
    motivo_glosa: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TISSGuiaListResponse(BaseModel):
    """Schema de lista simplificada"""
    id: UUID
    numero_guia_prestador: str
    tipo_guia: str
    nome_beneficiario: str
    data_atendimento: date
    valor_total_informado: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# PROCEDIMENTOS DA GUIA
# ============================================

class TISSProcedimentoBase(BaseModel):
    """Schema base de procedimento"""
    data_realizacao: date
    hora_inicial: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    hora_final: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    tabela: str = Field(..., max_length=10, description="22=TUSS, 18=CBHPM")
    codigo_procedimento: str = Field(..., max_length=20)
    descricao_procedimento: str = Field(..., max_length=500)
    quantidade_executada: int = Field(default=1, ge=1)
    via_acesso: Optional[str] = Field(None, max_length=10)
    tecnica_utilizada: Optional[str] = Field(None, max_length=10)
    valor_unitario_informado: float = Field(..., ge=0)
    nome_profissional_executante: Optional[str] = Field(None, max_length=200)
    conselho_profissional: Optional[str] = Field(None, max_length=20)
    numero_conselho: Optional[str] = Field(None, max_length=20)
    uf_conselho: Optional[str] = Field(None, min_length=2, max_length=2)
    codigo_cbo: Optional[str] = Field(None, max_length=10)
    grau_participacao: Optional[str] = Field(None, max_length=10, description="00=Responsável, 01=Auxiliar")
    observacoes: Optional[str] = None


class TISSProcedimentoCreate(TISSProcedimentoBase):
    """Schema para criação"""
    guia_id: UUID


class TISSProcedimentoUpdate(BaseModel):
    """Schema para atualização"""
    data_realizacao: Optional[date] = None
    hora_inicial: Optional[str] = None
    hora_final: Optional[str] = None
    quantidade_executada: Optional[int] = None
    valor_unitario_informado: Optional[float] = None
    quantidade_autorizada: Optional[int] = None
    valor_unitario_processado: Optional[float] = None
    valor_total_processado: Optional[float] = None
    valor_glosa: Optional[float] = None
    valor_liberado: Optional[float] = None
    codigo_glosa: Optional[str] = None
    motivo_glosa: Optional[str] = None
    observacoes: Optional[str] = None


class TISSProcedimentoResponse(TISSProcedimentoBase):
    """Schema de resposta"""
    id: UUID
    organization_id: UUID
    guia_id: UUID
    valor_total_informado: float
    quantidade_autorizada: Optional[int]
    valor_unitario_processado: Optional[float]
    valor_total_processado: Optional[float]
    valor_glosa: float
    valor_liberado: Optional[float]
    codigo_glosa: Optional[str]
    motivo_glosa: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# TABELA REFERÊNCIA (TUSS/CBHPM)
# ============================================

class TISSTabelaReferenciaBase(BaseModel):
    """Schema base de tabela de referência"""
    tipo_tabela: str = Field(..., max_length=20, description="TUSS, CBHPM, BRASINDICE")
    codigo_tabela: str = Field(..., max_length=10, description="22=TUSS, 18=CBHPM")
    codigo: str = Field(..., max_length=20)
    descricao: str = Field(..., max_length=500)
    valor_referencia: Optional[float] = Field(None, ge=0)
    valor_minimo: Optional[float] = Field(None, ge=0)
    valor_maximo: Optional[float] = Field(None, ge=0)
    data_inicio_vigencia: date
    data_fim_vigencia: Optional[date] = None
    capitulo: Optional[str] = Field(None, max_length=200)
    grupo: Optional[str] = Field(None, max_length=200)
    subgrupo: Optional[str] = Field(None, max_length=200)
    porte_anestesico: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None
    ativo: bool = True


class TISSTabelaReferenciaCreate(TISSTabelaReferenciaBase):
    """Schema para criação"""
    pass


class TISSTabelaReferenciaUpdate(BaseModel):
    """Schema para atualização"""
    descricao: Optional[str] = None
    valor_referencia: Optional[float] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    data_fim_vigencia: Optional[date] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None


class TISSTabelaReferenciaResponse(TISSTabelaReferenciaBase):
    """Schema de resposta"""
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# SCHEMAS COMPLEMENTARES
# ============================================

class TISSGuiaComProcedimentos(TISSGuiaResponse):
    """Guia com lista de procedimentos"""
    procedimentos: List[TISSProcedimentoResponse] = []


class TISSLoteComGuias(TISSLoteResponse):
    """Lote com lista de guias"""
    guias: List[TISSGuiaListResponse] = []
    operadora: Optional[TISSOperadoraResponse] = None


# ============================================
# AÇÕES ESPECIAIS
# ============================================

class AdicionarGuiaAoLoteRequest(BaseModel):
    """Request para adicionar guia ao lote"""
    guia_id: UUID
    lote_id: UUID


class FecharLoteRequest(BaseModel):
    """Request para fechar lote"""
    lote_id: UUID


class GerarXMLTISSRequest(BaseModel):
    """Request para gerar XML TISS"""
    lote_id: UUID


class GlosarGuiaRequest(BaseModel):
    """Request para glosar guia"""
    guia_id: UUID
    valor_glosa: float = Field(..., ge=0)
    motivo_glosa: str = Field(..., min_length=1)


# ============================================
# RELATÓRIOS
# ============================================

class TISSResumoFaturamento(BaseModel):
    """Resumo de faturamento para dashboard"""
    total_lotes: int
    total_guias: int
    valor_total_informado: float
    valor_total_processado: float
    valor_total_glosa: float
    valor_total_liberado: float
    lotes_por_status: dict


class TISSResumoPorOperadora(BaseModel):
    """Resumo por operadora"""
    operadora_id: UUID
    operadora_nome: str
    total_guias: int
    valor_total: float
    valor_aceito: float
    valor_glosa: float


class TISSResumoPorPeriodo(BaseModel):
    """Resumo por período"""
    ano: int
    mes: int
    mes_nome: str
    total_guias: int
    valor_total: float
    total_lotes: int


# ============================================
# LABELS EM PORTUGUÊS
# ============================================

TIPO_GUIA_LABELS = {
    "consulta": "Consulta",
    "sp_sadt": "SP/SADT",
    "internacao": "Internação",
    "honorarios": "Honorários Individuais"
}

STATUS_GUIA_LABELS = {
    "pendente": "Pendente",
    "enviado": "Enviado",
    "processado": "Processado",
    "pago": "Pago",
    "glosado": "Glosado",
    "rejeitado": "Rejeitado"
}

STATUS_LOTE_LABELS = {
    "rascunho": "Rascunho",
    "enviado": "Enviado",
    "processado": "Processado",
    "pago": "Pago",
    "rejeitado": "Rejeitado",
    "cancelado": "Cancelado"
}