"""
Scheduler de Lembretes Automáticos
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging
import asyncio

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.services.notification_service import NotificationService, NotificationTemplates

logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.notification_service = NotificationService()
        logger.info("📅 ReminderScheduler inicializado")
    
    def start(self):
        if not self.scheduler.running:
            self.scheduler.add_job(
                func=self.check_and_send_reminders,
                trigger=IntervalTrigger(minutes=30),
                id='reminder_checker',
                name='Verificar lembretes',
                replace_existing=True
            )
            self.scheduler.start()
            logger.info("✅ Scheduler iniciado - verificando a cada 30 minutos")
        else:
            logger.info("ℹ️ Scheduler já está rodando")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("⏹️ Scheduler parado")
    
    def check_and_send_reminders(self):
        logger.info("🔍 Verificando consultas...")
        db = next(get_db())
        try:
            self.send_24h_reminders(db)
            self.send_1h_reminders(db)
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
        finally:
            db.close()
    
    def send_24h_reminders(self, db: Session):
        now = datetime.utcnow()
        tomorrow_start = now + timedelta(hours=23, minutes=30)
        tomorrow_end = now + timedelta(hours=24, minutes=30)
        
        appointments = db.query(Appointment).filter(
            and_(
                Appointment.scheduled_date >= tomorrow_start,
                Appointment.scheduled_date <= tomorrow_end,
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        ).all()
        
        logger.info(f"📋 {len(appointments)} consultas para lembrete 24h")
        
        for apt in appointments:
            existing = db.query(Notification).filter(
                and_(
                    Notification.appointment_id == str(apt.id),
                    Notification.template_used == 'lembrete_24h',
                    Notification.status == NotificationStatus.SENT
                )
            ).first()
            
            if existing:
                continue
            
            patient = db.query(Patient).filter(Patient.id == apt.patient_id).first()
            professional = db.query(User).filter(User.id == apt.healthcare_professional_id).first()
            
            if not patient or not patient.phone:
                continue
            
            date_str = apt.scheduled_date.strftime('%d/%m/%Y às %H:%M')
            message = NotificationTemplates.lembrete_24h(
                patient_name=patient.full_name.split()[0],
                professional_name=professional.full_name if professional else 'Profissional',
                date_time=date_str
            )
            
            result = asyncio.run(self.notification_service.send_whatsapp(
                recipient_phone=patient.phone,
                recipient_name=patient.full_name,
                message=message
            ))
            
            notification = Notification(
                notification_type=NotificationType.WHATSAPP,
                status=NotificationStatus.SENT if result['success'] else NotificationStatus.FAILED,
                recipient_name=patient.full_name,
                recipient_phone=patient.phone,
                message=message,
                template_used='lembrete_24h',
                appointment_id=str(apt.id),
                patient_id=patient.id,
                sent_at=result.get('sent_at'),
                provider_response=str(result)
            )
            
            db.add(notification)
            db.commit()
            logger.info(f"✅ Lembrete 24h enviado")
    
    def send_1h_reminders(self, db: Session):
        now = datetime.utcnow()
        one_hour_start = now + timedelta(minutes=45)
        one_hour_end = now + timedelta(minutes=75)
        
        appointments = db.query(Appointment).filter(
            and_(
                Appointment.scheduled_date >= one_hour_start,
                Appointment.scheduled_date <= one_hour_end,
                Appointment.status.in_(['scheduled', 'confirmed'])
            )
        ).all()
        
        logger.info(f"📋 {len(appointments)} consultas para lembrete 1h")
        
        for apt in appointments:
            existing = db.query(Notification).filter(
                and_(
                    Notification.appointment_id == str(apt.id),
                    Notification.template_used == 'lembrete_1h',
                    Notification.status == NotificationStatus.SENT
                )
            ).first()
            
            if existing:
                continue
            
            patient = db.query(Patient).filter(Patient.id == apt.patient_id).first()
            professional = db.query(User).filter(User.id == apt.healthcare_professional_id).first()
            
            if not patient or not patient.phone:
                continue
            
            date_str = apt.scheduled_date.strftime('%d/%m/%Y às %H:%M')
            message = NotificationTemplates.lembrete_1h(
                patient_name=patient.full_name.split()[0],
                professional_name=professional.full_name if professional else 'Profissional',
                date_time=date_str
            )
            
            result = asyncio.run(self.notification_service.send_whatsapp(
                recipient_phone=patient.phone,
                recipient_name=patient.full_name,
                message=message
            ))
            
            notification = Notification(
                notification_type=NotificationType.WHATSAPP,
                status=NotificationStatus.SENT if result['success'] else NotificationStatus.FAILED,
                recipient_name=patient.full_name,
                recipient_phone=patient.phone,
                message=message,
                template_used='lembrete_1h',
                appointment_id=str(apt.id),
                patient_id=patient.id,
                sent_at=result.get('sent_at'),
                provider_response=str(result)
            )
            
            db.add(notification)
            db.commit()
            logger.info(f"✅ Lembrete 1h enviado")

reminder_scheduler = ReminderScheduler()
