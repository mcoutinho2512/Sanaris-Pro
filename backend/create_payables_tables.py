"""
Script para criar tabelas de contas a pagar
"""
from app.core.database import engine, Base
from app.models.financial import Supplier, ExpenseCategory, CostCenter, AccountPayable, PayableTransaction

print("🚀 Criando tabelas de contas a pagar...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Contas a Pagar:")
    print("  - suppliers")
    print("  - expense_categories")
    print("  - cost_centers")
    print("  - accounts_payable")
    print("  - payable_transactions")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
