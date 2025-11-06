from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    LogoUploadResponse
)

router = APIRouter()

UPLOAD_DIR = Path("/home/administrador/sanaris-pro/sanaris/uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(organization_data: OrganizationCreate, db: Session = Depends(get_db)):
    if organization_data.cnpj:
        existing = db.query(Organization).filter(Organization.cnpj == organization_data.cnpj).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ já cadastrado")
    new_org = Organization(**organization_data.dict())
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Organization).filter(Organization.deleted_at.is_(None)).offset(skip).limit(limit).all()

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: str, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id, Organization.deleted_at.is_(None)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")
    return org

@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(organization_id: str, organization_data: OrganizationUpdate, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id, Organization.deleted_at.is_(None)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")
    for field, value in organization_data.dict(exclude_unset=True).items():
        setattr(org, field, value)
    org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(org)
    return org

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(organization_id: str, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id, Organization.deleted_at.is_(None)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")
    org.deleted_at = datetime.utcnow()
    org.is_active = False
    db.commit()
    return None

@router.post("/{organization_id}/upload-logo", response_model=LogoUploadResponse)
async def upload_logo(organization_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id, Organization.deleted_at.is_(None)).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organização não encontrada")
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Extensão não permitida")
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Arquivo muito grande")
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logo_url = f"/uploads/logos/{unique_filename}"
    org.logo_url = logo_url
    org.updated_at = datetime.utcnow()
    db.commit()
    return {"logo_url": logo_url, "message": "Logo enviada com sucesso!"}
