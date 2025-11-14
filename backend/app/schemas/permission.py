from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserPermissionBase(BaseModel):
    user_id: UUID
    permission_id: UUID

class UserPermissionCreate(BaseModel):
    permission_ids: List[UUID]

class UserPermissionResponse(BaseModel):
    id: UUID
    user_id: UUID
    permission_id: UUID
    granted_by_id: Optional[UUID]
    granted_at: datetime
    
    class Config:
        from_attributes = True

class UserPermissionsDetail(BaseModel):
    user_id: UUID
    permissions: List[PermissionResponse]
