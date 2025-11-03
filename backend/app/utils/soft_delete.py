"""
Sistema de Soft Delete
Models que herdam de SoftDeleteMixin terão exclusão lógica
"""
from sqlalchemy import Column, DateTime, Boolean
from datetime import datetime


class SoftDeleteMixin:
    """
    Mixin para adicionar soft delete aos models
    
    Adiciona campos:
    - is_deleted: Boolean (False por padrão)
    - deleted_at: DateTime (null por padrão)
    """
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Marca o registro como deletado"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restaura um registro deletado"""
        self.is_deleted = False
        self.deleted_at = None


def apply_soft_delete_filter(query):
    """
    Aplica filtro para retornar apenas registros não deletados
    
    Args:
        query: Query do SQLAlchemy
        
    Returns:
        Query filtrada
    """
    return query.filter_by(is_deleted=False)
