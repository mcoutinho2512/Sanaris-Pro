"""
Rotas de Integração CFM
Autenticação, Envio e Sincronização
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.models.cfm_integration import CFMCredentials, CFMPrescriptionLog
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.schemas.cfm_integration import (
    CFMCredentialsCreate, CFMCredentialsUpdate, CFMCredentialsResponse,
    CFMLoginRequest, CFMLoginResponse, CFMLogoutRequest,
    CFMPrescriptionSend, CFMPrescriptionSendResponse,
    CFMPrescriptionLogResponse, CFMSyncRequest, CFMSyncResponse,
    CFMConnectionStatus
)
from app.services.cfm_service import cfm_service

router = APIRouter(prefix="/api/v1/cfm", tags=["Integração CFM"])


# ============================================
# CREDENCIAIS CFM
# ============================================

@router.post("/credentials", response_model=CFMCredentialsResponse, status_code=status.HTTP_201_CREATED)
def create_cfm_credentials(cred_data: CFMCredentialsCreate, db: Session = Depends(get_db)):
    """Cadastra credenciais CFM do profissional"""
    
    # Verifica se já existe
    existing = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == cred_data.healthcare_professional_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciais CFM já cadastradas para este profissional"
        )
    
    # Criptografa senha
    encrypted_password = cfm_service.encrypt_password(cred_data.cfm_password)
    
    # Cria credenciais
    credentials = CFMCredentials(
        healthcare_professional_id=cred_data.healthcare_professional_id,
        crm_number=cred_data.crm_number,
        crm_state=cred_data.crm_state,
        cfm_username=cred_data.cfm_username,
        cfm_password_encrypted=encrypted_password,
        auto_sync=cred_data.auto_sync,
        sync_interval_minutes=cred_data.sync_interval_minutes
    )
    
    db.add(credentials)
    db.commit()
    db.refresh(credentials)
    
    return credentials


@router.get("/credentials/{professional_id}", response_model=CFMCredentialsResponse)
def get_cfm_credentials(professional_id: str, db: Session = Depends(get_db)):
    """Busca credenciais CFM do profissional"""
    
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    return credentials


@router.put("/credentials/{professional_id}", response_model=CFMCredentialsResponse)
def update_cfm_credentials(
    professional_id: str,
    cred_data: CFMCredentialsUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza credenciais CFM"""
    
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    # Atualiza campos
    update_data = cred_data.dict(exclude_unset=True)
    
    # Se tem nova senha, criptografa
    if 'cfm_password' in update_data:
        update_data['cfm_password_encrypted'] = cfm_service.encrypt_password(update_data.pop('cfm_password'))
    
    for field, value in update_data.items():
        setattr(credentials, field, value)
    
    db.commit()
    db.refresh(credentials)
    
    return credentials


@router.delete("/credentials/{professional_id}")
def delete_cfm_credentials(professional_id: str, db: Session = Depends(get_db)):
    """Deleta credenciais CFM"""
    
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    db.delete(credentials)
    db.commit()
    
    return {"message": "Credenciais deletadas com sucesso", "success": True}


# ============================================
# AUTENTICAÇÃO CFM
# ============================================

@router.post("/login", response_model=CFMLoginResponse)
def login_cfm(login_data: CFMLoginRequest, db: Session = Depends(get_db)):
    """Faz login no sistema CFM"""
    
    # Busca credenciais
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == login_data.healthcare_professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas. Configure primeiro."
        )
    
    # Descriptografa senha
    password = cfm_service.decrypt_password(credentials.cfm_password_encrypted)
    
    # Faz login no CFM
    result = cfm_service.login(
        username=credentials.cfm_username,
        password=password,
        crm=credentials.crm_number,
        uf=credentials.crm_state
    )
    
    if result['success']:
        # Salva tokens
        credentials.access_token = result['access_token']
        credentials.refresh_token = result['refresh_token']
        credentials.token_expires_at = result['expires_at']
        credentials.is_connected = True
        credentials.last_sync_at = datetime.utcnow()
        
        db.commit()
        
        return CFMLoginResponse(
            success=True,
            message="Login no CFM realizado com sucesso",
            is_connected=True,
            expires_at=result['expires_at']
        )
    else:
        return CFMLoginResponse(
            success=False,
            message=result.get('message', 'Erro ao fazer login no CFM'),
            is_connected=False
        )


@router.post("/logout")
def logout_cfm(logout_data: CFMLogoutRequest, db: Session = Depends(get_db)):
    """Faz logout do sistema CFM"""
    
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == logout_data.healthcare_professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    # Logout no CFM
    if credentials.access_token:
        cfm_service.logout(credentials.access_token)
    
    # Limpa tokens
    credentials.access_token = None
    credentials.refresh_token = None
    credentials.token_expires_at = None
    credentials.is_connected = False
    
    db.commit()
    
    return {"message": "Logout realizado com sucesso", "success": True}


@router.get("/status/{professional_id}", response_model=CFMConnectionStatus)
def get_cfm_status(professional_id: str, db: Session = Depends(get_db)):
    """Retorna status de conexão com CFM"""
    
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    return CFMConnectionStatus(
        healthcare_professional_id=professional_id,
        is_connected=credentials.is_connected,
        crm_number=credentials.crm_number,
        crm_state=credentials.crm_state,
        last_sync_at=credentials.last_sync_at,
        total_prescriptions_sent=credentials.total_prescriptions_sent,
        token_expires_at=credentials.token_expires_at
    )


# ============================================
# ENVIO DE PRESCRIÇÕES
# ============================================

@router.post("/send-prescription", response_model=CFMPrescriptionSendResponse)
def send_prescription_to_cfm(send_data: CFMPrescriptionSend, db: Session = Depends(get_db)):
    """Envia prescrição para o sistema CFM"""
    
    # Busca credenciais
    credentials = db.query(CFMCredentials).filter(
        CFMCredentials.healthcare_professional_id == send_data.healthcare_professional_id
    ).first()
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciais CFM não encontradas"
        )
    
    if not credentials.is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não conectado ao CFM. Faça login primeiro."
        )
    
    # Busca prescrição
    prescription = db.query(Prescription).filter(Prescription.id == send_data.prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser enviadas ao CFM"
        )
    
    # Busca paciente
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    
    # Prepara dados
    patient_data = {
        "name": patient.full_name,
        "cpf": patient.cpf,
        "birth_date": patient.birth_date.isoformat() if patient.birth_date else None,
        "phone": patient.phone
    }
    
    professional_data = {
        "crm": credentials.crm_number,
        "uf": credentials.crm_state,
        "name": ""  # TODO: buscar nome do profissional
    }
    
    medications = [
        {
            "name": item.medication_name,
            "dosage": item.dosage,
            "frequency": item.frequency,
            "duration": item.duration,
            "instructions": item.instructions,
            "quantity": item.quantity
        }
        for item in prescription.items
    ]
    
    # Envia para CFM
    result = cfm_service.send_prescription(
        access_token=credentials.access_token,
        patient_data=patient_data,
        medications=medications,
        professional_data=professional_data
    )
    
    # Cria log
    log = CFMPrescriptionLog(
        prescription_id=prescription.id,
        cfm_credentials_id=credentials.id,
        status="sent" if result['success'] else "error",
        error_message=result.get('error'),
        sent_at=datetime.utcnow() if result['success'] else None
    )
    
    if result['success']:
        log.cfm_prescription_id = result.get('cfm_prescription_id')
        log.cfm_validation_code = result.get('validation_code')
        log.cfm_url = result.get('url')
        log.confirmed_at = datetime.utcnow()
        log.status = "confirmed"
        
        # Atualiza credenciais
        credentials.total_prescriptions_sent += 1
        credentials.last_prescription_sent_at = datetime.utcnow()
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return CFMPrescriptionSendResponse(
        success=result['success'],
        message=result.get('message'),
        cfm_prescription_id=result.get('cfm_prescription_id'),
        cfm_validation_code=result.get('validation_code'),
        cfm_url=result.get('url'),
        sent_at=log.sent_at
    )


# ============================================
# LOGS E HISTÓRICO
# ============================================

@router.get("/logs", response_model=List[CFMPrescriptionLogResponse])
def list_cfm_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    professional_id: Optional[str] = None,
    prescription_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista logs de prescrições enviadas ao CFM"""
    
    query = db.query(CFMPrescriptionLog)
    
    if professional_id:
        credentials = db.query(CFMCredentials).filter(
            CFMCredentials.healthcare_professional_id == professional_id
        ).first()
        if credentials:
            query = query.filter(CFMPrescriptionLog.cfm_credentials_id == credentials.id)
    
    if prescription_id:
        query = query.filter(CFMPrescriptionLog.prescription_id == prescription_id)
    
    if status:
        query = query.filter(CFMPrescriptionLog.status == status)
    
    logs = query.order_by(desc(CFMPrescriptionLog.created_at)).offset(skip).limit(limit).all()
    
    return logs
