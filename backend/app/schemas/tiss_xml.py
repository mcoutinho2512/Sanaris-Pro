from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class XMLGuiaConsultaSchema(BaseModel):
    numero_guia: str
    data_emissao: date
    codigo_operadora: str
    numero_carteira: str
    nome_beneficiario: str
    codigo_prestador: str
    nome_prestador: str
    codigo_procedimento: str
    descricao_procedimento: str
    data_realizacao: date
    valor_procedimento: Decimal
    valor_total: Decimal

class XMLLoteSchema(BaseModel):
    numero_lote: str
    data_criacao: date
    operadora_codigo: str
    operadora_nome: str
    prestador_codigo: str
    prestador_nome: str
    guias: List[XMLGuiaConsultaSchema]
    valor_total_lote: Decimal
    quantidade_guias: int

class XMLTISSGenerateRequest(BaseModel):
    lote_id: str
    tipo_guia: str = "consulta"  # consulta, sp_sadt, internacao, etc

class XMLTISSGenerateResponse(BaseModel):
    success: bool
    filename: str
    xml_content: str
    message: str
