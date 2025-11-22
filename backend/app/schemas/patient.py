from pydantic import BaseModel, UUID4
from datetime import date, datetime
from typing import Optional

class PatientBase(BaseModel):
    full_name: str
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Campos TISS
    numero_carteira: Optional[str] = None
    validade_carteira: Optional[date] = None
    operadora_id: Optional[UUID4] = None
    cns: Optional[str] = None
    nome_mae: Optional[str] = None

class PatientCreate(PatientBase):
    tenant_id: UUID4

class PatientUpdate(BaseModel):
    """Schema para atualização de paciente - todos os campos opcionais"""
    full_name: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Campos TISS
    numero_carteira: Optional[str] = None
    validade_carteira: Optional[date] = None
    operadora_id: Optional[UUID4] = None
    cns: Optional[str] = None
    nome_mae: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(PatientBase):
    id: UUID4
    tenant_id: UUID4
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
