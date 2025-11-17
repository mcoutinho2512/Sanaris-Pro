from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.permission import Permission, UserPermission
from app.schemas.permission import (
    PermissionResponse,
    UserPermissionCreate,
    UserPermissionsDetail
)

router = APIRouter()


@router.get("/", response_model=List[PermissionResponse])
def list_all_permissions(db: Session = Depends(get_db)):
    """Lista todas as permissões disponíveis no sistema"""
    permissions = db.query(Permission).order_by(Permission.module, Permission.action).all()
    return permissions


@router.get("/my-permissions", response_model=List[str])
def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna lista de nomes de permissões do usuário atual"""
    
    # Super admin tem todas as permissões
    if current_user.role == 'super_admin':
        all_perms = db.query(Permission.name).all()
        return [p[0] for p in all_perms]
    
    # Admin tem todas menos manage_users
    if current_user.role == 'admin':
        all_perms = db.query(Permission.name).filter(
            Permission.name != 'manage_users'
        ).all()
        return [p[0] for p in all_perms]
    
    # Usuários básicos: buscar permissões específicas
    user_perms = db.query(Permission.name).join(
        UserPermission, UserPermission.permission_id == Permission.id
    ).filter(
        UserPermission.user_id == current_user.id
    ).all()
    
    return [p[0] for p in user_perms]


@router.get("/my-modules", response_model=List[str])
def get_my_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna lista de módulos que o usuário tem acesso"""
    
    # Super admin e admin têm acesso a todos
    if current_user.role in ['super_admin', 'admin']:
        return [
            "dashboard", "pacientes", "agenda", "prontuarios", 
            "prescricoes", "cfm", "relatorios", "chat"
        ]
    
    # Usuários básicos: retornar allowed_modules
    if current_user.allowed_modules:
        modules = current_user.allowed_modules
        
        # Se for string (formato PostgreSQL ARRAY {a,b,c}), converter para lista
        if isinstance(modules, str):
            # Remover { } e dividir por vírgula
            modules = modules.strip('{}').split(',')
            # Limpar espaços
            modules = [m.strip() for m in modules if m.strip()]
        
        return modules
    
    # Se não tiver módulos definidos, retornar vazio
    return []


@router.get("/user/{user_id}", response_model=UserPermissionsDetail)
def get_user_permissions(user_id: UUID, db: Session = Depends(get_db)):
    """Retorna permissões de um usuário específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    permissions = db.query(Permission).join(
        UserPermission, UserPermission.permission_id == Permission.id
    ).filter(
        UserPermission.user_id == user_id
    ).all()
    
    return UserPermissionsDetail(user_id=user_id, permissions=permissions)


@router.post("/user/{user_id}", status_code=status.HTTP_201_CREATED)
def assign_permissions_to_user(
    user_id: UUID,
    permissions_data: UserPermissionCreate,
    db: Session = Depends(get_db)
):
    """Atribui permissões a um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Remover permissões antigas
    db.query(UserPermission).filter(UserPermission.user_id == user_id).delete()
    
    # Adicionar novas permissões
    for perm_id in permissions_data.permission_ids:
        user_perm = UserPermission(
            user_id=user_id,
            permission_id=perm_id,
            granted_by_id=None
        )
        db.add(user_perm)
    
    db.commit()
    
    return {
        "message": "Permissões atualizadas com sucesso",
        "user_id": str(user_id),
        "permissions_count": len(permissions_data.permission_ids)
    }


@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_all_permissions(user_id: UUID, db: Session = Depends(get_db)):
    """Remove todas as permissões de um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.query(UserPermission).filter(UserPermission.user_id == user_id).delete()
    db.commit()
