"""
Rotas de Documentos e Pré-cadastro
CRUD completo + Assinatura + Geração de PDF
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.document import DocumentTemplate, PatientDocument, QuickPatientRegistration
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.schemas.document import (
    DocumentTemplateCreate, DocumentTemplateUpdate, DocumentTemplateResponse,
    PatientDocumentCreate, PatientDocumentSign, PatientDocumentResponse,
    PatientDocumentListResponse, QuickPatientRegistrationCreate,
    QuickPatientRegistrationConvert, QuickPatientRegistrationResponse,
    GenerateDocumentFromTemplate, DocumentType
)

router = APIRouter(prefix="/api/v1/documents", tags=["Documentos e Termos"])


# ============================================
# TEMPLATES DE DOCUMENTOS
# ============================================

@router.post("/templates", response_model=DocumentTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template_data: DocumentTemplateCreate, db: Session = Depends(get_db)):
    """Cria um template de documento"""
    template = DocumentTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=List[DocumentTemplateResponse])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    document_type: Optional[DocumentType] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista templates de documentos"""
    query = db.query(DocumentTemplate)
    if document_type:
        query = query.filter(DocumentTemplate.document_type == document_type)
    if category:
        query = query.filter(DocumentTemplate.category == category)
    if is_active is not None:
        query = query.filter(DocumentTemplate.is_active == is_active)
    templates = query.order_by(DocumentTemplate.name).offset(skip).limit(limit).all()
    return templates


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    """Busca um template por ID"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    return template


@router.put("/templates/{template_id}", response_model=DocumentTemplateResponse)
def update_template(template_id: str, template_data: DocumentTemplateUpdate, db: Session = Depends(get_db)):
    """Atualiza um template"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Deleta um template"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    db.delete(template)
    db.commit()
    return {"message": "Template deletado com sucesso", "success": True}


# ============================================
# DOCUMENTOS DO PACIENTE
# ============================================

@router.post("/patient-documents", response_model=PatientDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_patient_document(document_data: PatientDocumentCreate, db: Session = Depends(get_db)):
    """Cria um documento para paciente"""
    patient = db.query(Patient).filter(Patient.id == document_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    document = PatientDocument(**document_data.dict())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("/generate-from-template", response_model=PatientDocumentResponse, status_code=status.HTTP_201_CREATED)
def generate_from_template(data: GenerateDocumentFromTemplate, db: Session = Depends(get_db)):
    """Gera documento a partir de um template"""
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == data.template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    
    content = template.content
    default_vars = {
        '{patient_name}': patient.full_name,
        '{patient_cpf}': patient.cpf or '',
        '{patient_phone}': patient.phone or '',
        '{patient_email}': patient.email or '',
        '{date}': datetime.now().strftime('%d/%m/%Y'),
        '{time}': datetime.now().strftime('%H:%M')
    }
    if data.variables:
        default_vars.update(data.variables)
    for key, value in default_vars.items():
        content = content.replace(key, str(value))
    
    document = PatientDocument(
        patient_id=data.patient_id,
        appointment_id=data.appointment_id,
        template_id=data.template_id,
        document_type=template.document_type,
        title=template.name,
        content=content
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/patient-documents", response_model=List[PatientDocumentListResponse])
def list_patient_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    patient_id: Optional[str] = None,
    appointment_id: Optional[str] = None,
    document_type: Optional[DocumentType] = None,
    is_signed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista documentos de pacientes"""
    query = db.query(PatientDocument)
    if patient_id:
        query = query.filter(PatientDocument.patient_id == patient_id)
    if appointment_id:
        query = query.filter(PatientDocument.appointment_id == appointment_id)
    if document_type:
        query = query.filter(PatientDocument.document_type == document_type)
    if is_signed is not None:
        query = query.filter(PatientDocument.is_signed == is_signed)
    documents = query.order_by(desc(PatientDocument.created_at)).offset(skip).limit(limit).all()
    return documents


@router.get("/patient-documents/{document_id}", response_model=PatientDocumentResponse)
def get_patient_document(document_id: str, db: Session = Depends(get_db)):
    """Busca documento por ID"""
    document = db.query(PatientDocument).filter(PatientDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/patient-documents/{document_id}/sign", response_model=PatientDocumentResponse)
def sign_document(document_id: str, sign_data: PatientDocumentSign, db: Session = Depends(get_db)):
    """Assina um documento"""
    document = db.query(PatientDocument).filter(PatientDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    
    if sign_data.signer_type == "patient":
        document.patient_signature = sign_data.signature
        document.patient_signed_at = datetime.utcnow()
    elif sign_data.signer_type == "witness":
        if not sign_data.witness_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome da testemunha é obrigatório")
        document.witness_name = sign_data.witness_name
        document.witness_signature = sign_data.signature
        document.witness_signed_at = datetime.utcnow()
    elif sign_data.signer_type == "professional":
        document.professional_signature = sign_data.signature
        document.professional_signed_at = datetime.utcnow()
    
    template = db.query(DocumentTemplate).filter(DocumentTemplate.id == document.template_id).first()
    if template:
        requires_all = document.patient_signature and (not template.requires_witness or document.witness_signature)
        if requires_all:
            document.is_signed = True
    else:
        if document.patient_signature:
            document.is_signed = True
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/patient-documents/{document_id}")
def delete_patient_document(document_id: str, db: Session = Depends(get_db)):
    """Deleta documento"""
    document = db.query(PatientDocument).filter(PatientDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    if document.is_signed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Documentos assinados não podem ser deletados")
    db.delete(document)
    db.commit()
    return {"message": "Documento deletado com sucesso", "success": True}


# ============================================
# PRÉ-CADASTRO RÁPIDO
# ============================================

@router.post("/quick-registration", response_model=QuickPatientRegistrationResponse, status_code=status.HTTP_201_CREATED)
def quick_register_patient(registration_data: QuickPatientRegistrationCreate, db: Session = Depends(get_db)):
    """Cria pré-cadastro rápido de paciente"""
    from app.utils import validate_phone
    if not validate_phone(registration_data.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Telefone inválido")
    if registration_data.cpf:
        from app.utils import validate_cpf
        if not validate_cpf(registration_data.cpf):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF inválido")
    registration = QuickPatientRegistration(**registration_data.dict())
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


@router.get("/quick-registration", response_model=List[QuickPatientRegistrationResponse])
def list_quick_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_converted: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista pré-cadastros"""
    query = db.query(QuickPatientRegistration)
    if is_converted is not None:
        query = query.filter(QuickPatientRegistration.is_converted == is_converted)
    registrations = query.order_by(desc(QuickPatientRegistration.created_at)).offset(skip).limit(limit).all()
    return registrations


@router.get("/quick-registration/{registration_id}", response_model=QuickPatientRegistrationResponse)
def get_quick_registration(registration_id: str, db: Session = Depends(get_db)):
    """Busca pré-cadastro por ID"""
    registration = db.query(QuickPatientRegistration).filter(QuickPatientRegistration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pré-cadastro não encontrado")
    return registration


@router.post("/quick-registration/{registration_id}/convert")
def convert_to_patient(registration_id: str, convert_data: QuickPatientRegistrationConvert, db: Session = Depends(get_db)):
    """Converte pré-cadastro em paciente completo"""
    registration = db.query(QuickPatientRegistration).filter(QuickPatientRegistration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pré-cadastro não encontrado")
    if registration.is_converted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pré-cadastro já foi convertido")
    
    patient_data = {
        "full_name": registration.full_name,
        "phone": registration.phone,
        "cpf": registration.cpf,
        "email": registration.email,
        "birth_date": registration.birth_date
    }
    if convert_data.additional_data:
        patient_data.update(convert_data.additional_data)
    
    patient = Patient(**patient_data)
    db.add(patient)
    db.flush()
    
    registration.is_converted = True
    registration.patient_id = patient.id
    registration.converted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(patient)
    
    return {"message": "Pré-cadastro convertido com sucesso", "patient_id": patient.id, "success": True}


@router.delete("/quick-registration/{registration_id}")
def delete_quick_registration(registration_id: str, db: Session = Depends(get_db)):
    """Deleta pré-cadastro"""
    registration = db.query(QuickPatientRegistration).filter(QuickPatientRegistration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pré-cadastro não encontrado")
    if registration.is_converted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pré-cadastros convertidos não podem ser deletados")
    db.delete(registration)
    db.commit()
    return {"message": "Pré-cadastro deletado com sucesso", "success": True}
