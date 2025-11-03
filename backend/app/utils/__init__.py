"""
Utilidades do Sistema
"""
from app.utils.validators import (
    validate_cpf, format_cpf,
    validate_cnpj, format_cnpj,
    validate_phone, format_phone,
    validate_cep, format_cep,
    validate_crm
)
from app.utils.soft_delete import SoftDeleteMixin, apply_soft_delete_filter
from app.utils.pagination import PageParams, PageResponse, paginate, create_page_response
from app.utils.filters import (
    filter_by_date_range,
    filter_by_search,
    filter_by_status,
    filter_by_professional,
    filter_by_patient
)

__all__ = [
    # Validators
    "validate_cpf", "format_cpf",
    "validate_cnpj", "format_cnpj",
    "validate_phone", "format_phone",
    "validate_cep", "format_cep",
    "validate_crm",
    
    # Soft Delete
    "SoftDeleteMixin", "apply_soft_delete_filter",
    
    # Pagination
    "PageParams", "PageResponse", "paginate", "create_page_response",
    
    # Filters
    "filter_by_date_range",
    "filter_by_search",
    "filter_by_status",
    "filter_by_professional",
    "filter_by_patient"
]
