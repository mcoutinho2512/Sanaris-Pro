"""
Endpoints de Notificações
Webhook para confirmação de consultas via WhatsApp
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.services.notification_service import NotificationService, NotificationTemplates

router = APIRouter()
logger = logging.getLogger(__name__)
notification_service = NotificationService()

@router.post("/webhook/twilio")
async def twilio_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook para receber respostas do Twilio (WhatsApp/SMS)
    Quando paciente responde SIM ou NÃO, este endpoint processa
    """
    try:
        # Pegar dados do formulário (Twilio envia form-data)
        form_data = await request.form()
        
        from_number = form_data.get('From', '')
        body = form_data.get('Body', '').strip().upper()
        message_sid = form_data.get('MessageSid', '')
        
        logger.info(f"📱 Webhook recebido de {from_number}: {body}")
        
        # Limpar número de WhatsApp
        phone = from_number.replace('whatsapp:', '').strip()
        
        # Buscar paciente pelo telefone
        patient = db.query(Patient).filter(Patient.phone == phone).first()
        
        if not patient:
            logger.warning(f"⚠️ Paciente não encontrado para telefone {phone}")
            return {"status": "ok", "message": "Paciente não encontrado"}
        
        # Buscar última notificação pendente de confirmação
        notification = db.query(Notification).filter(
            Notification.recipient_phone == phone,
            Notification.template_used.in_(['lembrete_24h', 'lembrete_1h']),
            Notification.status == NotificationStatus.SENT
        ).order_by(Notification.sent_at.desc()).first()
        
        if not notification or not notification.appointment_id:
            logger.warning(f"⚠️ Nenhuma notificação pendente para {patient.full_name}")
            return {"status": "ok", "message": "Sem notificação pendente"}
        
        # Buscar consulta
        appointment = db.query(Appointment).filter(
            Appointment.id == notification.appointment_id
        ).first()
        
        if not appointment:
            logger.warning(f"⚠️ Consulta não encontrada")
            return {"status": "ok"}
        
        # Processar resposta
        if 'SIM' in body or 'YES' in body or 'OK' in body or 'CONFIRMAR' in body:
            # CONFIRMAR consulta
            appointment.status = 'confirmed'
            db.commit()
            
            # Enviar mensagem de confirmação
            confirmation_msg = NotificationTemplates.confirmacao_recebida(
                patient_name=patient.full_name.split()[0]
            )
            
            result = await notification_service.send_whatsapp(
                recipient_phone=phone,
                recipient_name=patient.full_name,
                message=confirmation_msg
            )
            
            # Salvar notificação de confirmação
            confirmation_notification = Notification(
                notification_type=NotificationType.WHATSAPP,
                status=NotificationStatus.SENT if result['success'] else NotificationStatus.FAILED,
                recipient_name=patient.full_name,
                recipient_phone=phone,
                message=confirmation_msg,
                template_used='confirmacao_recebida',
                appointment_id=str(appointment.id),
                patient_id=patient.id,
                sent_at=result.get('sent_at'),
                provider_response=str(result)
            )
            
            db.add(confirmation_notification)
            db.commit()
            
            logger.info(f"✅ Consulta confirmada por {patient.full_name}")
        
        elif 'NAO' in body or 'NÃO' in body or 'NO' in body or 'CANCELAR' in body:
            # CANCELAR consulta
            appointment.status = 'cancelled'
            db.commit()
            
            # Enviar mensagem de cancelamento
            cancellation_msg = NotificationTemplates.cancelamento_recebido(
                patient_name=patient.full_name.split()[0]
            )
            
            result = await notification_service.send_whatsapp(
                recipient_phone=phone,
                recipient_name=patient.full_name,
                message=cancellation_msg
            )
            
            # Salvar notificação de cancelamento
            cancellation_notification = Notification(
                notification_type=NotificationType.WHATSAPP,
                status=NotificationStatus.SENT if result['success'] else NotificationStatus.FAILED,
                recipient_name=patient.full_name,
                recipient_phone=phone,
                message=cancellation_msg,
                template_used='cancelamento_recebido',
                appointment_id=str(appointment.id),
                patient_id=patient.id,
                sent_at=result.get('sent_at'),
                provider_response=str(result)
            )
            
            db.add(cancellation_notification)
            db.commit()
            
            logger.info(f"❌ Consulta cancelada por {patient.full_name}")
        
        else:
            logger.info(f"ℹ️ Resposta não reconhecida: {body}")
        
        return {"status": "ok", "message": "Processado"}
    
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/history")
async def get_notifications_history(
    patient_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Listar histórico de notificações"""
    query = db.query(Notification).order_by(Notification.created_at.desc())
    
    if patient_id:
        query = query.filter(Notification.patient_id == patient_id)
    
    notifications = query.limit(limit).all()
    
    return [
        {
            "id": str(n.id),
            "type": n.notification_type,
            "status": n.status,
            "recipient_name": n.recipient_name,
            "recipient_phone": n.recipient_phone,
            "template_used": n.template_used,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notifications
    ]


@router.post("/test")
async def test_notification(
    phone: str,
    name: str,
    db: Session = Depends(get_db)
):
    """Endpoint para testar envio de notificação"""
    message = f"""🧪 *Teste de Notificação*

Olá {name}!

Este é um teste do sistema de lembretes do Sanaris Pro.

Se você recebeu esta mensagem, o sistema está funcionando! ✅"""
    
    result = await notification_service.send_whatsapp(
        recipient_phone=phone,
        recipient_name=name,
        message=message
    )
    
    # Salvar no banco
    notification = Notification(
        notification_type=NotificationType.WHATSAPP,
        status=NotificationStatus.SENT if result['success'] else NotificationStatus.FAILED,
        recipient_name=name,
        recipient_phone=phone,
        message=message,
        template_used='test',
        sent_at=result.get('sent_at'),
        provider_response=str(result)
    )
    
    db.add(notification)
    db.commit()
    
    return {
        "success": result['success'],
        "message": "Notificação de teste enviada",
        "details": result
    }
