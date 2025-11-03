"""
Script para criar tabelas de Prontuário Eletrônico
"""
from app.core.database import engine, Base
from app.models.medical_record import MedicalRecord, VitalSigns, MedicalRecordAttachment
from app.models.patient import Patient

print("🚀 Criando tabelas de Prontuário Eletrônico...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas do Prontuário Eletrônico:")
    print("  - medical_records")
    print("  - vital_signs")
    print("  - medical_record_attachments")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
