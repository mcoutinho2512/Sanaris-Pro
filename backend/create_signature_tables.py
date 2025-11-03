"""
Script para criar tabelas de assinatura digital
"""
from app.core.database import engine, Base
from app.models.digital_signature import DigitalCertificate, OTPConfiguration, SignatureLog

print("🚀 Criando tabelas de assinatura digital...")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print("\nTabelas de Assinatura Digital:")
    print("  - digital_certificates")
    print("  - otp_configurations")
    print("  - signature_logs")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
