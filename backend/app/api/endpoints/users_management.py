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
    organization_id: UUID
    role: str = Field(default="user", pattern="^(admin|user)$")
    crm: Optional[str] = None
    specialty: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    organization_id: Optional[UUID] = None
    role: Optional[str] = None
    crm: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    organization_id: Optional[UUID]
    organization_name: Optional[str] = None
    role: str
    is_active: bool
    crm: Optional[str] = None
    specialty: Optional[str] = None
    created_at: str
    
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
    user_count = db.query(User).filter(
        User.organization_id == org.id,
        User.is_active == True
    ).count()
    
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
    
    # Adicionar nome da organização na resposta
    response = UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        organization_id=new_user.organization_id,
        organization_name=org.name,
        role=new_user.role,
        is_active=new_user.is_active,
        crm=new_user.crm,
        specialty=new_user.specialty,
        created_at=new_user.created_at.isoformat()
    )
    
    return response

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    organization_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar usuários (admin vê todos, user vê só da sua org)"""
    
    query = db.query(User)
    
    # Admin vê todos, user vê só da sua organização
    if current_user.role == 'admin':
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
    else:
        query = query.filter(User.organization_id == current_user.organization_id)
    
    # Filtrar por status
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    # Adicionar nome da organização
    result = []
    for user in users:
        org_name = None
        if user.organization_id:
            org = db.query(Organization).filter(Organization.id == user.organization_id).first()
            if org:
                org_name = org.name
        
        result.append(UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization_id=user.organization_id,
            organization_name=org_name,
            role=user.role,
            is_active=user.is_active,
            crm=user.crm,
            specialty=user.specialty,
            created_at=user.created_at.isoformat()
        ))
    
    return result

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter detalhes de um usuário"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar permissão
    if current_user.role != 'admin' and user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    org_name = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        if org:
            org_name = org.name
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization_id=user.organization_id,
        organization_name=org_name,
        role=user.role,
        is_active=user.is_active,
        crm=user.crm,
        specialty=user.specialty,
        created_at=user.created_at.isoformat()
    )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar usuário (apenas admin)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar usuários")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar campos
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.organization_id is not None:
        org = db.query(Organization).filter(Organization.id == user_data.organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organização não encontrada")
        user.organization_id = user_data.organization_id
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.crm is not None:
        user.crm = user_data.crm
    
    if user_data.specialty is not None:
        user.specialty = user_data.specialty
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    org_name = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        if org:
            org_name = org.name
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization_id=user.organization_id,
        organization_name=org_name,
        role=user.role,
        is_active=user.is_active,
        crm=user.crm,
        specialty=user.specialty,
        created_at=user.created_at.isoformat()
    )

@router.delete("/{user_id}")
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar usuário (apenas admin)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem desativar usuários")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta")
    
    user.is_active = False
    db.commit()
    
    return {"message": "Usuário desativado com sucesso"}

@router.get("/statistics/by-organization")
def get_users_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estatísticas de usuários por organização (apenas admin)"""
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem ver estatísticas")
    
    from sqlalchemy import func
    
    # Contar usuários ativos por organização
    stats = db.query(
        Organization.id,
        Organization.name,
        Organization.max_users,
        func.count(User.id).label('current_users')
    ).outerjoin(
        User, 
        (User.organization_id == Organization.id) & (User.is_active == True)
    ).group_by(
        Organization.id, 
        Organization.name, 
        Organization.max_users
    ).all()
    
    result = []
    for org_id, org_name, max_users, current_users in stats:
        result.append({
            "organization_id": str(org_id),
            "organization_name": org_name,
            "max_users": max_users,
            "current_users": current_users,
            "available_slots": max_users - current_users,
            "usage_percentage": round((current_users / max_users * 100) if max_users > 0 else 0, 2)
        })
    
    return result
