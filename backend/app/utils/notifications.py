"""
Sistema de Notificações
WhatsApp, Email e SMS
"""
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests


class NotificationService:
    """Serviço de notificações"""
    
    def __init__(self):
        # Configurações (em produção, usar variáveis de ambiente)
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = ""  # Configurar
        self.smtp_password = ""  # Configurar
        
        self.whatsapp_api_url = ""  # Configurar API WhatsApp
        self.whatsapp_token = ""  # Configurar token
        
        self.sms_api_url = ""  # Configurar API SMS
        self.sms_token = ""  # Configurar token
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = True,
        attachment_path: Optional[str] = None,
        attachment_name: Optional[str] = None
    ) -> bool:
        """
        Envia email
        
        Args:
            to_email: Email destinatário
            subject: Assunto
            body: Corpo da mensagem
            html: Se é HTML ou texto simples
            attachment_path: Caminho do arquivo anexo
            attachment_name: Nome do arquivo anexo
        
        Returns:
            True se enviado com sucesso
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Corpo da mensagem
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Anexo
            if attachment_path and attachment_name:
                with open(attachment_path, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                    msg.attach(attach)
            
            # Enviar
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    def send_whatsapp(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None
    ) -> bool:
        """
        Envia mensagem WhatsApp
        
        Args:
            phone: Telefone com DDD (sem +55)
            message: Mensagem de texto
            media_url: URL de mídia (imagem, PDF, etc)
        
        Returns:
            True se enviado com sucesso
        """
        try:
            # Formatar telefone
            phone_formatted = f"55{phone}"
            
            payload = {
                "phone": phone_formatted,
                "message": message
            }
            
            if media_url:
                payload["media_url"] = media_url
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.whatsapp_api_url,
                json=payload,
                headers=headers
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar WhatsApp: {e}")
            return False
    
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Envia SMS
        
        Args:
            phone: Telefone com DDD
            message: Mensagem (máx 160 caracteres)
        
        Returns:
            True se enviado com sucesso
        """
        try:
            payload = {
                "phone": phone,
                "message": message[:160]  # Limita a 160 caracteres
            }
            
            headers = {
                "Authorization": f"Bearer {self.sms_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.sms_api_url,
                json=payload,
                headers=headers
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar SMS: {e}")
            return False


# Singleton
notification_service = NotificationService()
