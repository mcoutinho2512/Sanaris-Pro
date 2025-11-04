"""
Script para criar tabelas de repasse profissionais
"""
from app.core.database import engine, Base
from app.models.financial import ProfessionalFeeConfiguration, ProfessionalFee, ProfessionalFeeItem

print("🚀 Criando tabelas de repasse profissionais...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Repasse:")
    print("  - professional_fee_configurations")
    print("  - professional_fees")
    print("  - professional_fee_items")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
