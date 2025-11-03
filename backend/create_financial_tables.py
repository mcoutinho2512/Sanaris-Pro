"""
Script para criar tabelas financeiras
"""
from app.core.database import engine, Base
from app.models.financial import AccountReceivable, PaymentInstallment, PaymentTransaction

print("🚀 Criando tabelas financeiras...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas Financeiras:")
    print("  - accounts_receivable")
    print("  - payment_installments")
    print("  - payment_transactions")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
