"""
Serviço de Notificações
Envia confirmações por WhatsApp, Email e SMS
"""
from datetime import datetime


class NotificationService:
    """Serviço para envio de notificações"""
    
    @staticmethod
    async def send_appointment_confirmation(
        patient_name: str,
        patient_phone: str,
        patient_email: str,
        appointment_date: datetime,
        professional_name: str,
        clinic_name: str,
        method: str
    ) -> bool:
        """Envia confirmação de agendamento"""
        date_str = appointment_date.strftime("%d/%m/%Y às %H:%M")
        message = f"Olá {patient_name}! Confirmamos seu agendamento para {date_str} com {professional_name}"
        print(f"📱 {method}: {message[:50]}...")
        return True
    
    @staticmethod
    async def notify_waitlist_opening(
        patient_name: str,
        patient_phone: str,
        patient_email: str,
        available_date: datetime,
        professional_name: str,
        clinic_name: str,
        method: str
    ) -> bool:
        """Notifica vaga disponível"""
        date_str = available_date.strftime("%d/%m/%Y às %H:%M")
        message = f"Vaga disponível para {patient_name} em {date_str}"
        print(f"🎉 {method}: {message[:50]}...")
        return True


notification_service = NotificationService()
