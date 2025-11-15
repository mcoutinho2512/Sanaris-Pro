"""
Rotas de Prescrição Digital - COMPLETO
CRUD completo + Templates + Assinatura + Histórico
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionTemplate
from app.models.patient import Patient
from app.schemas.prescription import (
    PrescriptionSendEmail, PrescriptionSendWhatsApp, PrescriptionSendSMS,
    PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse,
    PrescriptionListResponse, PrescriptionSign, PrescriptionDispense,
    PrescriptionItemCreate, PrescriptionItemUpdate, PrescriptionItemResponse,
    PrescriptionTemplateCreate, PrescriptionTemplateUpdate, PrescriptionTemplateResponse,
    PrescriptionType
)

router = APIRouter(tags=["Prescrições"])


# ============================================
# CRUD DE PRESCRIÇÕES
# ============================================

@router.post("/", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova prescrição com medicamentos"""
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == prescription_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Define data da prescrição se não informada
    
    # Define validade padrão (30 dias) se não informada
    
    # Cria prescrição (sem os items)
    prescription_dict = prescription_data.dict(exclude={'items'})
    prescription = Prescription(**prescription_dict)
    db.add(prescription)
    db.flush()  # Garante que o ID seja gerado
    
    # Adiciona os items
    for idx, item_data in enumerate(prescription_data.items):
        item_dict = item_data.dict()
        item = PrescriptionItem(
            prescription_id=prescription.id,
            **item_dict
        )
        db.add(item)
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


@router.get("/", response_model=List[PrescriptionListResponse])
def list_prescriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    patient_id: Optional[str] = None,
    professional_id: Optional[str] = None,
    prescription_type: Optional[PrescriptionType] = None,
    is_signed: Optional[bool] = None,
    is_dispensed: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Lista prescrições com filtros avançados
    
    Filtros disponíveis:
    - patient_id: filtra por paciente
    - professional_id: filtra por profissional
    - prescription_type: filtra por tipo
    - is_signed: filtra por assinadas/não assinadas
    - is_dispensed: filtra por dispensadas/não dispensadas
    - date_from/date_to: filtra por período
    """
    
    query = db.query(Prescription)
    
    # Aplicar filtros
    if patient_id:
        query = query.filter(Prescription.patient_id == patient_id)
    
    if professional_id:
        query = query.filter(Prescription.healthcare_professional_id == professional_id)
    
    if prescription_type:
        query = query.filter(Prescription.prescription_type == prescription_type)
    
    if is_signed is not None:
        query = query.filter(Prescription.is_signed == is_signed)
    
    if is_dispensed is not None:
        query = query.filter(Prescription.is_dispensed == is_dispensed)
    
    if date_from:
        query = query.filter(Prescription.prescription_date >= date_from)
    
    if date_to:
        query = query.filter(Prescription.prescription_date <= date_to)
    
    # Ordenar por data (mais recente primeiro)
    query = query.order_by(desc(Prescription.prescription_date))
    
    prescriptions = query.offset(skip).limit(limit).all()
    
    # Adicionar contagem de items
    result = []
    for prescription in prescriptions:
        prescription_dict = {
            "id": prescription.id,
            "patient_id": prescription.patient_id,
            "healthcare_professional_id": prescription.healthcare_professional_id,
            "prescription_date": prescription.prescription_date,
            "prescription_type": prescription.prescription_type,
            "is_signed": prescription.is_signed,
            "is_dispensed": prescription.is_dispensed,
            "items_count": len(prescription.items)
        }
        result.append(PrescriptionListResponse(**prescription_dict))
    
    return result


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(prescription_id: str, db: Session = Depends(get_db)):
    """Busca uma prescrição completa por ID"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    return prescription


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
def update_prescription(
    prescription_id: str,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma prescrição"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    # Não permite atualizar se já foi assinada
    if prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescrição assinada não pode ser alterada"
        )
    
    # Atualiza campos
    update_data = prescription_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


@router.delete("/{prescription_id}")
def delete_prescription(prescription_id: str, db: Session = Depends(get_db)):
    """Deleta uma prescrição"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    # Não permite deletar se já foi assinada
    if prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescrição assinada não pode ser deletada"
        )
    
    db.delete(prescription)
    db.commit()
    
    return {"message": "Prescrição deletada com sucesso", "success": True}



# ============================================
# AÇÕES ESPECIAIS DA PRESCRIÇÃO
# ============================================

@router.post("/{prescription_id}/sign", response_model=PrescriptionResponse)
def sign_prescription(
    prescription_id: str,
    sign_data: PrescriptionSign,
    db: Session = Depends(get_db)
):
    """Assina digitalmente a prescrição"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescrição já está assinada"
        )
    
    # Registra assinatura
    prescription.is_signed = True
    prescription.signed_at = datetime.utcnow()
    prescription.crm_number = sign_data.crm_number
    prescription.crm_state = sign_data.crm_state
    prescription.professional_signature = sign_data.signature
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


@router.post("/{prescription_id}/print", response_model=PrescriptionResponse)
def print_prescription(prescription_id: str, db: Session = Depends(get_db)):
    """Marca prescrição como impressa"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser impressas"
        )
    
    prescription.is_printed = True
    prescription.printed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


@router.post("/{prescription_id}/dispense", response_model=PrescriptionResponse)
def dispense_prescription(
    prescription_id: str,
    dispense_data: PrescriptionDispense,
    db: Session = Depends(get_db)
):
    """Registra dispensação da prescrição (uso farmácia)"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser dispensadas"
        )
    
    if prescription.is_dispensed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prescrição já foi dispensada"
        )
    
    prescription.is_dispensed = True
    prescription.dispensed_at = datetime.utcnow()
    prescription.pharmacy_name = dispense_data.pharmacy_name
    prescription.pharmacist_name = dispense_data.pharmacist_name
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


# ============================================
# GERENCIAMENTO DE ITEMS
# ============================================

@router.post("/{prescription_id}/items", response_model=PrescriptionItemResponse, status_code=status.HTTP_201_CREATED)
def add_item(
    prescription_id: str,
    item_data: PrescriptionItemCreate,
    db: Session = Depends(get_db)
):
    """Adiciona medicamento à prescrição"""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível adicionar items a prescrição assinada"
        )
    
    item = PrescriptionItem(
        prescription_id=prescription_id,
        **item_data.dict()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@router.get("/{prescription_id}/items", response_model=List[PrescriptionItemResponse])
def get_items(prescription_id: str, db: Session = Depends(get_db)):
    """Lista todos os medicamentos de uma prescrição"""
    
    items = db.query(PrescriptionItem).filter(
        PrescriptionItem.prescription_id == prescription_id
    ).order_by(PrescriptionItem.display_order).all()
    
    return items


@router.put("/items/{item_id}", response_model=PrescriptionItemResponse)
def update_item(
    item_id: str,
    item_data: PrescriptionItemUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza medicamento"""
    
    item = db.query(PrescriptionItem).filter(PrescriptionItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    
    # Verifica se a prescrição foi assinada
    prescription = db.query(Prescription).filter(Prescription.id == item.prescription_id).first()
    if prescription and prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar items de prescrição assinada"
        )
    
    # Atualiza campos
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """Remove medicamento da prescrição"""
    
    item = db.query(PrescriptionItem).filter(PrescriptionItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    
    # Verifica se a prescrição foi assinada
    prescription = db.query(Prescription).filter(Prescription.id == item.prescription_id).first()
    if prescription and prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível remover items de prescrição assinada"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deletado com sucesso", "success": True}



# ============================================
# TEMPLATES DE PRESCRIÇÃO
# ============================================

@router.post("/templates", response_model=PrescriptionTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: PrescriptionTemplateCreate,
    db: Session = Depends(get_db)
):
    """Cria um modelo de prescrição"""
    
    template = PrescriptionTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


@router.get("/templates", response_model=List[PrescriptionTemplateResponse])
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    professional_id: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista templates de prescrição"""
    
    query = db.query(PrescriptionTemplate)
    
    if professional_id:
        query = query.filter(PrescriptionTemplate.healthcare_professional_id == professional_id)
    
    if category:
        query = query.filter(PrescriptionTemplate.category == category)
    
    if is_active is not None:
        query = query.filter(PrescriptionTemplate.is_active == is_active)
    
    if is_public is not None:
        query = query.filter(PrescriptionTemplate.is_public == is_public)
    
    templates = query.order_by(desc(PrescriptionTemplate.usage_count)).offset(skip).limit(limit).all()
    
    return templates


@router.get("/templates/{template_id}", response_model=PrescriptionTemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    """Busca um template por ID"""
    
    template = db.query(PrescriptionTemplate).filter(PrescriptionTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    return template


@router.put("/templates/{template_id}", response_model=PrescriptionTemplateResponse)
def update_template(
    template_id: str,
    template_data: PrescriptionTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um template"""
    
    template = db.query(PrescriptionTemplate).filter(PrescriptionTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    # Atualiza campos
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/templates/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Deleta um template"""
    
    template = db.query(PrescriptionTemplate).filter(PrescriptionTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deletado com sucesso", "success": True}


@router.post("/templates/{template_id}/use", response_model=PrescriptionResponse)
def use_template(
    template_id: str,
    patient_id: str,
    medical_record_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Cria uma prescrição a partir de um template"""
    
    template = db.query(PrescriptionTemplate).filter(PrescriptionTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template está inativo"
        )
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Cria prescrição usando o template
    import json
    template_items = json.loads(template.template_data)
    
    prescription = Prescription(
        patient_id=patient_id,
        medical_record_id=medical_record_id,
        healthcare_professional_id=template.healthcare_professional_id,
        prescription_date=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(days=30),
        prescription_type="regular"
    )
    db.add(prescription)
    db.flush()
    
    # Adiciona items do template
    for idx, item_data in enumerate(template_items):
        item = PrescriptionItem(
            prescription_id=prescription.id,
            display_order=idx,
            **item_data
        )
        db.add(item)
    
    # Atualiza contador de uso do template
    template.usage_count += 1
    template.last_used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prescription)
    
    return prescription


# ============================================
# HISTÓRICO E RELATÓRIOS
# ============================================

@router.get("/patient/{patient_id}/history", response_model=List[PrescriptionListResponse])
def get_patient_history(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retorna histórico de prescrições do paciente
    Ordenado por data (mais recente primeiro)
    """
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).order_by(desc(Prescription.prescription_date)).offset(skip).limit(limit).all()
    
    # Adicionar contagem de items
    result = []
    for prescription in prescriptions:
        prescription_dict = {
            "id": prescription.id,
            "patient_id": prescription.patient_id,
            "healthcare_professional_id": prescription.healthcare_professional_id,
            "prescription_date": prescription.prescription_date,
            "prescription_type": prescription.prescription_type,
            "is_signed": prescription.is_signed,
            "is_dispensed": prescription.is_dispensed,
            "items_count": len(prescription.items)
        }
        result.append(PrescriptionListResponse(**prescription_dict))
    
    return result


@router.get("/statistics")
def get_statistics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    professional_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retorna estatísticas de prescrições"""
    
    query = db.query(Prescription)
    
    if date_from:
        query = query.filter(Prescription.prescription_date >= date_from)
    if date_to:
        query = query.filter(Prescription.prescription_date <= date_to)
    if professional_id:
        query = query.filter(Prescription.healthcare_professional_id == professional_id)
    
    total = query.count()
    signed = query.filter(Prescription.is_signed == True).count()
    dispensed = query.filter(Prescription.is_dispensed == True).count()
    
    by_type = db.query(
        Prescription.prescription_type,
        func.count(Prescription.id)
    ).filter(
        Prescription.id.in_(query.with_entities(Prescription.id))
    ).group_by(Prescription.prescription_type).all()
    
    return {
        "total_prescriptions": total,
        "signed_prescriptions": signed,
        "dispensed_prescriptions": dispensed,
        "pending_signature": total - signed,
        "signature_rate": round((signed / total * 100), 2) if total > 0 else 0,
        "prescriptions_by_type": {pt: count for pt, count in by_type}
    }



# ============================================
# ENVIO DE PRESCRIÇÕES
# ============================================

@router.post("/{prescription_id}/send-email", response_model=dict)
def send_prescription_by_email(
    prescription_id: str,
    send_data: PrescriptionSendEmail,
    db: Session = Depends(get_db)
):
    """Envia prescrição por email"""
    from app.utils.notifications import notification_service
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser enviadas"
        )
    
    # Buscar paciente
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    
    # Montar mensagem
    subject = f"Prescrição Médica - {patient.full_name}"
    
    if send_data.message:
        body = send_data.message
    else:
        body = f"""
        <html>
        <body>
            <h2>Prescrição Médica</h2>
            <p>Prezado(a) {patient.full_name},</p>
            <p>Segue em anexo sua prescrição médica.</p>
            <p><strong>Data:</strong> {prescription.prescription_date.strftime('%d/%m/%Y')}</p>
            <p><strong>Validade:</strong> {prescription.valid_until.strftime('%d/%m/%Y') if prescription.valid_until else 'N/A'}</p>
            <br>
            <p><strong>Medicamentos prescritos:</strong></p>
            <ul>
            {''.join([f'<li>{item.medication_name} - {item.dosage}</li>' for item in prescription.items])}
            </ul>
            <br>
            <p>Atenciosamente,</p>
            <p>Equipe Médica</p>
        </body>
        </html>
        """
    
    # Enviar (em produção, gerar PDF da prescrição)
    success = notification_service.send_email(
        to_email=send_data.email,
        subject=subject,
        body=body,
        html=True
    )
    
    if success:
        prescription.is_sent = True
        prescription.sent_at = datetime.utcnow()
        db.commit()
    
    return {
        "success": success,
        "method": "email",
        "sent_to": send_data.email,
        "sent_at": datetime.utcnow() if success else None,
        "message": "Prescrição enviada com sucesso" if success else "Falha ao enviar prescrição"
    }


@router.post("/{prescription_id}/send-whatsapp", response_model=dict)
def send_prescription_by_whatsapp(
    prescription_id: str,
    send_data: PrescriptionSendWhatsApp,
    db: Session = Depends(get_db)
):
    """Envia prescrição por WhatsApp"""
    from app.utils.notifications import notification_service
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser enviadas"
        )
    
    # Buscar paciente
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    
    # Montar mensagem
    if send_data.message:
        message = send_data.message
    else:
        medications = "\n".join([f"• {item.medication_name} - {item.dosage}" for item in prescription.items])
        message = f"""
🏥 *Prescrição Médica*

Olá {patient.full_name}!

Sua prescrição médica está pronta.

*Data:* {prescription.prescription_date.strftime('%d/%m/%Y')}
*Validade:* {prescription.valid_until.strftime('%d/%m/%Y') if prescription.valid_until else 'N/A'}

*Medicamentos:*
{medications}

Qualquer dúvida, entre em contato.
        """
    
    # Enviar
    success = notification_service.send_whatsapp(
        phone=send_data.phone,
        message=message
    )
    
    if success:
        prescription.is_sent = True
        prescription.sent_at = datetime.utcnow()
        db.commit()
    
    return {
        "success": success,
        "method": "whatsapp",
        "sent_to": send_data.phone,
        "sent_at": datetime.utcnow() if success else None,
        "message": "Prescrição enviada com sucesso" if success else "Falha ao enviar prescrição"
    }


@router.post("/{prescription_id}/send-sms", response_model=dict)
def send_prescription_by_sms(
    prescription_id: str,
    send_data: PrescriptionSendSMS,
    db: Session = Depends(get_db)
):
    """Envia notificação de prescrição por SMS"""
    from app.utils.notifications import notification_service
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescrição não encontrada"
        )
    
    if not prescription.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas prescrições assinadas podem ser enviadas"
        )
    
    # Buscar paciente
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    
    # Montar mensagem (SMS tem limite de 160 caracteres)
    if send_data.message:
        message = send_data.message[:160]
    else:
        message = f"Sua prescrição médica está pronta. {len(prescription.items)} medicamento(s) prescrito(s). Retire na recepção ou acesse o portal."
    
    # Enviar
    success = notification_service.send_sms(
        phone=send_data.phone,
        message=message
    )
    
    if success:
        prescription.is_sent = True
        prescription.sent_at = datetime.utcnow()
        db.commit()
    
    return {
        "success": success,
        "method": "sms",
        "sent_to": send_data.phone,
        "sent_at": datetime.utcnow() if success else None,
        "message": "Notificação enviada com sucesso" if success else "Falha ao enviar notificação"
    }

