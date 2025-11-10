from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import json

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UserPermissionsUpdate(BaseModel):
    allowed_modules: List[str]

class UserPermissionsResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    allowed_modules: List[str]
    
    class Config:
        from_attributes = True

# Módulos disponíveis no sistema
AVAILABLE_MODULES = [
    "dashboard",
    "pacientes", 
    "agenda",
    "prontuarios",
    "prescricoes",
    "cfm",
    "financeiro",
    "faturamento_tiss",
    "relatorios",
    "configuracoes",
    "chat"
]

@router.get("/available-modules")
def get_available_modules():
    """Listar módulos disponíveis para configuração"""
    return {
        "modules": [
            {"id": "dashboard", "name": "Dashboard", "icon": "LayoutDashboard"},
            {"id": "pacientes", "name": "Pacientes", "icon": "Users"},
            {"id": "agenda", "name": "Agenda", "icon": "Calendar"},
            {"id": "prontuarios", "name": "Prontuários", "icon": "FileText"},
            {"id": "prescricoes", "name": "Prescrições", "icon": "FileEdit"},
            {"id": "cfm", "name": "CFM", "icon": "Shield"},
            {"id": "financeiro", "name": "Financeiro", "icon": "DollarSign"},
            {"id": "faturamento_tiss", "name": "Faturamento TISS", "icon": "Receipt"},
            {"id": "relatorios", "name": "Relatórios", "icon": "BarChart"},
            {"id": "configuracoes", "name": "Configurações", "icon": "Settings"},
            {"id": "chat", "name": "Chat", "icon": "MessageSquare"}
        ]
    }

@router.get("/user/{user_id}")
def get_user_permissions(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter permissões de um usuário"""
    
    # Apenas admin pode ver permissões de usuários da sua organização
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Admin só pode ver usuários da sua organização
    if current_user.role == 'admin':
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Usuário não pertence à sua organização")
    
    # Parsear JSON de módulos
    try:
        allowed_modules = json.loads(user.allowed_modules) if user.allowed_modules else []
    except:
        allowed_modules = []
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "allowed_modules": allowed_modules
    }

@router.put("/user/{user_id}")
def update_user_permissions(
    user_id: UUID,
    permissions: UserPermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar permissões de um usuário"""
    
    # Apenas admin pode alterar permissões
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Admin só pode alterar usuários da sua organização
    if current_user.role == 'admin':
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Usuário não pertence à sua organização")
    
    # Não pode alterar permissões de admin ou super_admin
    if user.role in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Não é possível alterar permissões de administradores")
    
    # Validar módulos
    invalid_modules = [m for m in permissions.allowed_modules if m not in AVAILABLE_MODULES]
    if invalid_modules:
        raise HTTPException(status_code=400, detail=f"Módulos inválidos: {invalid_modules}")
    
    # Atualizar
    user.allowed_modules = json.dumps(permissions.allowed_modules)
    db.commit()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "allowed_modules": permissions.allowed_modules,
        "message": "Permissões atualizadas com sucesso"
    }

@router.get("/my-modules")
def get_my_modules(current_user: User = Depends(get_current_user)):
    """Obter módulos permitidos para o usuário logado"""
    
    # Super admin tem acesso especial (apenas gestão)
    if current_user.role == 'super_admin':
        return {
            "role": "super_admin",
            "modules": ["organizacoes", "usuarios"]  # Apenas gestão do sistema
        }
    
    # Admin tem acesso total
    if current_user.role == 'admin':
        return {
            "role": "admin",
            "modules": AVAILABLE_MODULES
        }
    
    # User comum tem acesso conforme configurado
    try:
        allowed_modules = json.loads(current_user.allowed_modules) if current_user.allowed_modules else []
    except:
        allowed_modules = ["dashboard", "pacientes", "agenda"]
    
    return {
        "role": "user",
        "modules": allowed_modules
    }
