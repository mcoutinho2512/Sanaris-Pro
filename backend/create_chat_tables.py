import sys
import os

# Configurar path corretamente
backend_path = '/home/administrador/sanaris-pro/sanaris/backend'
sys.path.insert(0, backend_path)
os.chdir(backend_path)

# Importar do local correto
from app.core.database import engine, Base
from app.models.chat import ChatChannel, ChatMessage, ChatParticipant, ChatReadStatus

print("🔄 Criando tabelas de chat no database...")

try:
    # Criar tabelas
    Base.metadata.create_all(bind=engine, tables=[
        ChatChannel.__table__,
        ChatParticipant.__table__,
        ChatMessage.__table__,
        ChatReadStatus.__table__
    ])
    print("✅ Tabelas de chat criadas com sucesso!")
    print("   - chat_channels")
    print("   - chat_participants")
    print("   - chat_messages")
    print("   - chat_read_status")
except Exception as e:
    print(f"❌ Erro ao criar tabelas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
