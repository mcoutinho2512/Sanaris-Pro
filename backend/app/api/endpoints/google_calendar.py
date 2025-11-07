from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.services.google_calendar_service import GoogleCalendarService
from pydantic import BaseModel

router = APIRouter()


class CalendarEventCreate(BaseModel):
    appointment_id: str
    send_notifications: bool = True


class CalendarEventResponse(BaseModel):
    success: bool
    event_id: Optional[str] = None
    html_link: Optional[str] = None
    message: str


@router.post("/sync-appointment", response_model=CalendarEventResponse)
async def sync_appointment_to_calendar(
    data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sincronizar agendamento com Google Calendar"""
    
    # Verificar se user tem access_token do Google
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não autenticado com Google. Faça login com Google primeiro."
        )
    
    # Buscar appointment
    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    # Buscar paciente
    patient = db.query(Patient).filter(
        Patient.id == appointment.patient_id
    ).first()
    
    # Calcular end_time
    start_time = appointment.scheduled_date
    end_time = start_time + timedelta(minutes=appointment.duration_minutes)
    
    # Criar evento no Google Calendar
    result = GoogleCalendarService.create_event(
        access_token=current_user.google_access_token,
        summary=f"Consulta - {patient.full_name if patient else 'Paciente'}",
        description=f"Tipo: {appointment.appointment_type}\nObservações: {appointment.notes or 'N/A'}",
        start_datetime=start_time,
        end_datetime=end_time,
        attendee_email=patient.email if patient and patient.email else None,
        location=appointment.location or "Clínica"
    )
    
    if result.get('success'):
        # Salvar event_id no banco
        appointment.google_calendar_event_id = result.get('event_id')
        db.commit()
        
        return CalendarEventResponse(
            success=True,
            event_id=result.get('event_id'),
            html_link=result.get('html_link'),
            message="Agendamento sincronizado com Google Calendar!"
        )
    else:
        return CalendarEventResponse(
            success=False,
            message=f"Erro ao sincronizar: {result.get('error')}"
        )


@router.delete("/sync-appointment/{appointment_id}")
async def remove_from_calendar(
    appointment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remover agendamento do Google Calendar"""
    
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não autenticado com Google"
        )
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado"
        )
    
    if not appointment.google_calendar_event_id:
        return {"message": "Agendamento não está sincronizado com Google Calendar"}
    
    # Deletar do Google Calendar
    result = GoogleCalendarService.delete_event(
        access_token=current_user.google_access_token,
        event_id=appointment.google_calendar_event_id
    )
    
    if result.get('success'):
        appointment.google_calendar_event_id = None
        db.commit()
        return {"message": "Removido do Google Calendar com sucesso"}
    else:
        return {"message": f"Erro ao remover: {result.get('error')}"}


@router.get("/events")
async def list_calendar_events(
    max_results: int = 10,
    current_user: User = Depends(get_current_active_user)
):
    """Listar próximos eventos do Google Calendar"""
    
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não autenticado com Google"
        )
    
    result = GoogleCalendarService.list_events(
        access_token=current_user.google_access_token,
        max_results=max_results
    )
    
    return result
