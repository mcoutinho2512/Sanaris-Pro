from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_current_user, get_password_hash
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)
    organization_id: UUID  # ADMIN ESCOLHE A ORGANIZAÇÃO
    role: str = Field(default="user", pattern="^(admin|user)$")
    crm: Optional[str] = None
    specialty: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    organization_id: UUID
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo usuário (apenas admin)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar usuários")
    
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Verificar se organização existe
    org = db.query(Organization).filter(Organization.id == user_data.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    
    if not org.is_active:
        raise HTTPException(status_code=400, detail="Organização inativa")
    
    # Verificar limite de usuários
    user_count = db.query(User).filter(User.organization_id == org.id).count()
    if user_count >= org.max_users:
        raise HTTPException(
            status_code=400, 
            detail=f"Limite de {org.max_users} usuários atingido para esta organização"
        )
    
    # Criar usuário
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        organization_id=user_data.organization_id,
        role=user_data.role,
        crm=user_data.crm,
        specialty=user_data.specialty,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar usuários"""
    
    query = db.query(User)
    
    # Se admin, pode ver de qualquer org
    if current_user.role == 'admin':
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
    else:
        # Usuário comum só vê da sua organização
        query = query.filter(User.organization_id == current_user.organization_id)
    
    users = query.offset(skip).limit(limit).all()
    return users
