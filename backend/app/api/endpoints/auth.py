from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse
import httpx

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user
)
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    Token,
    UserCreate,
    UserResponse,
    LoginRequest,
    GoogleCallbackResponse
)

router = APIRouter()

# Configurar OAuth
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# ============================================================
# AUTENTICAÇÃO TRADICIONAL
# ============================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar novo usuário com email e senha"""
    
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Criar usuário
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        email_verified=False,
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login com email e senha"""
    
    # Buscar usuário
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar senha
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Atualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login com email e senha (formato JSON)"""
    
    # Buscar usuário
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verificar senha
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verificar se está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Atualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# ============================================================
# GOOGLE OAUTH
# ============================================================

@router.get("/google/login")
async def google_login(request: Request):
    """Iniciar login com Google"""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Callback do Google OAuth"""
    
    try:
        # Obter token do Google
        token = await oauth.google.authorize_access_token(request)
        
        # Obter informações do usuário
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')
        picture = user_info.get('picture')
        email_verified = user_info.get('email_verified', False)
        
        # Buscar usuário existente
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        if user:
            # Atualizar usuário existente
            user.google_id = google_id
            user.google_access_token = token.get('access_token')
            user.google_refresh_token = token.get('refresh_token')
            user.picture = picture
            user.email_verified = email_verified
            user.last_login = datetime.utcnow()
            user.is_active = True
        else:
            # Criar novo usuário
            user = User(
                email=email,
                full_name=full_name,
                google_id=google_id,
                google_access_token=token.get('access_token'),
                google_refresh_token=token.get('refresh_token'),
                picture=picture,
                email_verified=email_verified,
                is_active=True,
                is_superuser=False,
                last_login=datetime.utcnow()
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Criar token JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Redirecionar para frontend com token
        frontend_url = f"http://localhost:3001/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


# ============================================================
# USUÁRIO ATUAL
# ============================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Obter informações do usuário logado"""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout (limpar tokens do Google se existir)"""
    
    if current_user.google_access_token:
        current_user.google_access_token = None
        current_user.google_refresh_token = None
        db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todos os usuários (apenas admin)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar usuários"
        )
    
    users = db.query(User).all()
    return users

@router.put("/change-password")
def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trocar senha do usuário logado
    """
    from app.core.security import verify_password, get_password_hash
    
    # Verificar senha antiga
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Senha atual incorreta"
        )
    
    # Validar nova senha
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="A nova senha deve ter pelo menos 6 caracteres"
        )
    
    if old_password == new_password:
        raise HTTPException(
            status_code=400,
            detail="A nova senha deve ser diferente da senha atual"
        )
    
    # Atualizar senha
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {
        "message": "Senha alterada com sucesso",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name
        }
    }


# ==================== RECUPERAÇÃO DE SENHA ====================

@router.post("/forgot-password")
def request_password_reset(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Solicitar reset de senha - Gera token e 'envia' email
    """
    import secrets
    import hashlib
    from datetime import timedelta
    from app.models.password_reset_token import PasswordResetToken
    
    # Buscar usuário
    user = db.query(User).filter(User.email == email).first()
    
    # SEMPRE retornar sucesso (segurança - não revelar se email existe)
    if not user:
        return {
            "message": "Se o email existir no sistema, você receberá um link de recuperação."
        }
    
    # Gerar token único
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    # Invalidar tokens anteriores do usuário
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})
    
    # Criar novo token (válido por 15 minutos)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    
    db.add(reset_token)
    db.commit()
    
    # AQUI: Em produção, enviar email com o link
    # reset_link = f"http://localhost:3001/reset-password?token={raw_token}"
    # send_email(user.email, "Recuperação de Senha", reset_link)
    
    # POR ENQUANTO: Log do token (REMOVER EM PRODUÇÃO!)
    print(f"\n{'='*60}")
    print(f"🔐 TOKEN DE RECUPERAÇÃO PARA: {user.email}")
    print(f"Token: {raw_token}")
    print(f"Link: http://localhost:3001/reset-password?token={raw_token}")
    print(f"Válido até: {reset_token.expires_at}")
    print(f"{'='*60}\n")
    
    return {
        "message": "Se o email existir no sistema, você receberá um link de recuperação.",
        "dev_token": raw_token  # REMOVER EM PRODUÇÃO!
    }


@router.post("/reset-password")
def reset_password_with_token(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Resetar senha usando token
    """
    import hashlib
    from app.models.password_reset_token import PasswordResetToken
    from app.core.security import get_password_hash
    
    # Validar nova senha
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="A senha deve ter pelo menos 6 caracteres"
        )
    
    # Hash do token recebido
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Buscar token
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado"
        )
    
    # Verificar se é válido
    if not reset_token.is_valid():
        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    # Atualizar senha
    user.hashed_password = get_password_hash(new_password)
    
    # Marcar token como usado
    reset_token.is_used = True
    reset_token.used_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Senha alterada com sucesso! Faça login com sua nova senha.",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name
        }
    }


@router.get("/verify-reset-token/{token}")
def verify_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verificar se token é válido (sem usar)
    """
    import hashlib
    from app.models.password_reset_token import PasswordResetToken
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()
    
    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado"
        )
    
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    
    return {
        "valid": True,
        "user_email": user.email if user else None,
        "expires_at": reset_token.expires_at.isoformat()
    }
