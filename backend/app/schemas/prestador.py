from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class PrestadorBase(BaseModel):
    tipo_prestador: str = Field(..., pattern=r'^(medico|clinica|laboratorio|hospital)$')
    nome: str = Field(..., max_length=200)
    razao_social: Optional[str] = Field(None, max_length=200)
    cnpj: Optional[str] = Field(None, max_length=18)
    cpf: Optional[str] = Field(None, max_length=14)
    crm: Optional[str] = Field(None, max_length=20)
    uf_crm: Optional[str] = Field(None, min_length=2, max_length=2)
    especialidade: Optional[str] = Field(None, max_length=100)
    codigo_cbo: Optional[str] = Field(None, max_length=10)
    cnes: Optional[str] = Field(None, max_length=20)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=200)
    numero: Optional[str] = Field(None, max_length=10)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    banco_codigo: Optional[str] = Field(None, max_length=10)
    banco_agencia: Optional[str] = Field(None, max_length=10)
    banco_conta: Optional[str] = Field(None, max_length=20)
    ativo: bool = True
    observacoes: Optional[str] = None

class PrestadorCreate(PrestadorBase):
    pass

class PrestadorUpdate(BaseModel):
    tipo_prestador: Optional[str] = None
    nome: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    crm: Optional[str] = None
    uf_crm: Optional[str] = None
    especialidade: Optional[str] = None
    codigo_cbo: Optional[str] = None
    cnes: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    banco_codigo: Optional[str] = None
    banco_agencia: Optional[str] = None
    banco_conta: Optional[str] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None

class PrestadorResponse(PrestadorBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
