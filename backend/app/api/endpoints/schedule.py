from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, time, timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.professional_schedule import ProfessionalSchedule, ScheduleBlock
from app.models.appointment import Appointment
from app.schemas.schedule import (
    ProfessionalScheduleCreate,
    ProfessionalScheduleUpdate,
    ProfessionalScheduleResponse,
    ProfessionalScheduleBulkCreate,
    ScheduleBlockCreate,
    ScheduleBlockUpdate,
    ScheduleBlockResponse,
    AvailabilityRequest,
    AvailabilityResponse,
    TimeSlot,
    WeekScheduleResponse
)

router = APIRouter()

# ==========================================
# PROFESSIONAL SCHEDULES (Horários de Trabalho)
# ==========================================

@router.get("/my-schedule", response_model=WeekScheduleResponse)
def get_my_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter minha configuração de horários da semana"""
    schedules = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.user_id == current_user.id,
        ProfessionalSchedule.is_active == True
    ).order_by(ProfessionalSchedule.day_of_week).all()
    
    return WeekScheduleResponse(
        user_id=current_user.id,
        schedules=schedules
    )

@router.get("/schedule/{user_id}", response_model=WeekScheduleResponse)
def get_user_schedule(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter horários de um profissional específico"""
    schedules = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.user_id == user_id,
        ProfessionalSchedule.is_active == True
    ).order_by(ProfessionalSchedule.day_of_week).all()
    
    return WeekScheduleResponse(
        user_id=user_id,
        schedules=schedules
    )

@router.post("/schedule", response_model=ProfessionalScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule_data: ProfessionalScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar configuração de horário para um dia específico"""
    # Verificar se já existe horário para este dia
    existing = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.user_id == schedule_data.user_id,
        ProfessionalSchedule.day_of_week == schedule_data.day_of_week,
        ProfessionalSchedule.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe horário configurado para este dia da semana"
        )
    
    schedule = ProfessionalSchedule(**schedule_data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    return schedule

@router.post("/schedule/bulk", response_model=List[ProfessionalScheduleResponse])
def create_schedule_bulk(
    bulk_data: ProfessionalScheduleBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar horários para múltiplos dias de uma vez"""
    # Verificar permissão
    if current_user.id != bulk_data.user_id and current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode configurar seus próprios horários"
        )
    
    # Desativar horários existentes
    db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.user_id == bulk_data.user_id
    ).update({ProfessionalSchedule.is_active: False})
    
    # Criar novos horários
    created_schedules = []
    for schedule_data in bulk_data.schedules:
        schedule = ProfessionalSchedule(
            user_id=bulk_data.user_id,
            **schedule_data.model_dump()
        )
        db.add(schedule)
        created_schedules.append(schedule)
    
    db.commit()
    
    for schedule in created_schedules:
        db.refresh(schedule)
    
    return created_schedules

@router.put("/schedule/{schedule_id}", response_model=ProfessionalScheduleResponse)
def update_schedule(
    schedule_id: UUID,
    schedule_data: ProfessionalScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar horário de trabalho"""
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horário não encontrado"
        )
    
    # Atualizar campos
    for field, value in schedule_data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    db.commit()
    db.refresh(schedule)
    
    return schedule

@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar horário de trabalho"""
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.id == schedule_id
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horário não encontrado"
        )
    
    schedule.is_active = False
    db.commit()
    
    return None

# ==========================================
# SCHEDULE BLOCKS (Bloqueios)
# ==========================================

@router.get("/blocks", response_model=List[ScheduleBlockResponse])
def list_blocks(
    user_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar bloqueios de horários"""
    query = db.query(ScheduleBlock).filter(ScheduleBlock.is_active == True)
    
    if user_id:
        query = query.filter(ScheduleBlock.user_id == user_id)
    
    if start_date:
        query = query.filter(ScheduleBlock.block_date >= start_date)
    
    if end_date:
        query = query.filter(ScheduleBlock.block_date <= end_date)
    
    blocks = query.order_by(ScheduleBlock.block_date).all()
    return blocks

@router.post("/blocks", response_model=ScheduleBlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    block_data: ScheduleBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar bloqueio de horário"""
    block = ScheduleBlock(**block_data.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    
    return block

@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remover bloqueio"""
    block = db.query(ScheduleBlock).filter(ScheduleBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bloqueio não encontrado"
        )
    
    block.is_active = False
    db.commit()
    
    return None

# ==========================================
# AVAILABILITY (Disponibilidade)
# ==========================================

@router.post("/availability", response_model=AvailabilityResponse)
def get_availability(
    request: AvailabilityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calcular horários disponíveis para um profissional em uma data"""
    user = db.query(User).filter(User.id == request.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    
    # Pegar dia da semana (0=segunda, 6=domingo)
    day_of_week = request.date.weekday()
    
    # Buscar configuração de horário para este dia
    schedule = db.query(ProfessionalSchedule).filter(
        ProfessionalSchedule.user_id == request.user_id,
        ProfessionalSchedule.day_of_week == day_of_week,
        ProfessionalSchedule.is_active == True
    ).first()
    
    if not schedule:
        return AvailabilityResponse(
            date=request.date,
            professional_id=request.user_id,
            professional_name=user.full_name,
            available_slots=[],
            total_slots=0
        )
    
    # Gerar slots disponíveis
    available_slots = generate_time_slots(
        request.date.date(),
        schedule,
        request.duration_minutes or schedule.default_duration_minutes,
        db,
        request.user_id
    )
    
    return AvailabilityResponse(
        date=request.date,
        professional_id=request.user_id,
        professional_name=user.full_name,
        available_slots=available_slots,
        total_slots=len(available_slots)
    )

def generate_time_slots(
    date,
    schedule: ProfessionalSchedule,
    duration_minutes: int,
    db: Session,
    user_id: UUID
) -> List[TimeSlot]:
    """Gerar slots de tempo disponíveis baseado na configuração"""
    slots = []
    
    # Horário atual
    current_time = datetime.combine(date, schedule.start_time)
    end_time = datetime.combine(date, schedule.end_time)
    
    # Intervalo
    break_start = datetime.combine(date, schedule.break_start) if schedule.break_start else None
    break_end = datetime.combine(date, schedule.break_end) if schedule.break_end else None
    
    # Buscar consultas já agendadas
    appointments = db.query(Appointment).filter(
        Appointment.healthcare_professional_id == user_id,
        Appointment.scheduled_date >= current_time,
        Appointment.scheduled_date < end_time,
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).all()
    
    busy_slots = [(apt.scheduled_date, apt.scheduled_date + timedelta(minutes=apt.duration_minutes)) for apt in appointments]
    
    # Gerar slots
    while current_time + timedelta(minutes=duration_minutes) <= end_time:
        slot_end = current_time + timedelta(minutes=duration_minutes)
        
        # Verificar se está no intervalo
        if break_start and break_end:
            if not (current_time >= break_end or slot_end <= break_start):
                current_time += timedelta(minutes=duration_minutes)
                continue
        
        # Verificar se está ocupado
        is_busy = False
        for busy_start, busy_end in busy_slots:
            if not (slot_end <= busy_start or current_time >= busy_end):
                is_busy = True
                break
        
        if not is_busy and current_time >= datetime.now():
            slots.append(TimeSlot(
                start=current_time,
                end=slot_end,
                duration_minutes=duration_minutes
            ))
        
        current_time += timedelta(minutes=duration_minutes)
    
    return slots
