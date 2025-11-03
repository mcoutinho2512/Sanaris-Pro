"""
Endpoints de Utilidades e Validações
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.utils import (
    validate_cpf, format_cpf,
    validate_cnpj, format_cnpj,
    validate_phone, format_phone,
    validate_cep, format_cep,
    validate_crm
)

router = APIRouter(prefix="/api/v1/utils", tags=["Utilidades"])


class ValidateCPFRequest(BaseModel):
    cpf: str


class ValidateCNPJRequest(BaseModel):
    cnpj: str


class ValidatePhoneRequest(BaseModel):
    phone: str


class ValidateCEPRequest(BaseModel):
    cep: str


class ValidateCRMRequest(BaseModel):
    crm: str
    state: str


@router.post("/validate/cpf")
def validate_cpf_endpoint(data: ValidateCPFRequest):
    """Valida e formata CPF"""
    is_valid = validate_cpf(data.cpf)
    formatted = format_cpf(data.cpf) if is_valid else None
    
    return {
        "valid": is_valid,
        "formatted": formatted,
        "message": "CPF válido" if is_valid else "CPF inválido"
    }


@router.post("/validate/cnpj")
def validate_cnpj_endpoint(data: ValidateCNPJRequest):
    """Valida e formata CNPJ"""
    is_valid = validate_cnpj(data.cnpj)
    formatted = format_cnpj(data.cnpj) if is_valid else None
    
    return {
        "valid": is_valid,
        "formatted": formatted,
        "message": "CNPJ válido" if is_valid else "CNPJ inválido"
    }


@router.post("/validate/phone")
def validate_phone_endpoint(data: ValidatePhoneRequest):
    """Valida e formata telefone"""
    is_valid = validate_phone(data.phone)
    formatted = format_phone(data.phone) if is_valid else None
    
    return {
        "valid": is_valid,
        "formatted": formatted,
        "message": "Telefone válido" if is_valid else "Telefone inválido"
    }


@router.post("/validate/cep")
def validate_cep_endpoint(data: ValidateCEPRequest):
    """Valida e formata CEP"""
    is_valid = validate_cep(data.cep)
    formatted = format_cep(data.cep) if is_valid else None
    
    return {
        "valid": is_valid,
        "formatted": formatted,
        "message": "CEP válido" if is_valid else "CEP inválido"
    }


@router.post("/validate/crm")
def validate_crm_endpoint(data: ValidateCRMRequest):
    """Valida CRM"""
    is_valid = validate_crm(data.crm, data.state)
    
    return {
        "valid": is_valid,
        "message": f"CRM válido para {data.state}" if is_valid else "CRM inválido"
    }


@router.get("/info")
def get_utils_info():
    """Retorna informações sobre utilidades disponíveis"""
    return {
        "validators": {
            "cpf": "Valida CPF brasileiro (XXX.XXX.XXX-XX)",
            "cnpj": "Valida CNPJ brasileiro (XX.XXX.XXX/XXXX-XX)",
            "phone": "Valida telefone brasileiro ((XX) XXXXX-XXXX)",
            "cep": "Valida CEP brasileiro (XXXXX-XXX)",
            "crm": "Valida CRM (Conselho Regional de Medicina)"
        },
        "features": {
            "soft_delete": "Exclusão lógica em todos os módulos",
            "pagination": "Paginação automática em listas",
            "advanced_filters": "Filtros por data, status, profissional",
            "search": "Busca avançada em múltiplos campos"
        },
        "version": "2.4"
    }
