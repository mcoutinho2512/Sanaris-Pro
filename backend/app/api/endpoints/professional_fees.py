"""
Rotas de Repasse Profissionais
Gestão de Comissões e Pagamentos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, extract
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from calendar import monthrange

from app.core.database import get_db
from app.models.financial import (
    ProfessionalFeeConfiguration, ProfessionalFee, ProfessionalFeeItem,
    AccountReceivable, PaymentStatus, ProfessionalFeeType
)
from app.schemas.financial import (
    ProfessionalFeeConfigurationCreate, ProfessionalFeeConfigurationUpdate,
    ProfessionalFeeConfigurationResponse,
    ProfessionalFeeResponse, ProfessionalFeeListResponse,
    ProfessionalFeeItemResponse,
    GenerateFeeRequest, PayFeeRequest,
    ProfessionalFeeSummary, MonthlyFeeSummary,
    MONTH_NAMES
)
from app.services.financial_service import financial_service

router = APIRouter(prefix="/api/v1/financial/professional-fees", tags=["Repasse Profissionais"])


# ============================================
# CONFIGURAÇÃO DE REPASSE
# ============================================

@router.post("/configurations", response_model=ProfessionalFeeConfigurationResponse, status_code=status.HTTP_201_CREATED)
def create_fee_configuration(config_data: ProfessionalFeeConfigurationCreate, db: Session = Depends(get_db)):
    """Cria configuração de repasse para profissional"""
    
    # Verifica se já existe configuração
    existing = db.query(ProfessionalFeeConfiguration).filter(
        ProfessionalFeeConfiguration.healthcare_professional_id == config_data.healthcare_professional_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profissional já possui configuração de repasse"
        )
    
    # Valida dados conforme tipo
    if config_data.fee_type == ProfessionalFeeType.PERCENTAGE:
        if not config_data.percentage or config_data.percentage <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentual deve ser informado para tipo 'percentage'"
            )
    elif config_data.fee_type == ProfessionalFeeType.FIXED:
        if not config_data.fixed_amount or config_data.fixed_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor fixo deve ser informado para tipo 'fixed'"
            )
    
    config = ProfessionalFeeConfiguration(**config_data.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.get("/configurations", response_model=List[ProfessionalFeeConfigurationResponse])
def list_fee_configurations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista configurações de repasse"""
    
    query = db.query(ProfessionalFeeConfiguration)
    
    if is_active is not None:
        query = query.filter(ProfessionalFeeConfiguration.is_active == is_active)
    
    configs = query.offset(skip).limit(limit).all()
    
    return configs


@router.get("/configurations/{professional_id}", response_model=ProfessionalFeeConfigurationResponse)
def get_fee_configuration(professional_id: str, db: Session = Depends(get_db)):
    """Busca configuração de repasse do profissional"""
    
    config = db.query(ProfessionalFeeConfiguration).filter(
        ProfessionalFeeConfiguration.healthcare_professional_id == professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    
    return config


@router.put("/configurations/{professional_id}", response_model=ProfessionalFeeConfigurationResponse)
def update_fee_configuration(
    professional_id: str,
    config_data: ProfessionalFeeConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza configuração de repasse"""
    
    config = db.query(ProfessionalFeeConfiguration).filter(
        ProfessionalFeeConfiguration.healthcare_professional_id == professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    
    update_data = config_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/configurations/{professional_id}")
def delete_fee_configuration(professional_id: str, db: Session = Depends(get_db)):
    """Deleta configuração de repasse"""
    
    config = db.query(ProfessionalFeeConfiguration).filter(
        ProfessionalFeeConfiguration.healthcare_professional_id == professional_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    
    db.delete(config)
    db.commit()
    
    return {"message": "Configuração deletada com sucesso", "success": True}


# ============================================
# GERAÇÃO DE REPASSE
# ============================================

@router.post("/generate", response_model=ProfessionalFeeResponse, status_code=status.HTTP_201_CREATED)
def generate_professional_fee(generate_data: GenerateFeeRequest, db: Session = Depends(get_db)):
    """Gera repasse para um profissional em um período"""
    
    # Busca configuração
    config = db.query(ProfessionalFeeConfiguration).filter(
        ProfessionalFeeConfiguration.healthcare_professional_id == generate_data.healthcare_professional_id,
        ProfessionalFeeConfiguration.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não possui configuração de repasse ativa"
        )
    
    # Verifica se já existe repasse para este período
    existing = db.query(ProfessionalFee).filter(
        ProfessionalFee.healthcare_professional_id == generate_data.healthcare_professional_id,
        ProfessionalFee.reference_month == generate_data.reference_month,
        ProfessionalFee.reference_year == generate_data.reference_year,
        ProfessionalFee.is_deleted == False
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe repasse gerado para este período"
        )
    
    # Define período
    period_start = datetime(generate_data.reference_year, generate_data.reference_month, 1)
    last_day = monthrange(generate_data.reference_year, generate_data.reference_month)[1]
    period_end = datetime(generate_data.reference_year, generate_data.reference_month, last_day, 23, 59, 59)
    
    # Busca contas pagas no período
    receivables = db.query(AccountReceivable).filter(
        AccountReceivable.healthcare_professional_id == generate_data.healthcare_professional_id,
        AccountReceivable.payment_date >= period_start,
        AccountReceivable.payment_date <= period_end,
        AccountReceivable.status == PaymentStatus.PAID.value,
        AccountReceivable.is_deleted == False
    ).all()
    
    if not receivables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há atendimentos pagos no período selecionado"
        )
    
    # Calcula valores
    gross_amount = Decimal(0)
    total_revenue = Decimal(0)
    total_appointments = len(receivables)
    
    fee_items = []
    
    for receivable in receivables:
        total_revenue += receivable.paid_amount
        
        # Calcula repasse baseado na configuração
        if config.fee_type == ProfessionalFeeType.PERCENTAGE.value:
            fee_amount = receivable.paid_amount * (config.percentage / 100)
        else:  # FIXED
            fee_amount = config.fixed_amount
        
        gross_amount += fee_amount
        
        # Cria item
        fee_items.append({
            'account_receivable_id': receivable.id,
            'appointment_id': receivable.appointment_id,
            'description': receivable.description,
            'service_amount': receivable.paid_amount,
            'fee_amount': fee_amount,
            'service_date': receivable.payment_date
        })
    
    # Calcula retenções
    inss_amount = Decimal(0)
    ir_amount = Decimal(0)
    iss_amount = Decimal(0)
    
    if config.apply_inss:
        inss_amount = gross_amount * (config.inss_rate / 100)
    
    if config.apply_ir:
        ir_amount = gross_amount * (config.ir_rate / 100)
    
    if config.apply_iss:
        iss_amount = gross_amount * (config.iss_rate / 100)
    
    # Valor líquido
    net_amount = gross_amount - inss_amount - ir_amount - iss_amount - config.other_deductions
    
    # Verifica valor mínimo
    if config.minimum_amount and net_amount < config.minimum_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor líquido ({net_amount}) é menor que o valor mínimo configurado ({config.minimum_amount})"
        )
    
    # Gera número do repasse
    fee_number = financial_service.generate_invoice_number(prefix="REP")
    
    # Cria repasse
    fee = ProfessionalFee(
        fee_number=fee_number,
        healthcare_professional_id=generate_data.healthcare_professional_id,
        reference_month=generate_data.reference_month,
        reference_year=generate_data.reference_year,
        period_start=period_start,
        period_end=period_end,
        gross_amount=gross_amount,
        inss_amount=inss_amount,
        ir_amount=ir_amount,
        iss_amount=iss_amount,
        other_deductions=config.other_deductions,
        net_amount=net_amount,
        total_appointments=total_appointments,
        total_revenue=total_revenue
    )
    
    db.add(fee)
    db.flush()  # Para obter o ID
    
    # Cria itens
    for item_data in fee_items:
        item = ProfessionalFeeItem(
            professional_fee_id=fee.id,
            **item_data
        )
        db.add(item)
    
    db.commit()
    db.refresh(fee)
    
    return fee


# ============================================
# REPASSES - CRUD
# ============================================

@router.get("", response_model=List[ProfessionalFeeListResponse])
def list_professional_fees(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    professional_id: Optional[str] = None,
    status: Optional[str] = None,
    reference_year: Optional[int] = None,
    reference_month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista repasses de profissionais"""
    
    query = db.query(ProfessionalFee).filter(ProfessionalFee.is_deleted == False)
    
    if professional_id:
        query = query.filter(ProfessionalFee.healthcare_professional_id == professional_id)
    
    if status:
        query = query.filter(ProfessionalFee.status == status)
    
    if reference_year:
        query = query.filter(ProfessionalFee.reference_year == reference_year)
    
    if reference_month:
        query = query.filter(ProfessionalFee.reference_month == reference_month)
    
    fees = query.order_by(desc(ProfessionalFee.created_at)).offset(skip).limit(limit).all()
    
    return fees


@router.get("/{fee_id}", response_model=ProfessionalFeeResponse)
def get_professional_fee(fee_id: str, db: Session = Depends(get_db)):
    """Busca repasse por ID"""
    
    fee = db.query(ProfessionalFee).filter(
        ProfessionalFee.id == fee_id,
        ProfessionalFee.is_deleted == False
    ).first()
    
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repasse não encontrado"
        )
    
    return fee


@router.get("/{fee_id}/items", response_model=List[ProfessionalFeeItemResponse])
def list_fee_items(fee_id: str, db: Session = Depends(get_db)):
    """Lista itens do repasse"""
    
    items = db.query(ProfessionalFeeItem).filter(
        ProfessionalFeeItem.professional_fee_id == fee_id
    ).order_by(ProfessionalFeeItem.service_date).all()
    
    return items


@router.delete("/{fee_id}")
def delete_professional_fee(fee_id: str, db: Session = Depends(get_db)):
    """Deleta repasse (soft delete)"""
    
    fee = db.query(ProfessionalFee).filter(
        ProfessionalFee.id == fee_id,
        ProfessionalFee.is_deleted == False
    ).first()
    
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repasse não encontrado"
        )
    
    if fee.status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar repasse já pago"
        )
    
    fee.is_deleted = True
    fee.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Repasse deletado com sucesso", "success": True}


# ============================================
# PAGAMENTO DE REPASSE
# ============================================

@router.post("/pay")
def pay_professional_fee(pay_data: PayFeeRequest, db: Session = Depends(get_db)):
    """Registra pagamento de repasse"""
    
    fee = db.query(ProfessionalFee).filter(
        ProfessionalFee.id == pay_data.fee_id,
        ProfessionalFee.is_deleted == False
    ).first()
    
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repasse não encontrado"
        )
    
    if fee.status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repasse já foi pago"
        )
    
    fee.status = PaymentStatus.PAID.value
    fee.payment_date = pay_data.payment_date or datetime.utcnow()
    fee.payment_method = pay_data.payment_method.value
    fee.payment_reference = pay_data.payment_reference
    
    if pay_data.notes:
        fee.notes = f"{fee.notes or ''}\n{pay_data.notes}"
    
    db.commit()
    
    return {"message": "Repasse pago com sucesso", "success": True}


# ============================================
# RELATÓRIOS
# ============================================

@router.get("/reports/by-professional/{professional_id}", response_model=ProfessionalFeeSummary)
def get_professional_summary(
    professional_id: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Resumo de repasses de um profissional"""
    
    query = db.query(ProfessionalFee).filter(
        ProfessionalFee.healthcare_professional_id == professional_id,
        ProfessionalFee.is_deleted == False
    )
    
    if year:
        query = query.filter(ProfessionalFee.reference_year == year)
    
    fees = query.all()
    
    total_fees = len(fees)
    total_gross = sum(fee.gross_amount for fee in fees)
    total_net = sum(fee.net_amount for fee in fees)
    total_deductions = total_gross - total_net
    
    pending_amount = sum(
        fee.net_amount for fee in fees 
        if fee.status != PaymentStatus.PAID.value
    )
    
    paid_amount = sum(
        fee.net_amount for fee in fees 
        if fee.status == PaymentStatus.PAID.value
    )
    
    return ProfessionalFeeSummary(
        professional_id=professional_id,
        total_fees=total_fees,
        total_gross=total_gross,
        total_net=total_net,
        total_deductions=total_deductions,
        pending_amount=pending_amount,
        paid_amount=paid_amount
    )


@router.get("/reports/monthly", response_model=List[MonthlyFeeSummary])
def get_monthly_summary(
    year: int = Query(..., ge=2020, le=2100),
    db: Session = Depends(get_db)
):
    """Resumo mensal de repasses"""
    
    summaries = []
    
    for month in range(1, 13):
        fees = db.query(ProfessionalFee).filter(
            ProfessionalFee.reference_year == year,
            ProfessionalFee.reference_month == month,
            ProfessionalFee.is_deleted == False
        ).all()
        
        if fees:
            total_professionals = len(set(fee.healthcare_professional_id for fee in fees))
            total_fees = len(fees)
            total_gross = sum(fee.gross_amount for fee in fees)
            total_net = sum(fee.net_amount for fee in fees)
            total_deductions = total_gross - total_net
            
            summaries.append(MonthlyFeeSummary(
                year=year,
                month=month,
                month_name=MONTH_NAMES[month],
                total_professionals=total_professionals,
                total_fees=total_fees,
                total_gross=total_gross,
                total_net=total_net,
                total_deductions=total_deductions
            ))
    
    return summaries
