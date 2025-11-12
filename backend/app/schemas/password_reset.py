from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitação de recuperação de senha"""
    recovery_email: EmailStr = Field(..., description="Email de recuperação do usuário")


class ResetPasswordRequest(BaseModel):
    """Schema para redefinição de senha com token"""
    token: str = Field(..., description="Token de recuperação")
    new_password: str = Field(..., min_length=6, description="Nova senha (mínimo 6 caracteres)")


class PasswordResetResponse(BaseModel):
    """Schema para resposta de recuperação de senha"""
    message: str


class TokenValidationResponse(BaseModel):
    """Schema para resposta de validação de token"""
    valid: bool
    user_email: Optional[str] = None
    recovery_email: Optional[str] = None
    message: Optional[str] = None
