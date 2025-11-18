from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from datetime import datetime, timedelta, date
from app.core.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.financial import PaymentTransaction
from app.core.security import get_current_user

router = APIRouter()

@router.get("/dashboard-admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dashboard completo para administradores da clínica"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    today = date.today()
    
    # 1. PACIENTES
    total_patients = db.query(Patient).filter(Patient.is_active == True).count()
    
    # Pacientes por gênero
    gender_stats = db.query(
        func.coalesce(Patient.gender, 'Não informado').label('gender'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.is_active == True
    ).group_by(
        func.coalesce(Patient.gender, 'Não informado')
    ).all()
    
    patients_by_gender = {gender: count for gender, count in gender_stats}
    
    # 2. CONSULTAS
    total_appointments = db.query(Appointment).count()
    
    # Consultas por status
    appointments_by_status = db.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()
    
    status_stats = {status: count for status, count in appointments_by_status}
    
    # Consultas hoje
    appointments_today = db.query(Appointment).filter(
        func.date(Appointment.scheduled_date) == today
    ).count()
    
    # Consultas próximos 7 dias
    appointments_next_7_days = db.query(Appointment).filter(
        func.date(Appointment.scheduled_date).between(today, today + timedelta(days=7))
    ).count()
    
    # Consultas por mês (últimos 6 meses)
    six_months_ago = today - timedelta(days=180)
    appointments_by_month = db.query(
        func.to_char(Appointment.scheduled_date, 'YYYY-MM').label('month'),
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.scheduled_date >= six_months_ago
    ).group_by(
        func.to_char(Appointment.scheduled_date, 'YYYY-MM')
    ).order_by('month').all()
    
    monthly_appointments = [
        {"month": month, "count": count} 
        for month, count in appointments_by_month
    ]
    
    # Taxa de comparecimento
    completed = status_stats.get('completed', 0)
    cancelled = status_stats.get('cancelled', 0)
    no_show = status_stats.get('no_show', 0)
    total_past = completed + cancelled + no_show
    attendance_rate = round((completed / total_past * 100) if total_past > 0 else 0, 1)
    
    # 3. PRONTUÁRIOS
    total_records = db.query(MedicalRecord).count()
    completed_records = db.query(MedicalRecord).filter(
        MedicalRecord.is_completed == True
    ).count()
    
    # 4. FINANCEIRO
    total_revenue = db.query(
        func.sum(PaymentTransaction.amount)
    ).filter(
        PaymentTransaction.is_confirmed == True
    ).scalar() or 0
    
    revenue_today = db.query(
        func.sum(PaymentTransaction.amount)
    ).filter(
        PaymentTransaction.is_confirmed == True,
        func.date(PaymentTransaction.payment_date) == today
    ).scalar() or 0
    
    revenue_month = db.query(
        func.sum(PaymentTransaction.amount)
    ).filter(
        PaymentTransaction.is_confirmed == True,
        extract('month', PaymentTransaction.payment_date) == today.month,
        extract('year', PaymentTransaction.payment_date) == today.year
    ).scalar() or 0
    
    # Receita por mês (últimos 6 meses)
    revenue_by_month = db.query(
        func.to_char(PaymentTransaction.payment_date, 'YYYY-MM').label('month'),
        func.sum(PaymentTransaction.amount).label('amount')
    ).filter(
        PaymentTransaction.is_confirmed == True,
        PaymentTransaction.payment_date >= six_months_ago
    ).group_by(
        func.to_char(PaymentTransaction.payment_date, 'YYYY-MM')
    ).order_by('month').all()
    
    monthly_revenue = [
        {"month": month, "amount": float(amount)} 
        for month, amount in revenue_by_month
    ]
    
    return {
        "patients": {
            "total": total_patients,
            "by_gender": patients_by_gender
        },
        "appointments": {
            "total": total_appointments,
            "today": appointments_today,
            "next_7_days": appointments_next_7_days,
            "by_status": status_stats,
            "by_month": monthly_appointments,
            "attendance_rate": attendance_rate
        },
        "medical_records": {
            "total": total_records,
            "completed": completed_records,
            "pending": total_records - completed_records
        },
        "financial": {
            "total_revenue": float(total_revenue),
            "revenue_today": float(revenue_today),
            "revenue_month": float(revenue_month),
            "by_month": monthly_revenue
        }
    }
