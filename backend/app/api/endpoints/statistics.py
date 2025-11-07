from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.medical_record import MedicalRecord

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Métricas gerais do dashboard"""
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    total_patients = db.query(func.count(Patient.id)).filter(
        Patient.created_at >= start_date,
        Patient.created_at <= end_date
    ).scalar() or 0
    
    consultas_previstas = db.query(func.count(Appointment.id)).filter(
        Appointment.scheduled_date >= start_date,
        Appointment.scheduled_date <= end_date
    ).scalar() or 0
    
    consultas_realizadas = db.query(func.count(Appointment.id)).filter(
        Appointment.scheduled_date >= start_date,
        Appointment.scheduled_date <= end_date,
        Appointment.status == "completed"
    ).scalar() or 0
    
    total_prontuarios = db.query(func.count(MedicalRecord.id)).filter(
        MedicalRecord.created_at >= start_date,
        MedicalRecord.created_at <= end_date
    ).scalar() or 0
    
    total_pacientes_geral = db.query(func.count(Patient.id)).scalar() or 0
    
    taxa_realizacao = round((consultas_realizadas / consultas_previstas * 100), 2) if consultas_previstas > 0 else 0
    
    return {
        "periodo": {
            "inicio": start_date,
            "fim": end_date
        },
        "metricas": {
            "pacientes_periodo": total_patients,
            "consultas_previstas": consultas_previstas,
            "consultas_realizadas": consultas_realizadas,
            "taxa_realizacao": taxa_realizacao,
            "total_prontuarios": total_prontuarios,
            "total_pacientes": total_pacientes_geral
        }
    }


@router.get("/patients-by-month")
async def get_patients_by_month(db: Session = Depends(get_db)):
    """Novos pacientes por mês (últimos 6 meses)"""
    
    six_months_ago = datetime.now() - timedelta(days=180)
    
    result = db.query(
        extract('month', Patient.created_at).label('month'),
        extract('year', Patient.created_at).label('year'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.created_at >= six_months_ago
    ).group_by('month', 'year').order_by('year', 'month').all()
    
    months = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    
    return [
        {
            "period": f"{months[int(r.month)]}/{int(r.year)}",
            "count": r.count
        }
        for r in result
    ]


@router.get("/appointments-by-status")
async def get_appointments_by_status(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Agendamentos por status"""
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    result = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.scheduled_date >= start_date,
        Appointment.scheduled_date <= end_date
    ).group_by(Appointment.status).all()
    
    status_map = {
        "scheduled": "Agendado",
        "confirmed": "Confirmado", 
        "completed": "Realizado",
        "cancelled": "Cancelado",
        "no_show": "Faltou"
    }
    
    if not result:
        return []
    
    return [
        {
            "status": status_map.get(r.status, r.status or "Sem status"),
            "count": r.count
        }
        for r in result
    ]


@router.get("/patients-activity")
async def get_patients_activity(db: Session = Depends(get_db)):
    """Pacientes ativos vs inativos"""
    
    active = db.query(func.count(Patient.id)).filter(
        Patient.is_active == True
    ).scalar() or 0
    
    inactive = db.query(func.count(Patient.id)).filter(
        Patient.is_active == False
    ).scalar() or 0
    
    return [
        {"status": "Ativos", "count": active},
        {"status": "Inativos", "count": inactive}
    ]
