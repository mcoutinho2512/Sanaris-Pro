from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class MedicationBase(BaseModel):
    anvisa_registry: Optional[str] = None
    commercial_name: str = Field(..., min_length=1, max_length=500)
    active_ingredient: str = Field(..., min_length=1, max_length=500)
    presentation: Optional[str] = None
    concentration: Optional[str] = None
    pharmaceutical_form: Optional[str] = None
    manufacturer: Optional[str] = None
    therapeutic_class: Optional[str] = None
    requires_prescription: int = 1
    ean_code: Optional[str] = None
    pmc: Optional[str] = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    commercial_name: Optional[str] = None
    active_ingredient: Optional[str] = None
    presentation: Optional[str] = None
    concentration: Optional[str] = None
    pharmaceutical_form: Optional[str] = None
    manufacturer: Optional[str] = None
    therapeutic_class: Optional[str] = None
    requires_prescription: Optional[int] = None
    pmc: Optional[str] = None


class MedicationResponse(MedicationBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MedicationSearchResult(BaseModel):
    id: UUID
    commercial_name: str
    active_ingredient: str
    presentation: Optional[str] = None
    manufacturer: Optional[str] = None
    requires_prescription: int
    
    class Config:
        from_attributes = True
