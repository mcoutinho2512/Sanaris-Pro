"""
Script para criar tabelas de integração CFM
"""
from app.core.database import engine, Base
from app.models.cfm_integration import CFMCredentials, CFMPrescriptionLog

print("🚀 Criando tabelas de integração CFM...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Integração CFM:")
    print("  - cfm_credentials")
    print("  - cfm_prescription_logs")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
