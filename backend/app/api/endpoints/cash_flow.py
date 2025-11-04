"""
Rotas de Fluxo de Caixa
Dashboard e Relatórios Financeiros
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import datetime, date, timedelta
from decimal import Decimal
from calendar import month_name

from app.core.database import get_db
from app.models.financial import (
    AccountReceivable, AccountPayable,
    PaymentTransaction, PayableTransaction,
    PaymentStatus, ExpenseCategory
)
from app.schemas.financial import (
    CashFlowDashboard, CashFlowPeriod,
    DailyCashFlow, MonthlyCashFlow,
    CategoryExpense, ProfessionalRevenue,
    CashFlowProjection, CashFlowAlert
)
from app.services.financial_service import financial_service

router = APIRouter(prefix="/api/v1/financial/cash-flow", tags=["Fluxo de Caixa"])


# ============================================
# DASHBOARD PRINCIPAL
# ============================================

@router.get("/dashboard", response_model=CashFlowDashboard)
def get_cash_flow_dashboard(db: Session = Depends(get_db)):
    """Dashboard principal de fluxo de caixa"""
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    month_start = datetime(today.year, today.month, 1)
    
    # Receitas de hoje
    today_income = db.query(func.sum(AccountReceivable.paid_amount)).filter(
        AccountReceivable.payment_date >= today_start,
        AccountReceivable.payment_date <= today_end,
        AccountReceivable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Despesas de hoje
    today_expense = db.query(func.sum(AccountPayable.paid_amount)).filter(
        AccountPayable.payment_date >= today_start,
        AccountPayable.payment_date <= today_end,
        AccountPayable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Receitas do mês
    month_income = db.query(func.sum(AccountReceivable.paid_amount)).filter(
        AccountReceivable.payment_date >= month_start,
        AccountReceivable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Despesas do mês
    month_expense = db.query(func.sum(AccountPayable.paid_amount)).filter(
        AccountPayable.payment_date >= month_start,
        AccountPayable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Contas a receber pendentes
    pending_receivables = db.query(func.sum(AccountReceivable.remaining_amount)).filter(
        AccountReceivable.status.in_(['PENDING', 'PARTIALLY_PAID']),
        AccountReceivable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Contas a pagar pendentes
    pending_payables = db.query(func.sum(AccountPayable.remaining_amount)).filter(
        AccountPayable.status.in_(['PENDING', 'PARTIALLY_PAID']),
        AccountPayable.is_deleted == False
    ).scalar() or Decimal(0)
    
    # Saldo atual (receitas - despesas do mês)
    current_balance = month_income - month_expense
    
    # Saldo projetado
    projected_balance = financial_service.get_projected_balance(
        current_balance,
        pending_receivables,
        pending_payables
    )
    
    return CashFlowDashboard(
        current_balance=current_balance,
        today_income=today_income,
        today_expense=today_expense,
        today_balance=today_income - today_expense,
        month_income=month_income,
        month_expense=month_expense,
        month_balance=current_balance,
        pending_receivables=pending_receivables,
        pending_payables=pending_payables,
        projected_balance=projected_balance
    )


# ============================================
# FLUXO POR PERÍODO
# ============================================

@router.get("/period", response_model=CashFlowPeriod)
def get_cash_flow_period(
    start_date: date = Query(..., description="Data inicial"),
    end_date: date = Query(..., description="Data final"),
    db: Session = Depends(get_db)
):
    """Fluxo de caixa de um período específico"""
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Receitas
    income_result = db.query(
        func.sum(AccountReceivable.paid_amount).label('total'),
        func.count(AccountReceivable.id).label('count')
    ).filter(
        AccountReceivable.payment_date >= start_datetime,
        AccountReceivable.payment_date <= end_datetime,
        AccountReceivable.is_deleted == False
    ).first()
    
    total_income = income_result.total or Decimal(0)
    income_count = income_result.count or 0
    
    # Despesas
    expense_result = db.query(
        func.sum(AccountPayable.paid_amount).label('total'),
        func.count(AccountPayable.id).label('count')
    ).filter(
        AccountPayable.payment_date >= start_datetime,
        AccountPayable.payment_date <= end_datetime,
        AccountPayable.is_deleted == False
    ).first()
    
    total_expense = expense_result.total or Decimal(0)
    expense_count = expense_result.count or 0
    
    return CashFlowPeriod(
        period_start=start_date,
        period_end=end_date,
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        income_count=income_count,
        expense_count=expense_count
    )


# ============================================
# FLUXO DIÁRIO
# ============================================

@router.get("/daily", response_model=List[DailyCashFlow])
def get_daily_cash_flow(
    days: int = Query(7, ge=1, le=90, description="Número de dias"),
    db: Session = Depends(get_db)
):
    """Fluxo de caixa diário dos últimos N dias"""
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    daily_flows = []
    
    for i in range(days + 1):
        current_date = start_date + timedelta(days=i)
        date_start = datetime.combine(current_date, datetime.min.time())
        date_end = datetime.combine(current_date, datetime.max.time())
        
        # Receitas do dia
        income = db.query(func.sum(AccountReceivable.paid_amount)).filter(
            AccountReceivable.payment_date >= date_start,
            AccountReceivable.payment_date <= date_end,
            AccountReceivable.is_deleted == False
        ).scalar() or Decimal(0)
        
        # Despesas do dia
        expense = db.query(func.sum(AccountPayable.paid_amount)).filter(
            AccountPayable.payment_date >= date_start,
            AccountPayable.payment_date <= date_end,
            AccountPayable.is_deleted == False
        ).scalar() or Decimal(0)
        
        daily_flows.append(DailyCashFlow(
            date=current_date,
            income=income,
            expense=expense,
            balance=income - expense
        ))
    
    return daily_flows


# ============================================
# FLUXO MENSAL
# ============================================

@router.get("/monthly", response_model=List[MonthlyCashFlow])
def get_monthly_cash_flow(
    months: int = Query(6, ge=1, le=24, description="Número de meses"),
    db: Session = Depends(get_db)
):
    """Fluxo de caixa mensal dos últimos N meses"""
    
    today = datetime.utcnow()
    monthly_flows = []
    
    month_names_pt = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    for i in range(months):
        # Calcula o mês
        month = today.month - i
        year = today.year
        
        while month <= 0:
            month += 12
            year -= 1
        
        month_start = datetime(year, month, 1)
        
        # Último dia do mês
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Receitas do mês
        income = db.query(func.sum(AccountReceivable.paid_amount)).filter(
            AccountReceivable.payment_date >= month_start,
            AccountReceivable.payment_date <= month_end,
            AccountReceivable.is_deleted == False
        ).scalar() or Decimal(0)
        
        # Despesas do mês
        expense = db.query(func.sum(AccountPayable.paid_amount)).filter(
            AccountPayable.payment_date >= month_start,
            AccountPayable.payment_date <= month_end,
            AccountPayable.is_deleted == False
        ).scalar() or Decimal(0)
        
        monthly_flows.append(MonthlyCashFlow(
            year=year,
            month=month,
            month_name=month_names_pt[month],
            income=income,
            expense=expense,
            balance=income - expense
        ))
    
    return list(reversed(monthly_flows))


# ============================================
# DESPESAS POR CATEGORIA
# ============================================

@router.get("/expenses-by-category", response_model=List[CategoryExpense])
def get_expenses_by_category(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Despesas agrupadas por categoria"""
    
    query = db.query(
        ExpenseCategory.id,
        ExpenseCategory.name,
        func.sum(AccountPayable.paid_amount).label('total'),
        func.count(AccountPayable.id).label('count')
    ).join(
        AccountPayable, AccountPayable.expense_category_id == ExpenseCategory.id
    ).filter(
        AccountPayable.is_deleted == False,
        AccountPayable.paid_amount > 0
    )
    
    if start_date:
        query = query.filter(AccountPayable.payment_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(AccountPayable.payment_date <= datetime.combine(end_date, datetime.max.time()))
    
    results = query.group_by(ExpenseCategory.id, ExpenseCategory.name).all()
    
    # Calcula total geral para percentuais
    total_general = sum(r.total for r in results) if results else Decimal(0)
    
    categories = []
    for result in results:
        percentage = float((result.total / total_general * 100)) if total_general > 0 else 0
        
        categories.append(CategoryExpense(
            category_id=result.id,
            category_name=result.name,
            total_amount=result.total or Decimal(0),
            percentage=round(percentage, 2),
            count=result.count
        ))
    
    return sorted(categories, key=lambda x: x.total_amount, reverse=True)


# ============================================
# PROJEÇÃO DE CAIXA
# ============================================

@router.get("/projection", response_model=List[CashFlowProjection])
def get_cash_flow_projection(
    days: int = Query(30, ge=1, le=90, description="Dias para projetar"),
    db: Session = Depends(get_db)
):
    """Projeção de fluxo de caixa futuro"""
    
    today = datetime.utcnow().date()
    projections = []
    
    for i in range(1, days + 1):
        projection_date = today + timedelta(days=i)
        date_start = datetime.combine(projection_date, datetime.min.time())
        date_end = datetime.combine(projection_date, datetime.max.time())
        
        # Contas a receber que vencem neste dia
        receivables_due = db.query(
            func.sum(AccountReceivable.remaining_amount).label('total'),
            func.count(AccountReceivable.id).label('count')
        ).filter(
            AccountReceivable.due_date >= date_start,
            AccountReceivable.due_date <= date_end,
            AccountReceivable.status.in_(['PENDING', 'PARTIALLY_PAID']),
            AccountReceivable.is_deleted == False
        ).first()
        
        # Contas a pagar que vencem neste dia
        payables_due = db.query(
            func.sum(AccountPayable.remaining_amount).label('total'),
            func.count(AccountPayable.id).label('count')
        ).filter(
            AccountPayable.due_date >= date_start,
            AccountPayable.due_date <= date_end,
            AccountPayable.status.in_(['PENDING', 'PARTIALLY_PAID']),
            AccountPayable.is_deleted == False
        ).first()
        
        projected_income = receivables_due.total or Decimal(0)
        projected_expense = payables_due.total or Decimal(0)
        
        projections.append(CashFlowProjection(
            projection_date=projection_date,
            projected_income=projected_income,
            projected_expense=projected_expense,
            projected_balance=projected_income - projected_expense,
            receivables_due=receivables_due.count or 0,
            payables_due=payables_due.count or 0
        ))
    
    return projections


# ============================================
# ALERTAS
# ============================================

@router.get("/alerts", response_model=List[CashFlowAlert])
def get_cash_flow_alerts(db: Session = Depends(get_db)):
    """Alertas de fluxo de caixa"""
    
    alerts = []
    today = datetime.utcnow()
    
    # Saldo atual
    month_start = datetime(today.year, today.month, 1)
    month_income = db.query(func.sum(AccountReceivable.paid_amount)).filter(
        AccountReceivable.payment_date >= month_start,
        AccountReceivable.is_deleted == False
    ).scalar() or Decimal(0)
    
    month_expense = db.query(func.sum(AccountPayable.paid_amount)).filter(
        AccountPayable.payment_date >= month_start,
        AccountPayable.is_deleted == False
    ).scalar() or Decimal(0)
    
    current_balance = month_income - month_expense
    
    # Alerta de saldo baixo
    if current_balance < 1000:
        alerts.append(CashFlowAlert(
            alert_type="low_balance",
            severity="high" if current_balance < 500 else "medium",
            message=f"Saldo baixo: {financial_service.format_currency(current_balance)}",
            value=current_balance
        ))
    
    # Contas vencidas a receber
    overdue_receivables = db.query(func.count(AccountReceivable.id)).filter(
        AccountReceivable.status == PaymentStatus.OVERDUE.value,
        AccountReceivable.is_deleted == False
    ).scalar() or 0
    
    if overdue_receivables > 0:
        alerts.append(CashFlowAlert(
            alert_type="overdue_receivables",
            severity="medium",
            message=f"{overdue_receivables} conta(s) a receber vencida(s)"
        ))
    
    # Contas vencidas a pagar
    overdue_payables = db.query(func.count(AccountPayable.id)).filter(
        AccountPayable.due_date < today,
        AccountPayable.status.in_(['PENDING', 'PARTIALLY_PAID']),
        AccountPayable.is_deleted == False
    ).scalar() or 0
    
    if overdue_payables > 0:
        alerts.append(CashFlowAlert(
            alert_type="overdue_payables",
            severity="high",
            message=f"{overdue_payables} conta(s) a pagar vencida(s)"
        ))
    
    return alerts
