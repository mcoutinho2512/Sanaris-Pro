from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job_title import JobTitle
from app.schemas.job_title import JobTitleCreate, JobTitleUpdate, JobTitleResponse

router = APIRouter()

@router.get("/", response_model=List[JobTitleResponse])
def list_job_titles(
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    is_healthcare_professional: bool = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os cargos com filtros opcionais"""
    query = db.query(JobTitle)
    
    if is_active is not None:
        query = query.filter(JobTitle.is_active == is_active)
    
    if department:
        query = query.filter(JobTitle.department == department)
    
    if is_healthcare_professional is not None:
        query = query.filter(JobTitle.is_healthcare_professional == is_healthcare_professional)
    
    job_titles = query.order_by(JobTitle.department, JobTitle.name).offset(skip).limit(limit).all()
    return job_titles

@router.get("/departments", response_model=List[str])
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os departamentos únicos"""
    departments = db.query(JobTitle.department).distinct().order_by(JobTitle.department).all()
    return [dept[0] for dept in departments]

@router.get("/{job_title_id}", response_model=JobTitleResponse)
def get_job_title(
    job_title_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter cargo por ID"""
    job_title = db.query(JobTitle).filter(JobTitle.id == job_title_id).first()
    
    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    return job_title

@router.post("/", response_model=JobTitleResponse, status_code=status.HTTP_201_CREATED)
def create_job_title(
    job_title_data: JobTitleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo cargo (apenas admins)"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar cargos"
        )
    
    # Verificar se já existe cargo com mesmo nome
    existing = db.query(JobTitle).filter(JobTitle.name == job_title_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um cargo com este nome"
        )
    
    job_title = JobTitle(**job_title_data.model_dump())
    db.add(job_title)
    db.commit()
    db.refresh(job_title)
    
    return job_title

@router.put("/{job_title_id}", response_model=JobTitleResponse)
def update_job_title(
    job_title_id: UUID,
    job_title_data: JobTitleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar cargo (apenas admins)"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem atualizar cargos"
        )
    
    job_title = db.query(JobTitle).filter(JobTitle.id == job_title_id).first()
    
    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Verificar nome duplicado se estiver alterando
    if job_title_data.name and job_title_data.name != job_title.name:
        existing = db.query(JobTitle).filter(JobTitle.name == job_title_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cargo com este nome"
            )
    
    # Atualizar campos
    for field, value in job_title_data.model_dump(exclude_unset=True).items():
        setattr(job_title, field, value)
    
    db.commit()
    db.refresh(job_title)
    
    return job_title

@router.delete("/{job_title_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_title(
    job_title_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar cargo (soft delete - apenas admins)"""
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem desativar cargos"
        )
    
    job_title = db.query(JobTitle).filter(JobTitle.id == job_title_id).first()
    
    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cargo não encontrado"
        )
    
    # Soft delete
    job_title.is_active = False
    db.commit()
    
    return None
