"""
Serviço de Notificações
Gerencia envio de Email, SMS e WhatsApp
"""
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço centralizado de notificações"""
    
    @staticmethod
    async def send_email(
        recipient_email: str,
        recipient_name: str,
        subject: str,
        message: str
    ) -> dict:
        """Enviar email (SendGrid/SMTP)"""
        try:
            # TODO: Integrar com SendGrid quando tiver API key
            logger.info(f"📧 EMAIL enviado para {recipient_email}")
            logger.info(f"Assunto: {subject}")
            logger.info(f"Mensagem: {message[:100]}...")
            
            return {
                "success": True,
                "sent_at": datetime.utcnow(),
                "provider": "SIMULATED",
                "message": "Email simulado com sucesso"
            }
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def send_sms(
        recipient_phone: str,
        recipient_name: str,
        message: str
    ) -> dict:
        """Enviar SMS (Twilio/Zenvia)"""
        try:
            # TODO: Integrar com Twilio/Zenvia quando tiver API key
            logger.info(f"📱 SMS enviado para {recipient_phone}")
            logger.info(f"Mensagem: {message[:100]}...")
            
            return {
                "success": True,
                "sent_at": datetime.utcnow(),
                "provider": "SIMULATED",
                "message": "SMS simulado com sucesso"
            }
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def send_whatsapp(
        recipient_phone: str,
        recipient_name: str,
        message: str
    ) -> dict:
        """Enviar WhatsApp (Z-API/Evolution API)"""
        try:
            # TODO: Integrar com Z-API/Evolution API quando tiver
            logger.info(f"💬 WhatsApp enviado para {recipient_phone}")
            logger.info(f"Mensagem: {message[:100]}...")
            
            return {
                "success": True,
                "sent_at": datetime.utcnow(),
                "provider": "SIMULATED",
                "message": "WhatsApp simulado com sucesso"
            }
        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class MessageTemplates:
    """Templates de mensagens"""
    
    @staticmethod
    def appointment_confirmation(
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        professional_name: str,
        clinic_name: str = "Clínica"
    ) -> dict:
        """Template de confirmação de agendamento"""
        return {
            "subject": f"Consulta Agendada - {clinic_name}",
            "message": f"""Olá {patient_name}!

Sua consulta foi agendada com sucesso! ✅

📅 Data: {appointment_date}
🕐 Horário: {appointment_time}
👨‍⚕️ Profissional: {professional_name}
🏥 Local: {clinic_name}

Por favor, chegue com 15 minutos de antecedência.

Em caso de imprevistos, entre em contato conosco.

Atenciosamente,
Equipe {clinic_name}"""
        }
    
    @staticmethod
    def appointment_reminder(
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        professional_name: str,
        clinic_name: str = "Clínica"
    ) -> dict:
        """Template de lembrete de consulta"""
        return {
            "subject": f"Lembrete: Consulta Amanhã - {clinic_name}",
            "message": f"""Olá {patient_name}!

Este é um lembrete da sua consulta marcada para amanhã! ⏰

📅 Data: {appointment_date}
🕐 Horário: {appointment_time}
👨‍⚕️ Profissional: {professional_name}
🏥 Local: {clinic_name}

Lembre-se de chegar com 15 minutos de antecedência.

Nos vemos em breve!

Atenciosamente,
Equipe {clinic_name}"""
        }
    
    @staticmethod
    def appointment_cancellation(
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        clinic_name: str = "Clínica"
    ) -> dict:
        """Template de cancelamento"""
        return {
            "subject": f"Consulta Cancelada - {clinic_name}",
            "message": f"""Olá {patient_name}!

Informamos que sua consulta foi cancelada.

📅 Data: {appointment_date}
🕐 Horário: {appointment_time}

Para reagendar, entre em contato conosco.

Atenciosamente,
Equipe {clinic_name}"""
        }
