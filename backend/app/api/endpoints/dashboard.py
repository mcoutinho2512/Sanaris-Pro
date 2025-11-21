"""
Endpoints de Dashboard
Estatísticas e métricas do sistema
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Estatísticas gerais do dashboard"""
    
    org_filter = current_user.organization_id if current_user.role != 'super_admin' else None
    
    # Total de pacientes
    query = db.query(func.count(Patient.id))
    if org_filter:
        query = query.filter(Patient.organization_id == org_filter)
    total_patients = query.scalar()
    
    # Total de consultas
    total_appointments = db.query(func.count(Appointment.id)).scalar()
    
    # Consultas hoje
    today = datetime.utcnow().date()
    appointments_today = db.query(func.count(Appointment.id)).filter(
        func.date(Appointment.scheduled_date) == today
    ).scalar()
    
    # Consultas pendentes
    pending_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.status.in_(['scheduled', 'confirmed'])
    ).scalar()
    
    # Total de prescrições
    total_prescriptions = db.query(func.count(Prescription.id)).scalar()
    
    # Novos pacientes este mês
    first_day_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    query = db.query(func.count(Patient.id)).filter(Patient.created_at >= first_day_month)
    if org_filter:
        query = query.filter(Patient.organization_id == org_filter)
    new_patients_month = query.scalar()
    
    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "appointments_today": appointments_today,
        "pending_appointments": pending_appointments,
        "total_prescriptions": total_prescriptions,
        "new_patients_month": new_patients_month
    }


@router.get("/appointments/by-month")
async def get_appointments_by_month(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultas por mês (últimos 12 meses)"""
    
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    
    results = db.query(
        extract('year', Appointment.scheduled_date).label('year'),
        extract('month', Appointment.scheduled_date).label('month'),
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.scheduled_date >= twelve_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    months = []
    counts = []
    
    for r in results:
        month_name = datetime(int(r.year), int(r.month), 1).strftime('%b/%Y')
        months.append(month_name)
        counts.append(r.count)
    
    return {
        "labels": months,
        "data": counts
    }


@router.get("/appointments/by-status")
async def get_appointments_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Distribuição de consultas por status"""
    
    results = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()
    
    status_map = {
        'scheduled': 'Agendada',
        'confirmed': 'Confirmada',
        'completed': 'Concluída',
        'cancelled': 'Cancelada',
        'no_show': 'Não Compareceu'
    }
    
    labels = [status_map.get(r.status, r.status) for r in results]
    data = [r.count for r in results]
    
    return {
        "labels": labels,
        "data": data
    }


@router.get("/patients/by-gender")
async def get_patients_by_gender(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Distribuição de pacientes por gênero"""
    
    org_filter = current_user.organization_id if current_user.role != 'super_admin' else None
    
    query = db.query(
        Patient.gender,
        func.count(Patient.id).label('count')
    ).group_by(Patient.gender)
    
    if org_filter:
        query = query.filter(Patient.organization_id == org_filter)
    
    results = query.all()
    
    gender_map = {
        'male': 'Masculino',
        'female': 'Feminino',
        'other': 'Outro',
        None: 'Não informado'
    }
    
    labels = [gender_map.get(r.gender, 'Não informado') for r in results]
    data = [r.count for r in results]
    
    return {
        "labels": labels,
        "data": data
    }
