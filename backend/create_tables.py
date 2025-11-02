#!/usr/bin/env python3
"""
Criar tabelas do banco de dados - Fase 2
"""
import sys
import os

# Adicionar o diretório ao path
sys.path.insert(0, '/home/administrador/sanaris-pro/sanaris/backend')

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

from app.core.database import Base, engine
from app.models import Patient, Appointment

print("🗄️  Criando tabelas no banco de dados...")
print()

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print()
    print("Tabelas criadas:")
    print("  - patients")
    print("  - appointments")
    print()
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ Banco de dados pronto!")
print()
print("Reinicie o backend para carregar as novas rotas:")
print("  Ctrl+C no terminal do backend")
print("  source venv/bin/activate")
print("  uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload")
