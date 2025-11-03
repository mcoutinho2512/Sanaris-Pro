"""
Helpers para Filtros Avançados
"""
from typing import Optional
from datetime import datetime, date
from sqlalchemy import and_, or_, func


def filter_by_date_range(query, date_field, date_from: Optional[datetime], date_to: Optional[datetime]):
    """
    Filtra query por range de datas
    
    Args:
        query: Query do SQLAlchemy
        date_field: Campo de data do model
        date_from: Data inicial
        date_to: Data final
        
    Returns:
        Query filtrada
    """
    if date_from:
        query = query.filter(date_field >= date_from)
    
    if date_to:
        query = query.filter(date_field <= date_to)
    
    return query


def filter_by_search(query, fields: list, search_term: Optional[str]):
    """
    Filtra query por termo de busca em múltiplos campos
    
    Args:
        query: Query do SQLAlchemy
        fields: Lista de campos para buscar
        search_term: Termo de busca
        
    Returns:
        Query filtrada
    """
    if not search_term:
        return query
    
    # Cria condições OR para cada campo
    search_conditions = []
    for field in fields:
        search_conditions.append(field.ilike(f"%{search_term}%"))
    
    if search_conditions:
        query = query.filter(or_(*search_conditions))
    
    return query


def filter_by_status(query, status_field, status: Optional[str]):
    """
    Filtra query por status
    
    Args:
        query: Query do SQLAlchemy
        status_field: Campo de status do model
        status: Status para filtrar
        
    Returns:
        Query filtrada
    """
    if status:
        query = query.filter(status_field == status)
    
    return query


def filter_by_professional(query, professional_field, professional_id: Optional[str]):
    """
    Filtra query por profissional
    
    Args:
        query: Query do SQLAlchemy
        professional_field: Campo de profissional do model
        professional_id: ID do profissional
        
    Returns:
        Query filtrada
    """
    if professional_id:
        query = query.filter(professional_field == professional_id)
    
    return query


def filter_by_patient(query, patient_field, patient_id: Optional[str]):
    """
    Filtra query por paciente
    
    Args:
        query: Query do SQLAlchemy
        patient_field: Campo de paciente do model
        patient_id: ID do paciente
        
    Returns:
        Query filtrada
    """
    if patient_id:
        query = query.filter(patient_field == patient_id)
    
    return query
