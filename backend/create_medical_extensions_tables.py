"""
Script para criar tabelas de extensões do prontuário
"""
from app.core.database import engine, Base
from app.models.medical_record_template import MedicalRecordTemplate, ExamResult, PhotoEvolution

print("🚀 Criando tabelas de extensões do prontuário...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Extensões do Prontuário:")
    print("  - medical_record_templates")
    print("  - exam_results")
    print("  - photo_evolutions")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
