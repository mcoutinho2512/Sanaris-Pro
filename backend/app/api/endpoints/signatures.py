from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import hashlib
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.signature import Signature, SignatureType, SignatureStatus
from app.schemas.signature import SignatureCreate, SignatureResponse
from app.models.prescription import Prescription

router = APIRouter()


def generate_document_hash(document_id: str) -> str:
    """Gera hash SHA-256 do documento"""
    return hashlib.sha256(document_id.encode()).hexdigest()


@router.post("/sign/simple", response_model=SignatureResponse)
async def sign_document_simple(
    data: SignatureCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Assinatura eletrônica simples
    Usa autenticação do usuário logado
    """
    
    # Gerar hash do documento
    doc_hash = generate_document_hash(data.document_id)
    
    # Criar assinatura
    signature = Signature(
        document_type=data.document_type,
        document_id=data.document_id,
        document_hash=doc_hash,
        signer_id=current_user.id,
        signer_name=current_user.full_name,
        signer_cpf=data.signer_cpf,
        signer_crm=data.signer_crm,
        signature_type=SignatureType.SIMPLE,
        status=SignatureStatus.SIGNED,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        is_valid=True,
        signed_at=datetime.utcnow()
    )
    
    db.add(signature)
    
    # Se for prescrição, atualizar status
    if data.document_type == "prescription":
        prescription = db.query(Prescription).filter(
            Prescription.id == data.document_id
        ).first()
        if prescription:
            prescription.is_signed = True
            prescription.signed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(signature)
    
    return signature


@router.get("/document/{document_id}", response_model=List[SignatureResponse])
async def get_document_signatures(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as assinaturas de um documento"""
    
    signatures = db.query(Signature).filter(
        Signature.document_id == document_id
    ).all()
    
    return signatures


@router.get("/validate/{signature_id}")
async def validate_signature(
    signature_id: str,
    db: Session = Depends(get_db)
):
    """Valida uma assinatura"""
    
    signature = db.query(Signature).filter(Signature.id == signature_id).first()
    
    if not signature:
        raise HTTPException(status_code=404, detail="Assinatura não encontrada")
    
    return {
        "valid": signature.is_valid,
        "status": signature.status,
        "signer_name": signature.signer_name,
        "signer_cpf": signature.signer_cpf,
        "signed_at": signature.signed_at,
        "signature_type": signature.signature_type
    }
