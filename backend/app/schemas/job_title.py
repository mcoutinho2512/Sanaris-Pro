from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class JobTitleBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nome do cargo")
    department: str = Field(..., max_length=50, description="Departamento (Médico, Administrativo, etc)")
    is_healthcare_professional: bool = Field(default=False, description="Se pode atender pacientes")
    can_schedule_appointments: bool = Field(default=True, description="Se pode agendar consultas")
    description: Optional[str] = Field(None, max_length=255, description="Descrição do cargo")

class JobTitleCreate(JobTitleBase):
    pass

class JobTitleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    is_healthcare_professional: Optional[bool] = None
    can_schedule_appointments: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

class JobTitleResponse(JobTitleBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
