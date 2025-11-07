from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.notification import (
    NotificationSend,
    NotificationResponse,
    AppointmentNotification
)
from app.services.notification_service import NotificationService, MessageTemplates

router = APIRouter()


@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    notification_data: NotificationSend,
    db: Session = Depends(get_db)
):
    """Enviar notificação manual"""
    
    # Criar registro no banco
    notification = Notification(
        notification_type=notification_data.notification_type,
        recipient_name=notification_data.recipient_name,
        recipient_email=notification_data.recipient_email,
        recipient_phone=notification_data.recipient_phone,
        subject=notification_data.subject,
        message=notification_data.message,
        template_used=notification_data.template_used,
        appointment_id=notification_data.appointment_id,
        patient_id=notification_data.patient_id
    )
    
    # Enviar de acordo com o tipo
    result = None
    
    if notification_data.notification_type == NotificationType.EMAIL:
        if not notification_data.recipient_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email do destinatário é obrigatório"
            )
        result = await NotificationService.send_email(
            recipient_email=notification_data.recipient_email,
            recipient_name=notification_data.recipient_name,
            subject=notification_data.subject or "Notificação",
            message=notification_data.message
        )
    
    elif notification_data.notification_type == NotificationType.SMS:
        if not notification_data.recipient_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefone do destinatário é obrigatório"
            )
        result = await NotificationService.send_sms(
            recipient_phone=notification_data.recipient_phone,
            recipient_name=notification_data.recipient_name,
            message=notification_data.message
        )
    
    elif notification_data.notification_type == NotificationType.WHATSAPP:
        if not notification_data.recipient_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefone do destinatário é obrigatório"
            )
        result = await NotificationService.send_whatsapp(
            recipient_phone=notification_data.recipient_phone,
            recipient_name=notification_data.recipient_name,
            message=notification_data.message
        )
    
    # Atualizar status
    if result and result.get("success"):
        notification.status = NotificationStatus.SENT
        notification.sent_at = result.get("sent_at")
        notification.provider_response = result.get("message")
    else:
        notification.status = NotificationStatus.FAILED
        notification.error_message = result.get("error") if result else "Erro desconhecido"
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.post("/appointment/{appointment_id}/notify")
async def notify_appointment(
    appointment_id: str,
    notification_data: AppointmentNotification,
    db: Session = Depends(get_db)
):
    """Enviar notificação de agendamento"""
    
    # Buscar agendamento
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Buscar paciente
    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Gerar template
    template = MessageTemplates.appointment_confirmation(
        patient_name=patient.full_name,
        appointment_date=appointment.scheduled_date.strftime("%d/%m/%Y"),
        appointment_time=appointment.scheduled_date.strftime("%H:%M"),
        professional_name=appointment.healthcare_professional_id or "Profissional",
        clinic_name="Sanaris Pro"
    )
    
    results = []
    
    # Enviar para cada tipo solicitado
    for notification_type in notification_data.notification_types:
        notification = Notification(
            notification_type=notification_type,
            recipient_name=patient.full_name,
            recipient_email=patient.email,
            recipient_phone=patient.mobile_phone or patient.phone,
            subject=template["subject"],
            message=template["message"],
            template_used="appointment_confirmation",
            appointment_id=appointment.id,
            patient_id=patient.id
        )
        
        result = None
        
        if notification_type == NotificationType.EMAIL and patient.email:
            result = await NotificationService.send_email(
                recipient_email=patient.email,
                recipient_name=patient.full_name,
                subject=template["subject"],
                message=template["message"]
            )
        
        elif notification_type == NotificationType.SMS and (patient.mobile_phone or patient.phone):
            result = await NotificationService.send_sms(
                recipient_phone=patient.mobile_phone or patient.phone,
                recipient_name=patient.full_name,
                message=template["message"]
            )
        
        elif notification_type == NotificationType.WHATSAPP and (patient.mobile_phone or patient.phone):
            result = await NotificationService.send_whatsapp(
                recipient_phone=patient.mobile_phone or patient.phone,
                recipient_name=patient.full_name,
                message=template["message"]
            )
        
        if result and result.get("success"):
            notification.status = NotificationStatus.SENT
            notification.sent_at = result.get("sent_at")
            notification.provider_response = result.get("message")
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = result.get("error") if result else "Dados de contato ausentes"
        
        db.add(notification)
        results.append({
            "type": notification_type,
            "status": notification.status,
            "sent_at": notification.sent_at
        })
    
    db.commit()
    
    return {
        "message": "Notificações processadas",
        "appointment_id": appointment_id,
        "patient_name": patient.full_name,
        "results": results
    }


@router.get("/history", response_model=List[NotificationResponse])
async def get_notifications_history(
    skip: int = 0,
    limit: int = 100,
    notification_type: str = None,
    db: Session = Depends(get_db)
):
    """Listar histórico de notificações"""
    
    query = db.query(Notification)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications


@router.get("/patient/{patient_id}", response_model=List[NotificationResponse])
async def get_patient_notifications(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Listar notificações de um paciente"""
    
    notifications = db.query(Notification).filter(
        Notification.patient_id == patient_id
    ).order_by(Notification.created_at.desc()).all()
    
    return notifications
