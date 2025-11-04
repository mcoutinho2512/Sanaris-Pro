"""
Script para criar tabelas TISS
"""
from app.core.database import engine, Base
from app.models.tiss import (
    HealthInsuranceOperator, TussProcedure, Beneficiary,
    TissGuide, TissGuideProcedure, TissBatch
)

print("🚀 Criando tabelas TISS...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas TISS:")
    print("  - health_insurance_operators")
    print("  - tuss_procedures")
    print("  - beneficiaries")
    print("  - tiss_guides")
    print("  - tiss_guide_procedures")
    print("  - tiss_batches")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
