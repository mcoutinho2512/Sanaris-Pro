from pydantic import BaseModel
from typing import Optional

class OrganizationBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationInDB(OrganizationBase):
    id: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True

class Organization(OrganizationInDB):
    pass

class OrganizationResponse(OrganizationInDB):
    pass

class OrganizationSimple(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True
