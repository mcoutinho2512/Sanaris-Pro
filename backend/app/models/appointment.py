"""
Modelos de Agendamento - COMPLETO (com UUID)
Inclui: Appointment, AppointmentWaitlist, ProfessionalSchedule
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid


# ============================================
# ENUMS (para uso no modelo)
# ============================================

class AppointmentStatus:
    """Status do agendamento"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType:
    """Tipo de consulta"""
    FIRST_TIME = "first_time"
    RETURN = "return"
    EMERGENCY = "emergency"
    TELEMEDICINE = "telemedicine"


class ConfirmationMethod:
    """Método de confirmação"""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    NONE = "none"


# ============================================
# MODEL PRINCIPAL DE AGENDAMENTO
# ============================================

class Appointment(Base):
    """Agendamento de consulta"""
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    healthcare_professional_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Agendamento
    scheduled_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30, nullable=False)
    appointment_type = Column(String(50), default=AppointmentType.FIRST_TIME)
    
    # Status
    status = Column(String(20), default=AppointmentStatus.SCHEDULED, nullable=False, index=True)
    
    # Confirmação
    confirmation_sent = Column(Boolean, default=False)
    confirmation_sent_at = Column(DateTime)
    confirmation_method = Column(String(20), default=ConfirmationMethod.NONE)
    confirmed_at = Column(DateTime)
    confirmed_by = Column(String(50))
    
    # Check-in
    checked_in_at = Column(DateTime)
    
    # Atendimento
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Lista de espera
    is_waitlist = Column(Boolean, default=False)
    waitlist_priority = Column(Integer, default=0)
    
    # Financeiro
    price = Column(Numeric(10, 2))
    paid = Column(Boolean, default=False)
    payment_method = Column(String(50))
    
    # Observações
    reason = Column(Text)
    notes = Column(Text)
    cancellation_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    patient = relationship("Patient", )
    
    def __repr__(self):
        return f"<Appointment {self.id} - {self.status}>"


# ============================================
# LISTA DE ESPERA
# ============================================

class AppointmentWaitlist(Base):
    """Lista de espera para agendamentos"""
    __tablename__ = "appointment_waitlist"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    healthcare_professional_id = Column(UUID(as_uuid=True), index=True)
    
    # Preferências
    preferred_date = Column(DateTime)
    preferred_period = Column(String(20))  # morning, afternoon, evening
    appointment_type = Column(String(50), default=AppointmentType.FIRST_TIME)
    
    # Prioridade
    priority = Column(Integer, default=0)
    urgency_level = Column(String(20))  # low, medium, high, urgent
    
    # Status
    is_active = Column(Boolean, default=True)
    notified = Column(Boolean, default=False)
    notified_at = Column(DateTime)
    
    # Observações
    reason = Column(Text)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AppointmentWaitlist {self.id} - Priority {self.priority}>"


# ============================================
# ESCALA DE PROFISSIONAIS
# ============================================

class ProfessionalSchedule(Base):
    """Escala/Horários de trabalho dos profissionais"""
    __tablename__ = "professional_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    healthcare_professional_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Dia da semana (0 = Segunda, 6 = Domingo)
    day_of_week = Column(Integer, nullable=False)
    
    # Horários
    start_time = Column(String(5), nullable=False)  # HH:MM
    end_time = Column(String(5), nullable=False)  # HH:MM
    
    # Intervalo para almoço/descanso
    break_start_time = Column(String(5))  # HH:MM
    break_end_time = Column(String(5))  # HH:MM
    
    # Duração padrão das consultas em minutos
    default_appointment_duration = Column(Integer, default=30)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalSchedule {self.day_of_week} {self.start_time}-{self.end_time}>"
