"""
Serviço de Notificações
Gerencia envio de Email, SMS e WhatsApp com integração Twilio
"""
from typing import Optional
from datetime import datetime, timedelta
import logging
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)

class NotificationTemplates:
    """Templates de mensagens"""
    
    @staticmethod
    def lembrete_24h(patient_name: str, professional_name: str, date_time: str) -> str:
        return f"""🏥 *Lembrete de Consulta*

Olá {patient_name}!

Você tem uma consulta marcada para *amanhã*:

📅 Data/Hora: {date_time}
👨‍⚕️ Profissional: {professional_name}

Para confirmar, responda *SIM*
Para cancelar, responda *NÃO*

Obrigado! 😊"""

    @staticmethod
    def lembrete_1h(patient_name: str, professional_name: str, date_time: str) -> str:
        return f"""⏰ *Lembrete Urgente*

Olá {patient_name}!

Sua consulta é em *1 hora*:

📅 {date_time}
👨‍⚕️ {professional_name}

Nos vemos em breve! 🏥"""

    @staticmethod
    def confirmacao_recebida(patient_name: str) -> str:
        return f"""✅ *Confirmação Recebida*

Obrigado {patient_name}!

Sua consulta foi *confirmada* com sucesso.

Te esperamos! 😊"""

    @staticmethod
    def cancelamento_recebido(patient_name: str) -> str:
        return f"""❌ *Cancelamento Registrado*

{patient_name}, sua consulta foi *cancelada*.

Para reagendar, entre em contato conosco.

Obrigado! 📞"""


class NotificationService:
    """Serviço centralizado de notificações com Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.twilio_whatsapp = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        self.is_configured = bool(self.account_sid and self.auth_token)
        
        if self.is_configured and self.account_sid != 'your_twilio_account_sid_here':
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("✅ Twilio configurado!")
            except Exception as e:
                logger.error(f"❌ Erro Twilio: {e}")
                self.is_configured = False
                self.client = None
        else:
            self.client = None
            logger.warning("⚠️ Twilio em modo simulação")
    
    async def send_whatsapp(self, recipient_phone: str, recipient_name: str, message: str) -> dict:
        """Enviar WhatsApp"""
        try:
            if not recipient_phone.startswith('whatsapp:'):
                recipient_phone = f"whatsapp:{recipient_phone}"
            
            if self.is_configured and self.client:
                try:
                    twilio_message = self.client.messages.create(
                        from_=self.twilio_whatsapp,
                        to=recipient_phone,
                        body=message
                    )
                    
                    logger.info(f"📱 WhatsApp enviado - SID: {twilio_message.sid}")
                    
                    return {
                        "success": True,
                        "sent_at": datetime.utcnow(),
                        "provider": "TWILIO",
                        "message_sid": twilio_message.sid
                    }
                
                except TwilioRestException as e:
                    logger.error(f"❌ Erro Twilio: {e}")
                    return {"success": False, "error": str(e)}
            else:
                logger.info(f"📱 [SIMULAÇÃO] WhatsApp para {recipient_name}")
                logger.info(f"Mensagem:\n{message}")
                
                return {
                    "success": True,
                    "sent_at": datetime.utcnow(),
                    "provider": "SIMULATED"
                }
        
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_sms(self, recipient_phone: str, recipient_name: str, message: str) -> dict:
        """Enviar SMS"""
        try:
            if self.is_configured and self.client:
                twilio_message = self.client.messages.create(
                    from_=self.twilio_phone,
                    to=recipient_phone,
                    body=message
                )
                return {
                    "success": True,
                    "sent_at": datetime.utcnow(),
                    "provider": "TWILIO"
                }
            else:
                logger.info(f"📱 [SIMULAÇÃO] SMS para {recipient_name}")
                return {
                    "success": True,
                    "sent_at": datetime.utcnow(),
                    "provider": "SIMULATED"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
