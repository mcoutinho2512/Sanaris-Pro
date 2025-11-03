"""
Script para criar tabelas de Documentos
"""
from app.core.database import engine, Base
from app.models.document import DocumentTemplate, PatientDocument, QuickPatientRegistration
from app.models.patient import Patient

print("🚀 Criando tabelas de Documentos e Pré-cadastro...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Documentos:")
    print("  - document_templates")
    print("  - patient_documents")
    print("  - quick_patient_registrations")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
