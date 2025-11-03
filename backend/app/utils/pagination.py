"""
Sistema de Paginação
"""
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from math import ceil


T = TypeVar('T')


class PageParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = 1
    page_size: int = 50
    
    @property
    def skip(self) -> int:
        """Calcula quantos registros pular"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Retorna o limite de registros"""
        return self.page_size


class PageResponse(BaseModel, Generic[T]):
    """Resposta paginada"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    class Config:
        from_attributes = True


def paginate(query, page_params: PageParams) -> tuple:
    """
    Pagina uma query do SQLAlchemy
    
    Args:
        query: Query do SQLAlchemy
        page_params: Parâmetros de paginação
        
    Returns:
        Tupla com (items, total)
    """
    total = query.count()
    items = query.offset(page_params.skip).limit(page_params.limit).all()
    
    return items, total


def create_page_response(items: List[T], total: int, page_params: PageParams) -> dict:
    """
    Cria resposta paginada
    
    Args:
        items: Lista de items
        total: Total de registros
        page_params: Parâmetros de paginação
        
    Returns:
        Dict com informações de paginação
    """
    total_pages = ceil(total / page_params.page_size) if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page_params.page,
        "page_size": page_params.page_size,
        "total_pages": total_pages,
        "has_next": page_params.page < total_pages,
        "has_previous": page_params.page > 1
    }
