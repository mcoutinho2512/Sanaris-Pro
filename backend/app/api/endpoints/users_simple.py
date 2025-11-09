from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UserSimple(BaseModel):
    id: UUID
    full_name: str
    email: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserSimple])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar usuários da mesma organização"""
    
    users = db.query(User).filter(
        User.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    
    return users
