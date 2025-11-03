"""
Script para criar tabelas de Prescrição Digital
"""
from app.core.database import engine, Base
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionTemplate
from app.models.patient import Patient

print("🚀 Criando tabelas de Prescrição Digital...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Prescrição Digital:")
    print("  - prescriptions")
    print("  - prescription_items")
    print("  - prescription_templates")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
