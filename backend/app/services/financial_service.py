"""
Serviço de Gestão Financeira
Lógica de negócio para contas a receber
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import secrets


class FinancialService:
    """Serviço de gestão financeira"""
    
    def generate_invoice_number(self, prefix: str = "FAT") -> str:
        """
        Gera número de fatura único
        
        Formato: FAT-YYYYMMDD-XXXX
        Exemplo: FAT-20251103-A5D2
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = secrets.token_hex(2).upper()
        return f"{prefix}-{date_str}-{random_str}"
    
    def generate_transaction_number(self, prefix: str = "TRX") -> str:
        """
        Gera número de transação único
        
        Formato: TRX-YYYYMMDDHHMMSS-XXXX
        Exemplo: TRX-20251103143025-B7F3
        """
        datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(2).upper()
        return f"{prefix}-{datetime_str}-{random_str}"
    
    def calculate_total_amount(
        self,
        original_amount: Decimal,
        discount_amount: Decimal = Decimal(0),
        interest_amount: Decimal = Decimal(0),
        fine_amount: Decimal = Decimal(0)
    ) -> Decimal:
        """Calcula valor total"""
        total = original_amount - discount_amount + interest_amount + fine_amount
        return round(total, 2)
    
    def calculate_interest(
        self,
        amount: Decimal,
        daily_rate: Decimal,
        days_overdue: int
    ) -> Decimal:
        """
        Calcula juros de mora
        
        Args:
            amount: Valor principal
            daily_rate: Taxa diária (ex: 0.033 para 1% ao mês)
            days_overdue: Dias de atraso
        
        Returns:
            Valor dos juros
        """
        if days_overdue <= 0:
            return Decimal(0)
        
        interest = amount * (daily_rate / 100) * days_overdue
        return round(interest, 2)
    
    def calculate_fine(
        self,
        amount: Decimal,
        fine_rate: Decimal
    ) -> Decimal:
        """
        Calcula multa por atraso
        
        Args:
            amount: Valor principal
            fine_rate: Taxa de multa (ex: 2.0 para 2%)
        
        Returns:
            Valor da multa
        """
        fine = amount * (fine_rate / 100)
        return round(fine, 2)
    
    def calculate_overdue_charges(
        self,
        original_amount: Decimal,
        due_date: datetime,
        charge_interest: bool = True,
        interest_rate_daily: Decimal = Decimal(0.033),
        charge_fine: bool = True,
        fine_rate: Decimal = Decimal(2.0)
    ) -> Dict[str, Any]:
        """
        Calcula juros e multa para conta vencida
        
        Returns:
            Dict com interest_amount, fine_amount, days_overdue
        """
        days_overdue = (datetime.utcnow() - due_date).days
        
        if days_overdue <= 0:
            return {
                "interest_amount": Decimal(0),
                "fine_amount": Decimal(0),
                "days_overdue": 0
            }
        
        interest = self.calculate_interest(
            original_amount,
            interest_rate_daily,
            days_overdue
        ) if charge_interest else Decimal(0)
        
        fine = self.calculate_fine(
            original_amount,
            fine_rate
        ) if charge_fine else Decimal(0)
        
        return {
            "interest_amount": interest,
            "fine_amount": fine,
            "days_overdue": days_overdue
        }
    
    def generate_installments(
        self,
        total_amount: Decimal,
        num_installments: int,
        first_due_date: datetime,
        interval_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Gera parcelas de pagamento
        
        Args:
            total_amount: Valor total
            num_installments: Número de parcelas
            first_due_date: Data de vencimento da primeira
            interval_days: Intervalo entre parcelas
        
        Returns:
            Lista de dicts com dados das parcelas
        """
        installments = []
        amount_per_installment = round(total_amount / num_installments, 2)
        
        # Ajusta última parcela para compensar arredondamento
        total_calculated = amount_per_installment * num_installments
        difference = total_amount - total_calculated
        
        for i in range(num_installments):
            installment_amount = amount_per_installment
            
            # Adiciona diferença na última parcela
            if i == num_installments - 1:
                installment_amount += difference
            
            installment = {
                "installment_number": i + 1,
                "original_amount": installment_amount,
                "total_amount": installment_amount,
                "due_date": first_due_date + timedelta(days=interval_days * i)
            }
            
            installments.append(installment)
        
        return installments
    
    def calculate_next_recurrence_date(
        self,
        current_date: datetime,
        recurrence_type: str,
        recurrence_day: Optional[int] = None
    ) -> datetime:
        """
        Calcula próxima data de recorrência
        
        Args:
            current_date: Data atual
            recurrence_type: Tipo de recorrência
            recurrence_day: Dia do mês (se aplicável)
        
        Returns:
            Próxima data de recorrência
        """
        if recurrence_type == "monthly":
            # Próximo mês, mesmo dia
            if recurrence_day:
                next_month = current_date.month + 1
                next_year = current_date.year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                return datetime(next_year, next_month, min(recurrence_day, 28))
            else:
                return current_date + timedelta(days=30)
        
        elif recurrence_type == "bimonthly":
            return current_date + timedelta(days=60)
        
        elif recurrence_type == "quarterly":
            return current_date + timedelta(days=90)
        
        elif recurrence_type == "semiannual":
            return current_date + timedelta(days=180)
        
        elif recurrence_type == "annual":
            return current_date + timedelta(days=365)
        
        return current_date
    
    def determine_payment_status(
        self,
        total_amount: Decimal,
        paid_amount: Decimal,
        due_date: datetime,
        is_cancelled: bool = False
    ) -> str:
        """
        Determina status de pagamento
        
        Returns:
            Status: pending, paid, overdue, partially_paid, cancelled
        """
        if is_cancelled:
            return "cancelled"
        
        if paid_amount >= total_amount:
            return "paid"
        
        if paid_amount > 0:
            return "partially_paid"
        
        if datetime.utcnow() > due_date:
            return "overdue"
        
        return "pending"
    
    def format_currency(self, amount: Decimal) -> str:
        """
        Formata valor em real brasileiro
        
        Args:
            amount: Valor
        
        Returns:
            String formatada (ex: "R$ 1.500,50")
        """
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    
    # ============================================
    # FLUXO DE CAIXA
    # ============================================
    
    def calculate_cash_balance(
        self,
        receivables_paid: Decimal,
        payables_paid: Decimal,
        initial_balance: Decimal = Decimal(0)
    ) -> Decimal:
        """Calcula saldo de caixa"""
        balance = initial_balance + receivables_paid - payables_paid
        return round(balance, 2)
    
    def get_period_summary(
        self,
        start_date,
        end_date,
        receivables_list,
        payables_list
    ):
        """
        Resumo do período
        
        Returns:
            Dict com total_income, total_expense, balance
        """
        total_income = Decimal(0)
        total_expense = Decimal(0)
        
        # Contas a receber pagas no período
        for receivable in receivables_list:
            if receivable.payment_date and start_date <= receivable.payment_date <= end_date:
                total_income += receivable.paid_amount
        
        # Contas a pagar pagas no período
        for payable in payables_list:
            if payable.payment_date and start_date <= payable.payment_date <= end_date:
                total_expense += payable.paid_amount
        
        balance = total_income - total_expense
        
        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "balance": round(balance, 2)
        }
    
    def get_projected_balance(
        self,
        current_balance: Decimal,
        future_receivables: Decimal,
        future_payables: Decimal
    ) -> Decimal:
        """Calcula saldo projetado"""
        projected = current_balance + future_receivables - future_payables
        return round(projected, 2)


# Singleton
financial_service = FinancialService()
