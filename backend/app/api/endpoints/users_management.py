from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_current_user, get_password_hash
from app.services.email_service import EmailService
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    recovery_email: EmailStr
    full_name: str
    password: str
    organization_id: Optional[UUID] = None
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    recovery_email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    organization_id: Optional[UUID] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    recovery_email: str
    full_name: str
    role: str
    is_active: bool
    organization_name: Optional[str] = None
    created_at: str

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == 'super_admin':
        users = db.query(User).filter(User.is_active == True).all()
    elif current_user.role == 'admin':
        users = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.is_active == True
        ).all()
    else:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    result = []
    for user in users:
        org_name = None
        if user.organization_id:
            org = db.query(Organization).filter(Organization.id == user.organization_id).first()
            if org:
                org_name = org.name
        
        created_at_str = user.created_at if isinstance(user.created_at, str) else user.created_at.isoformat()
        
        result.append(UserResponse(
            id=user.id,
            email=user.email,
            recovery_email=user.recovery_email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            organization_name=org_name,
            created_at=created_at_str
        ))
    return result

@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ['super_admin', 'admin']:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    if current_user.role == 'admin':
        if user_data.organization_id and user_data.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Admin só pode criar na própria organização")
        user_data.organization_id = current_user.organization_id
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Login já cadastrado")
    
    if db.query(User).filter(User.recovery_email == user_data.recovery_email).first():
        raise HTTPException(status_code=400, detail="Email de recuperação já cadastrado")
    
    new_user = User(
        email=user_data.email,
        recovery_email=user_data.recovery_email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        organization_id=user_data.organization_id,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow().isoformat()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Enviar email com credenciais
    try:
        email_service = EmailService()
        email_body = f"""
        <h2>Bem-vindo ao Sanaris Pro!</h2>
        <p>Olá <strong>{new_user.full_name}</strong>,</p>
        <p>Sua conta foi criada com sucesso!</p>
        <p><strong>Login:</strong> {new_user.email}</p>
        <p><strong>Senha temporária:</strong> {user_data.password}</p>
        <p>⚠️ Por favor, altere sua senha no primeiro acesso.</p>
        <p>Acesse: <a href="http://localhost:3001/login">Sanaris Pro</a></p>
        """
        email_service.send_email(
            to_email=new_user.recovery_email,
            subject="Bem-vindo ao Sanaris Pro - Suas Credenciais",
            html_content=email_body
        )
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
    
    org_name = None
    if new_user.organization_id:
        org = db.query(Organization).filter(Organization.id == new_user.organization_id).first()
        if org:
            org_name = org.name
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        recovery_email=new_user.recovery_email,
        full_name=new_user.full_name,
        role=new_user.role,
        is_active=new_user.is_active,
        organization_name=org_name,
        created_at=new_user.created_at if isinstance(new_user.created_at, str) else new_user.created_at.isoformat()
    )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if current_user.role == 'admin' and user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Login já cadastrado")
        user.email = user_data.email
    
    if user_data.recovery_email and user_data.recovery_email != user.recovery_email:
        if db.query(User).filter(User.recovery_email == user_data.recovery_email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email de recuperação já cadastrado")
        user.recovery_email = user_data.recovery_email
    
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.role:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.organization_id:
        user.organization_id = user_data.organization_id
    
    db.commit()
    db.refresh(user)
    
    org_name = None
    if user.organization_id:
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        if org:
            org_name = org.name
    
    created_at_str = user.created_at if isinstance(user.created_at, str) else user.created_at.isoformat()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        recovery_email=user.recovery_email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        organization_name=org_name,
        created_at=created_at_str
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não pode deletar próprio usuário")
    
    if current_user.role == 'admin' and user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    
    user.is_active = False
    db.commit()
    
    return {"message": "Usuário desativado com sucesso"}
