from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class NotificationSend(BaseModel):
    notification_type: NotificationType
    recipient_name: str
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    subject: Optional[str] = None
    message: str
    template_used: Optional[str] = None
    appointment_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None


class NotificationResponse(BaseModel):
    id: UUID
    notification_type: NotificationType
    status: NotificationStatus
    recipient_name: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: Optional[str] = None
    message: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentNotification(BaseModel):
    appointment_id: UUID
    notification_types: list[NotificationType] = [NotificationType.EMAIL]
