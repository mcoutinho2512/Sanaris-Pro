"""
Rotas de Assinatura Digital Avançada
ICP-Brasil e OTP
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.digital_signature import (
    DigitalCertificate, OTPConfiguration, SignatureLog,
    SignatureType, SignatureStatus
)
from app.schemas.digital_signature import (
    DigitalCertificateCreate, DigitalCertificateUpdate, DigitalCertificateResponse,
    OTPConfigurationCreate, OTPConfigurationUpdate, OTPConfigurationResponse,
    SignWithICPBrasil, SignWithOTP, SignWithBasicCRM,
    GenerateOTPRequest, GenerateOTPResponse,
    SignatureResponse, SignatureLogResponse,
    ValidateSignatureRequest, ValidateSignatureResponse
)
from app.services.signature_service import signature_service

router = APIRouter(prefix="/api/v1/signatures", tags=["Assinatura Digital"])


# ============================================
# CERTIFICADOS ICP-BRASIL
# ============================================

@router.post("/certificates", response_model=DigitalCertificateResponse, status_code=status.HTTP_201_CREATED)
def upload_certificate(cert_data: DigitalCertificateCreate, db: Session = Depends(get_db)):
    """Upload de certificado digital ICP-Brasil"""
    
    # Verifica se já existe certificado ativo
    existing = db.query(DigitalCertificate).filter(
        DigitalCertificate.healthcare_professional_id == cert_data.healthcare_professional_id,
        DigitalCertificate.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um certificado ativo. Desative o anterior primeiro."
        )
    
    # Valida certificado
    validation = signature_service.verify_certificate_icp(
        cert_data.certificate_data,
        cert_data.certificate_password
    )
    
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificado inválido"
        )
    
    # Verifica se está expirado
    is_expired = cert_data.valid_until < datetime.utcnow()
    
    # Criptografa senha
    encrypted_password = signature_service.encrypt_data(cert_data.certificate_password)
    
    # Cria certificado
    certificate = DigitalCertificate(
        healthcare_professional_id=cert_data.healthcare_professional_id,
        certificate_type=cert_data.certificate_type,
        certificate_data=cert_data.certificate_data,
        certificate_password_encrypted=encrypted_password,
        holder_name=cert_data.holder_name,
        holder_cpf=cert_data.holder_cpf,
        holder_crm=cert_data.holder_crm,
        holder_email=cert_data.holder_email,
        valid_from=cert_data.valid_from,
        valid_until=cert_data.valid_until,
        is_expired=is_expired,
        issuer_name=cert_data.issuer_name,
        serial_number=cert_data.serial_number
    )
    
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    
    return certificate


@router.get("/certificates/{professional_id}", response_model=List[DigitalCertificateResponse])
def list_certificates(professional_id: str, db: Session = Depends(get_db)):
    """Lista certificados do profissional"""
    
    certificates = db.query(DigitalCertificate).filter(
        DigitalCertificate.healthcare_professional_id == professional_id
    ).order_by(desc(DigitalCertificate.created_at)).all()
    
    return certificates


@router.get("/certificates/detail/{certificate_id}", response_model=DigitalCertificateResponse)
def get_certificate(certificate_id: str, db: Session = Depends(get_db)):
    """Busca certificado por ID"""
    
    certificate = db.query(DigitalCertificate).filter(DigitalCertificate.id == certificate_id).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado não encontrado"
        )
    
    return certificate


@router.put("/certificates/{certificate_id}", response_model=DigitalCertificateResponse)
def update_certificate(
    certificate_id: str,
    cert_data: DigitalCertificateUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza certificado"""
    
    certificate = db.query(DigitalCertificate).filter(DigitalCertificate.id == certificate_id).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado não encontrado"
        )
    
    update_data = cert_data.dict(exclude_unset=True)
    
    # Se tem nova senha, criptografa
    if 'certificate_password' in update_data:
        update_data['certificate_password_encrypted'] = signature_service.encrypt_data(
            update_data.pop('certificate_password')
        )
    
    for field, value in update_data.items():
        setattr(certificate, field, value)
    
    db.commit()
    db.refresh(certificate)
    
    return certificate


@router.delete("/certificates/{certificate_id}")
def delete_certificate(certificate_id: str, db: Session = Depends(get_db)):
    """Deleta certificado"""
    
    certificate = db.query(DigitalCertificate).filter(DigitalCertificate.id == certificate_id).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado não encontrado"
        )
    
    db.delete(certificate)
    db.commit()
    
    return {"message": "Certificado deletado com sucesso", "success": True}


# ============================================
# CONFIGURAÇÃO OTP
# ============================================

@router.post("/otp/configure", response_model=OTPConfigurationResponse, status_code=status.HTTP_201_CREATED)
def configure_otp(otp_data: OTPConfigurationCreate, db: Session = Depends(get_db)):
    """Configura OTP para o profissional"""
    
    # Verifica se já existe
    existing = db.query(OTPConfiguration).filter(
        OTPConfiguration.healthcare_professional_id == otp_data.healthcare_professional_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP já configurado. Use PUT para atualizar."
        )
    
    # Gera chave secreta
    secret_key = signature_service.generate_hash(f"{otp_data.healthcare_professional_id}{datetime.utcnow()}")
    encrypted_secret = signature_service.encrypt_data(secret_key)
    
    # Cria configuração
    config = OTPConfiguration(
        healthcare_professional_id=otp_data.healthcare_professional_id,
        secret_key_encrypted=encrypted_secret,
        phone_number=otp_data.phone_number,
        email=otp_data.email,
        otp_method=otp_data.otp_method.value,
        otp_length=otp_data.otp_length,
        otp_validity_minutes=otp_data.otp_validity_minutes
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.get("/otp/config/{professional_id}", response_model=OTPConfigurationResponse)
def get_otp_config(professional_id: str, db: Session = Depends(get_db)):
    """Busca configuração OTP"""
    
    config = db.query(OTPConfiguration).filter(
        OTPConfiguration.healthcare_professional_id == professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP não configurado"
        )
    
    return config


@router.put("/otp/config/{professional_id}", response_model=OTPConfigurationResponse)
def update_otp_config(
    professional_id: str,
    otp_data: OTPConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza configuração OTP"""
    
    config = db.query(OTPConfiguration).filter(
        OTPConfiguration.healthcare_professional_id == professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP não configurado"
        )
    
    update_data = otp_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config


# ============================================
# GERAÇÃO E ENVIO DE OTP
# ============================================

# Armazenamento temporário de OTPs (em produção, usar Redis)
otp_storage = {}

@router.post("/otp/generate", response_model=GenerateOTPResponse)
def generate_otp(otp_request: GenerateOTPRequest, db: Session = Depends(get_db)):
    """Gera e envia código OTP"""
    
    # Busca configuração
    config = db.query(OTPConfiguration).filter(
        OTPConfiguration.healthcare_professional_id == otp_request.healthcare_professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP não configurado"
        )
    
    if not config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP desativado"
        )
    
    # Gera código
    otp_code = signature_service.generate_otp(config.otp_length)
    
    # Armazena temporariamente
    storage_key = f"{otp_request.healthcare_professional_id}:{otp_request.document_id}"
    otp_storage[storage_key] = {
        "code": otp_code,
        "created_at": datetime.utcnow(),
        "validity_minutes": config.otp_validity_minutes
    }
    
    # Define destino
    destination = config.phone_number if config.otp_method == "sms" else config.email
    
    # Envia OTP
    result = signature_service.send_otp(
        method=config.otp_method,
        destination=destination,
        otp_code=otp_code
    )
    
    if result['success']:
        config.total_otps_sent += 1
        db.commit()
    
    expires_at = datetime.utcnow() + timedelta(minutes=config.otp_validity_minutes)
    
    return GenerateOTPResponse(
        success=result['success'],
        message=result['message'],
        otp_sent_to=destination,
        otp_method=config.otp_method,
        expires_at=expires_at
    )


# ============================================
# ASSINATURA DE DOCUMENTOS
# ============================================

@router.post("/sign/icp-brasil", response_model=SignatureResponse)
def sign_with_icp_brasil(
    sign_data: SignWithICPBrasil,
    request: Request,
    db: Session = Depends(get_db)
):
    """Assina documento com certificado ICP-Brasil"""
    
    # Busca certificado
    certificate = db.query(DigitalCertificate).filter(
        DigitalCertificate.id == sign_data.certificate_id
    ).first()
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado não encontrado"
        )
    
    if not certificate.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificado inativo"
        )
    
    if certificate.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificado expirado"
        )
    
    # Descriptografa senha
    stored_password = signature_service.decrypt_data(certificate.certificate_password_encrypted)
    
    if stored_password != sign_data.certificate_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha do certificado incorreta"
        )
    
    # Assina documento
    document_data = f"{sign_data.document_type}:{sign_data.document_id}"
    
    result = signature_service.sign_with_icp(
        document_data=document_data,
        certificate_data=certificate.certificate_data,
        password=sign_data.certificate_password
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result['message']
        )
    
    # Cria log
    log = SignatureLog(
        document_type=sign_data.document_type,
        document_id=sign_data.document_id,
        healthcare_professional_id=sign_data.healthcare_professional_id,
        signature_type=SignatureType.ICP_BRASIL,
        signature_data=result['signature_data'],
        signature_hash=result['signature_hash'],
        certificate_id=certificate.id,
        certificate_serial=certificate.serial_number,
        status=SignatureStatus.SIGNED,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        signed_at=result['signed_at']
    )
    
    db.add(log)
    
    # Atualiza estatísticas
    certificate.total_signatures += 1
    certificate.last_used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(log)
    
    return SignatureResponse(
        success=True,
        message="Documento assinado com ICP-Brasil",
        signature_id=log.id,
        signature_type="icp_brasil",
        signed_at=log.signed_at,
        signature_hash=log.signature_hash
    )


@router.post("/sign/otp", response_model=SignatureResponse)
def sign_with_otp(
    sign_data: SignWithOTP,
    request: Request,
    db: Session = Depends(get_db)
):
    """Assina documento com OTP"""
    
    # Busca configuração
    config = db.query(OTPConfiguration).filter(
        OTPConfiguration.healthcare_professional_id == sign_data.healthcare_professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP não configurado"
        )
    
    # Verifica OTP
    storage_key = f"{sign_data.healthcare_professional_id}:{sign_data.document_id}"
    stored_otp = otp_storage.get(storage_key)
    
    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP não gerado ou expirado. Gere um novo código."
        )
    
    # Valida OTP
    is_valid = signature_service.verify_otp(
        provided_otp=sign_data.otp_code,
        stored_otp=stored_otp['code'],
        created_at=stored_otp['created_at'],
        validity_minutes=stored_otp['validity_minutes']
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código OTP inválido ou expirado"
        )
    
    # Remove OTP usado
    del otp_storage[storage_key]
    
    # Assina documento
    document_data = f"{sign_data.document_type}:{sign_data.document_id}"
    
    result = signature_service.sign_with_otp(
        document_data=document_data,
        otp_code=sign_data.otp_code
    )
    
    # Cria log
    log = SignatureLog(
        document_type=sign_data.document_type,
        document_id=sign_data.document_id,
        healthcare_professional_id=sign_data.healthcare_professional_id,
        signature_type=SignatureType.OTP,
        signature_data=result['signature_data'],
        signature_hash=result['signature_hash'],
        otp_code="USED",  # Não armazenar código real
        otp_sent_to=config.phone_number if config.otp_method == "sms" else config.email,
        otp_verified_at=datetime.utcnow(),
        status=SignatureStatus.SIGNED,
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        signed_at=result['signed_at']
    )
    
    db.add(log)
    
    # Atualiza estatísticas
    config.total_signatures += 1
    config.last_used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(log)
    
    return SignatureResponse(
        success=True,
        message="Documento assinado com OTP",
        signature_id=log.id,
        signature_type="otp",
        signed_at=log.signed_at,
        signature_hash=log.signature_hash
    )


# ============================================
# LOGS E VALIDAÇÃO
# ============================================

@router.get("/logs", response_model=List[SignatureLogResponse])
def list_signature_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    professional_id: Optional[str] = None,
    document_type: Optional[str] = None,
    signature_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista logs de assinaturas"""
    
    query = db.query(SignatureLog)
    
    if professional_id:
        query = query.filter(SignatureLog.healthcare_professional_id == professional_id)
    if document_type:
        query = query.filter(SignatureLog.document_type == document_type)
    if signature_type:
        query = query.filter(SignatureLog.signature_type == signature_type)
    
    logs = query.order_by(desc(SignatureLog.created_at)).offset(skip).limit(limit).all()
    
    return logs
