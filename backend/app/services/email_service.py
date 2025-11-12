import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.titan.email")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "noreply@sanarispro.com.br")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@sanarispro.com.br")
        self.from_name = os.getenv("FROM_NAME", "Sanaris Pro")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Enviar email via SMTP com STARTTLS"""
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Adicionar versão texto
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Adicionar versão HTML
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # Conectar com STARTTLS (porta 587)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email enviado com sucesso para: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email para {to_email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_link: str, user_name: str) -> bool:
        """Enviar email de recuperação de senha"""
        subject = "Recuperação de Senha - Sanaris Pro"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); padding: 40px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">�� Sanaris Pro</h1>
                            <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 14px;">Sistema de Gestão de Clínicas</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 24px;">Olá, {user_name}!</h2>
                            
                            <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                Recebemos uma solicitação para redefinir a senha da sua conta no <strong>Sanaris Pro</strong>.
                            </p>
                            
                            <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                Para criar uma nova senha, clique no botão abaixo:
                            </p>
                            
                            <!-- Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 0 0 30px 0;">
                                        <a href="{reset_link}" 
                                           style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 6px; font-size: 16px; font-weight: bold; display: inline-block;">
                                            Redefinir Minha Senha
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Link alternativo -->
                            <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 0 0 20px 0;">
                                Se o botão não funcionar, copie e cole o link abaixo no seu navegador:
                            </p>
                            <p style="color: #2563eb; font-size: 13px; word-break: break-all; margin: 0 0 30px 0; padding: 15px; background-color: #f3f4f6; border-radius: 4px;">
                                {reset_link}
                            </p>
                            
                            <!-- Aviso de segurança -->
                            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 0 0 20px 0; border-radius: 4px;">
                                <p style="color: #92400e; font-size: 14px; margin: 0; line-height: 1.5;">
                                    ⚠️ <strong>Importante:</strong> Este link expira em 15 minutos por segurança.
                                </p>
                            </div>
                            
                            <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 0;">
                                Se você <strong>não solicitou</strong> esta alteração, ignore este email. Sua senha permanecerá inalterada.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                            <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                                © 2025 Sanaris Pro - Sistema de Gestão de Clínicas Médicas
                            </p>
                            <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                Este é um email automático, por favor não responda.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        text_content = f"""
Olá, {user_name}!

Recebemos uma solicitação para redefinir a senha da sua conta no Sanaris Pro.

Para criar uma nova senha, acesse o link abaixo:
{reset_link}

IMPORTANTE: Este link expira em 15 minutos por segurança.

Se você não solicitou esta alteração, ignore este email. Sua senha permanecerá inalterada.

---
© 2025 Sanaris Pro - Sistema de Gestão de Clínicas Médicas
Este é um email automático, por favor não responda.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_notification(self, to_email: str, user_name: str, ip_address: str = "Desconhecido") -> bool:
        """Enviar notificação de tentativa de reset"""
        subject = "⚠️ Tentativa de Recuperação de Senha - Sanaris Pro"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0;">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); padding: 40px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">⚠️ Alerta de Segurança</h1>
                            <p style="color: #fecaca; margin: 10px 0 0 0; font-size: 14px;">Sanaris Pro</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 24px;">Olá, {user_name}!</h2>
                            
                            <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                Detectamos uma <strong>solicitação de recuperação de senha</strong> para sua conta no Sanaris Pro.
                            </p>
                            
                            <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 20px; margin: 0 0 20px 0; border-radius: 4px;">
                                <p style="color: #991b1b; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong>Detalhes da Tentativa:</strong>
                                </p>
                                <p style="color: #7f1d1d; font-size: 13px; margin: 0;">
                                    📧 Email: {to_email}<br>
                                    🌐 IP: {ip_address}<br>
                                    🕐 Data/Hora: Agora
                                </p>
                            </div>
                            
                            <p style="color: #16a34a; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0; padding: 15px; background-color: #f0fdf4; border-radius: 4px;">
                                ✅ <strong>Foi você?</strong> Ótimo! Você receberá um email com instruções para redefinir sua senha.
                            </p>
                            
                            <p style="color: #dc2626; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0; padding: 15px; background-color: #fef2f2; border-radius: 4px;">
                                ❌ <strong>Não foi você?</strong> Alguém pode estar tentando acessar sua conta. Recomendamos que você altere sua senha imediatamente.
                            </p>
                            
                            <p style="color: #6b7280; font-size: 14px; line-height: 1.6; margin: 0;">
                                Se precisar de ajuda, entre em contato com o suporte.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                            <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                                © 2025 Sanaris Pro - Sistema de Gestão de Clínicas Médicas
                            </p>
                            <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                Este é um email automático, por favor não responda.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        text_content = f"""
⚠️ ALERTA DE SEGURANÇA - Sanaris Pro

Olá, {user_name}!

Detectamos uma solicitação de recuperação de senha para sua conta.

Detalhes da Tentativa:
- Email: {to_email}
- IP: {ip_address}
- Data/Hora: Agora

✅ Foi você? Ótimo! Você receberá um email com instruções.

❌ Não foi você? Alguém pode estar tentando acessar sua conta. 
Recomendamos que você altere sua senha imediatamente.

---
© 2025 Sanaris Pro
Este é um email automático, por favor não responda.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Instância global
email_service = EmailService()
