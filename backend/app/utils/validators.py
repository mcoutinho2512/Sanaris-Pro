"""
Validações Brasileiras - CPF, CNPJ, Telefone
"""
import re
from typing import Optional


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro
    
    Args:
        cpf: CPF com ou sem formatação
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula primeiro dígito verificador
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    first_digit = (sum_digits * 10 % 11) % 10
    
    if int(cpf[9]) != first_digit:
        return False
    
    # Calcula segundo dígito verificador
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    second_digit = (sum_digits * 10 % 11) % 10
    
    if int(cpf[10]) != second_digit:
        return False
    
    return True


def format_cpf(cpf: str) -> str:
    """
    Formata CPF para padrão XXX.XXX.XXX-XX
    
    Args:
        cpf: CPF sem formatação
        
    Returns:
        CPF formatado
    """
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro
    
    Args:
        cnpj: CNPJ com ou sem formatação
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula primeiro dígito verificador
    weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights[i] for i in range(12))
    first_digit = (sum_digits % 11)
    first_digit = 0 if first_digit < 2 else 11 - first_digit
    
    if int(cnpj[12]) != first_digit:
        return False
    
    # Calcula segundo dígito verificador
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights[i] for i in range(13))
    second_digit = (sum_digits % 11)
    second_digit = 0 if second_digit < 2 else 11 - second_digit
    
    if int(cnpj[13]) != second_digit:
        return False
    
    return True


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ para padrão XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj: CNPJ sem formatação
        
    Returns:
        CNPJ formatado
    """
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj


def validate_phone(phone: str) -> bool:
    """
    Valida telefone brasileiro (fixo ou celular)
    
    Formatos aceitos:
    - (XX) XXXX-XXXX (fixo)
    - (XX) 9XXXX-XXXX (celular)
    - Sem formatação: 10 ou 11 dígitos
    
    Args:
        phone: Telefone com ou sem formatação
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Verifica se tem 10 ou 11 dígitos
    if len(phone) not in [10, 11]:
        return False
    
    # Verifica DDD (primeiros 2 dígitos)
    ddd = int(phone[:2])
    valid_ddds = [
        11, 12, 13, 14, 15, 16, 17, 18, 19,  # SP
        21, 22, 24,  # RJ
        27, 28,  # ES
        31, 32, 33, 34, 35, 37, 38,  # MG
        41, 42, 43, 44, 45, 46,  # PR
        47, 48, 49,  # SC
        51, 53, 54, 55,  # RS
        61,  # DF
        62, 64,  # GO
        63,  # TO
        65, 66,  # MT
        67,  # MS
        68,  # AC
        69,  # RO
        71, 73, 74, 75, 77,  # BA
        79,  # SE
        81, 87,  # PE
        82,  # AL
        83,  # PB
        84,  # RN
        85, 88,  # CE
        86, 89,  # PI
        91, 93, 94,  # PA
        92, 97,  # AM
        95,  # RR
        96,  # AP
        98, 99  # MA
    ]
    
    if ddd not in valid_ddds:
        return False
    
    # Se tem 11 dígitos, verifica se o terceiro dígito é 9 (celular)
    if len(phone) == 11 and phone[2] != '9':
        return False
    
    return True


def format_phone(phone: str) -> str:
    """
    Formata telefone brasileiro
    
    Args:
        phone: Telefone sem formatação
        
    Returns:
        Telefone formatado: (XX) XXXX-XXXX ou (XX) 9XXXX-XXXX
    """
    phone = re.sub(r'[^0-9]', '', phone)
    
    if len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    elif len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    
    return phone


def validate_cep(cep: str) -> bool:
    """
    Valida CEP brasileiro
    
    Args:
        cep: CEP com ou sem formatação
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cep = re.sub(r'[^0-9]', '', cep)
    
    # Verifica se tem 8 dígitos
    return len(cep) == 8


def format_cep(cep: str) -> str:
    """
    Formata CEP para padrão XXXXX-XXX
    
    Args:
        cep: CEP sem formatação
        
    Returns:
        CEP formatado
    """
    cep = re.sub(r'[^0-9]', '', cep)
    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep


def validate_crm(crm: str, state: str) -> bool:
    """
    Valida CRM (Conselho Regional de Medicina)
    
    Args:
        crm: Número do CRM
        state: UF do CRM
        
    Returns:
        True se válido, False caso contrário
    """
    # Remove caracteres não numéricos
    crm = re.sub(r'[^0-9]', '', crm)
    
    # Verifica se tem entre 4 e 6 dígitos
    if not (4 <= len(crm) <= 6):
        return False
    
    # Verifica se state é uma UF válida
    valid_states = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    return state.upper() in valid_states
