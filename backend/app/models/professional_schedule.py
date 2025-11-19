from sqlalchemy import Column, String, Integer, Time, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class ProfessionalSchedule(Base):
    """
    Configuração de horários de trabalho de cada profissional
    Define quando o profissional está disponível para atendimento
    """
    __tablename__ = "professional_schedules"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # FK para users (profissional)
    
    # Dia da semana (0=Segunda, 6=Domingo)
    day_of_week = Column(Integer, nullable=False)
    
    # Horários
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Intervalos (ex: almoço)
    break_start = Column(Time, nullable=True)
    break_end = Column(Time, nullable=True)
    
    # Duração padrão das consultas em minutos
    default_duration_minutes = Column(Integer, default=30)
    
    # Configurações adicionais (JSON)
    settings = Column(JSON, default={})
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfessionalSchedule {self.user_id} - Day {self.day_of_week}>"


class ScheduleBlock(Base):
    """
    Bloqueios de horários específicos
    Para férias, folgas, compromissos pessoais, etc
    """
    __tablename__ = "schedule_blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # FK para users
    
    # Data e horário do bloqueio
    block_date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Motivo do bloqueio
    reason = Column(String(255))
    block_type = Column(String(50), default='custom')  # custom, vacation, sick_leave, etc
    
    # Recorrência (para bloqueios que se repetem)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)  # Ex: {"frequency": "weekly", "days": [1,3,5]}
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ScheduleBlock {self.user_id} - {self.block_date}>"
