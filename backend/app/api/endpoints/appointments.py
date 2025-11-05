"""
Rotas de Agendamentos - COMPLETO
CRUD completo + confirmações + lista de espera + escalas + disponibilidade
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentWaitlist, ProfessionalSchedule
from app.models.patient import Patient
from app.schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, AppointmentConfirm,
    AppointmentCancel, AppointmentResponse, AppointmentListResponse,
    WaitlistCreate, WaitlistResponse, ScheduleCreate, ScheduleResponse,
    AppointmentStatus, AppointmentType, ConfirmationMethod
)
from app.services.notifications import notification_service
from app.services.notifications import notification_service

router = APIRouter(prefix="/api/v1/appointments", tags=["Agendamentos"])


# ============================================
# CRUD DE AGENDAMENTOS
# ============================================

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo agendamento com verificação de conflitos"""
    
    # Verifica se paciente existe
    patient = db.query(Patient).filter(Patient.id == appointment_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verifica conflito de horário
    conflict = db.query(Appointment).filter(
        Appointment.healthcare_professional_id == appointment_data.healthcare_professional_id,
        Appointment.scheduled_date == appointment_data.scheduled_date,
        Appointment.status.in_([
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.IN_PROGRESS
        ])
    ).first()
    
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um agendamento neste horário"
        )
    
    # Cria agendamento
    appointment = Appointment(**appointment_data.dict())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.get("/", response_model=List[AppointmentListResponse])
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[AppointmentStatus] = None,
    professional_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lista agendamentos com filtros avançados
    
    Filtros disponíveis:
    - status_filter: filtra por status
    - professional_id: filtra por profissional
    - patient_id: filtra por paciente
    - date_from/date_to: filtra por período
    """
    
    query = db.query(Appointment)
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if professional_id:
        query = query.filter(Appointment.healthcare_professional_id == professional_id)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if date_from:
        query = query.filter(func.date(Appointment.scheduled_date) >= date_from)
    
    if date_to:
        query = query.filter(func.date(Appointment.scheduled_date) <= date_to)
    
    # Ordenar por data
    query = query.order_by(Appointment.scheduled_date)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Busca um agendamento por ID"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um agendamento"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Verifica se pode editar
    if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível editar agendamentos concluídos ou cancelados"
        )
    
    # Atualiza campos
    update_data = appointment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Deleta um agendamento"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    db.delete(appointment)
    db.commit()
    
    return {"message": "Agendamento deletado com sucesso", "success": True}


# ============================================
# CONFIRMAÇÕES E NOTIFICAÇÕES
# ============================================

@router.post("/{appointment_id}/send-confirmation")
async def send_appointment_confirmation(
    appointment_id: str,
    method: ConfirmationMethod = Query(..., description="Método de envio"),
    db: Session = Depends(get_db)
):
    """Envia confirmação de agendamento via WhatsApp, Email ou SMS"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Busca dados do paciente
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    
    # Envia notificação
    success = await notification_service.send_appointment_confirmation(
        patient_name=patient.full_name,
        patient_phone=patient.phone or "",
        patient_email=patient.email or "",
        appointment_date=appointment.scheduled_date,
        professional_name="Dr. Profissional",  # TODO: Buscar do banco
        clinic_name="Sua Clínica",
        method=method
    )
    
    if success:
        appointment.confirmation_sent = True
        appointment.confirmation_sent_at = datetime.utcnow()
        appointment.confirmation_method = method
        db.commit()
        
        return {
            "message": f"Confirmação enviada via {method.value}",
            "success": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar confirmação"
        )


@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(
    appointment_id: str,
    confirm_data: AppointmentConfirm,
    db: Session = Depends(get_db)
):
    """Confirma um agendamento (confirmação recebida do paciente)"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento não pode ser confirmado"
        )
    
    appointment.status = AppointmentStatus.CONFIRMED
    appointment.confirmed_at = datetime.utcnow()
    appointment.confirmation_method = confirm_data.confirmation_method
    appointment.confirmed_by = confirm_data.confirmed_by
    
    db.commit()
    db.refresh(appointment)
    
    return appointment



# ============================================
# FLUXO DE STATUS DO AGENDAMENTO
# ============================================

@router.post("/{appointment_id}/check-in", response_model=AppointmentResponse)
def check_in_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Faz check-in do paciente"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    appointment.checked_in_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/start", response_model=AppointmentResponse)
def start_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Inicia o atendimento"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    if appointment.status not in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento não pode ser iniciado"
        )
    
    appointment.status = AppointmentStatus.IN_PROGRESS
    appointment.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Finaliza o atendimento"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    if appointment.status != AppointmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento não pode ser finalizado"
        )
    
    appointment.status = AppointmentStatus.COMPLETED
    appointment.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: str,
    cancel_data: AppointmentCancel,
    db: Session = Depends(get_db)
):
    """Cancela um agendamento"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    if appointment.status not in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agendamento não pode ser cancelado"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = cancel_data.cancellation_reason
    
    db.commit()
    db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/no-show", response_model=AppointmentResponse)
def mark_no_show(appointment_id: str, db: Session = Depends(get_db)):
    """Marca como falta"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    appointment.status = AppointmentStatus.NO_SHOW
    
    db.commit()
    db.refresh(appointment)
    
    return appointment



# ============================================
# LISTA DE ESPERA
# ============================================

waitlist_router = APIRouter(prefix="/api/v1/waitlist", tags=["Lista de Espera"])


@waitlist_router.post("/", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_waitlist(
    waitlist_data: WaitlistCreate,
    db: Session = Depends(get_db)
):
    """Adiciona paciente à lista de espera"""
    
    waitlist_entry = AppointmentWaitlist(**waitlist_data.dict())
    db.add(waitlist_entry)
    db.commit()
    db.refresh(waitlist_entry)
    
    return waitlist_entry


@waitlist_router.get("/", response_model=List[WaitlistResponse])
def list_waitlist(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Lista todos na fila de espera"""
    
    query = db.query(AppointmentWaitlist)
    
    if active_only:
        query = query.filter(AppointmentWaitlist.is_active == True)
    
    query = query.order_by(
        AppointmentWaitlist.priority.desc(),
        AppointmentWaitlist.created_at
    )
    
    return query.all()


@waitlist_router.get("/{waitlist_id}", response_model=WaitlistResponse)
def get_waitlist_entry(
    waitlist_id: str,
    db: Session = Depends(get_db)
):
    """Busca uma entrada específica da lista de espera"""
    
    entry = db.query(AppointmentWaitlist).filter(
        AppointmentWaitlist.id == waitlist_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada da lista de espera não encontrada"
        )
    
    return entry


@waitlist_router.put("/{waitlist_id}", response_model=WaitlistResponse)
def update_waitlist_entry(
    waitlist_id: str,
    waitlist_data: WaitlistCreate,
    db: Session = Depends(get_db)
):
    """Atualiza uma entrada da lista de espera"""
    
    entry = db.query(AppointmentWaitlist).filter(
        AppointmentWaitlist.id == waitlist_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada da lista de espera não encontrada"
        )
    
    update_data = waitlist_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    db.commit()
    db.refresh(entry)
    
    return entry


@waitlist_router.delete("/{waitlist_id}")
def delete_waitlist_entry(
    waitlist_id: str,
    db: Session = Depends(get_db)
):
    """Remove uma entrada da lista de espera"""
    
    entry = db.query(AppointmentWaitlist).filter(
        AppointmentWaitlist.id == waitlist_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada da lista de espera não encontrada"
        )
    
    db.delete(entry)
    db.commit()
    
    return {
        "message": "Entrada removida da lista de espera",
        "success": True
    }


@waitlist_router.post("/{waitlist_id}/notify")
async def notify_waitlist_patient(
    waitlist_id: str,
    method: ConfirmationMethod = Query(..., description="Método de notificação"),
    available_date: datetime = Query(..., description="Data/hora disponível"),
    db: Session = Depends(get_db)
):
    """Notifica paciente sobre vaga disponível"""
    
    entry = db.query(AppointmentWaitlist).filter(
        AppointmentWaitlist.id == waitlist_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada da lista de espera não encontrada"
        )
    
    # Busca dados do paciente
    patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
    
    # Envia notificação
    success = await notification_service.notify_waitlist_opening(
        patient_name=patient.full_name,
        patient_phone=patient.phone or "",
        patient_email=patient.email or "",
        available_date=available_date,
        professional_name="Dr. Profissional",  # TODO: Buscar do banco
        clinic_name="Sua Clínica",
        method=method
    )
    
    if success:
        entry.notified = True
        entry.notified_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"Paciente notificado via {method.value}",
            "success": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar notificação"
        )



# ============================================
# ESCALAS DE PROFISSIONAIS
# ============================================

schedule_router = APIRouter(prefix="/api/v1/schedules", tags=["Escalas"])


@schedule_router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Cria horário de trabalho para profissional"""
    
    schedule = ProfessionalSchedule(**schedule_data.dict())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    return schedule


@schedule_router.get("/professional/{professional_id}", response_model=List[ScheduleResponse])
def get_professional_schedule(
    professional_id: str,
    db: Session = Depends(get_db)
):
    """Busca escala de um profissional"""
    
    schedules = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.healthcare_professional_id == professional_id,
        ProfessionalSchedule.is_active == True
    ).order_by(ProfessionalSchedule.day_of_week).all()
    
    return schedules


@schedule_router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Busca uma escala específica"""
    
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    return schedule


@schedule_router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db)
):
    """Atualiza uma escala"""
    
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    update_data = schedule_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule


@schedule_router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db)
):
    """Remove uma escala"""
    
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    db.delete(schedule)
    db.commit()
    
    return {
        "message": "Escala removida com sucesso",
        "success": True
    }



# ============================================
# DISPONIBILIDADE DE HORÁRIOS
# ============================================

availability_router = APIRouter(prefix="/api/v1/availability", tags=["Disponibilidade"])


@availability_router.get("/professional/{professional_id}")
def get_available_slots(
    professional_id: str,
    date_filter: date = Query(..., description="Data para verificar disponibilidade"),
    db: Session = Depends(get_db)
):
    """
    Retorna horários disponíveis de um profissional em uma data específica
    
    Retorna lista de horários no formato HH:MM que estão livres
    """
    
    # Busca escala do profissional para o dia da semana
    day_of_week = date_filter.weekday()  # 0 = Monday, 6 = Sunday
    
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.healthcare_professional_id == professional_id,
        ProfessionalSchedule.day_of_week == day_of_week,
        ProfessionalSchedule.is_active == True
    ).first()
    
    if not schedule:
        return {
            "date": date_filter.isoformat(),
            "professional_id": professional_id,
            "available_slots": [],
            "message": "Profissional não trabalha neste dia"
        }
    
    # Busca agendamentos existentes na data
    start_of_day = datetime.combine(date_filter, datetime.min.time())
    end_of_day = datetime.combine(date_filter, datetime.max.time())
    
    existing_appointments = db.query(Appointment).filter(
        Appointment.healthcare_professional_id == professional_id,
        Appointment.scheduled_date >= start_of_day,
        Appointment.scheduled_date <= end_of_day,
        Appointment.status.in_([
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.IN_PROGRESS
        ])
    ).all()
    
    # Gera todos os slots possíveis
    def time_to_minutes(t: str) -> int:
        h, m = map(int, t.split(':'))
        return h * 60 + m
    
    def minutes_to_time(minutes: int) -> str:
        h = minutes // 60
        m = minutes % 60
        return f"{h:02d}:{m:02d}"
    
    start_minutes = time_to_minutes(schedule.start_time)
    end_minutes = time_to_minutes(schedule.end_time)
    duration = schedule.default_appointment_duration
    
    # Remove intervalo de almoço/descanso
    break_start_minutes = None
    break_end_minutes = None
    if schedule.break_start_time and schedule.break_end_time:
        break_start_minutes = time_to_minutes(schedule.break_start_time)
        break_end_minutes = time_to_minutes(schedule.break_end_time)
    
    available_slots = []
    current_minutes = start_minutes
    
    while current_minutes + duration <= end_minutes:
        time_str = minutes_to_time(current_minutes)
        
        # Verifica se está no intervalo
        if break_start_minutes and break_end_minutes:
            if break_start_minutes <= current_minutes < break_end_minutes:
                current_minutes += duration
                continue
        
        # Verifica se tem conflito com agendamentos existentes
        slot_datetime = datetime.combine(date_filter, datetime.strptime(time_str, "%H:%M").time())
        has_conflict = False
        
        for appointment in existing_appointments:
            app_start = appointment.scheduled_date
            app_end = app_start + timedelta(minutes=appointment.duration_minutes)
            slot_end = slot_datetime + timedelta(minutes=duration)
            
            # Verifica sobreposição
            if (slot_datetime < app_end) and (slot_end > app_start):
                has_conflict = True
                break
        
        if not has_conflict:
            available_slots.append(time_str)
        
        current_minutes += duration
    
    return {
        "date": date_filter.isoformat(),
        "professional_id": professional_id,
        "day_of_week": day_of_week,
        "work_hours": {
            "start": schedule.start_time,
            "end": schedule.end_time,
            "break_start": schedule.break_start_time,
            "break_end": schedule.break_end_time
        },
        "appointment_duration": duration,
        "available_slots": available_slots,
        "total_slots": len(available_slots)
    }

