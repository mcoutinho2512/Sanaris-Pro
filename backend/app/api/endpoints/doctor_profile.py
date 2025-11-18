from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from app.core.security import get_current_user
from app.schemas.doctor_profile import (
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse
)
import shutil
import os
from uuid import uuid4

router = APIRouter()

@router.get("/me", response_model=DoctorProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter perfil médico do usuário logado
    """
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil médico não encontrado"
        )
    
    return profile

@router.post("/", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: DoctorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Criar perfil médico
    """
    # Verificar se já existe perfil
    existing = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil médico já existe. Use PUT para atualizar."
        )
    
    # Criar novo perfil
    profile = DoctorProfile(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        **profile_data.dict()
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile

@router.put("/", response_model=DoctorProfileResponse)
def update_profile(
    profile_data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualizar perfil médico
    """
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil médico não encontrado. Use POST para criar."
        )
    
    # Atualizar apenas campos fornecidos
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile

@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload de logo do médico
    """
    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem"
        )
    
    # Criar diretório se não existir
    upload_dir = "uploads/logos"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Gerar nome único
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Salvar arquivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # URL relativa para acesso
    logo_url = f"/uploads/logos/{unique_filename}"
    
    # Atualizar perfil
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == current_user.id
    ).first()
    
    if profile:
        # Deletar logo antigo se existir
        if profile.logo_url:
            old_file = profile.logo_url.replace('/uploads/logos/', '')
            old_path = os.path.join(upload_dir, old_file)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        profile.logo_url = logo_url
        db.commit()
    
    return {"logo_url": logo_url, "message": "Logo enviado com sucesso"}

@router.delete("/")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar perfil médico
    """
    profile = db.query(DoctorProfile).filter(
        DoctorProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil médico não encontrado"
        )
    
    # Deletar logo se existir
    if profile.logo_url:
        upload_dir = "uploads/logos"
        filename = profile.logo_url.replace('/uploads/logos/', '')
        file_path = os.path.join(upload_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Perfil deletado com sucesso"}
