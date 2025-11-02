#!/bin/bash

##############################################
# SANARIS PRO - Configuração Manual PostgreSQL
# Use este script se a instalação parou no PostgreSQL
##############################################

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

echo "╔════════════════════════════════════════════════════════╗"
echo "║     SANARIS PRO - Configuração Manual PostgreSQL      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Verificar se PostgreSQL está rodando
if ! systemctl is-active --quiet postgresql; then
    log_error "PostgreSQL não está rodando!"
    echo "Execute: sudo systemctl start postgresql"
    exit 1
fi

log_success "PostgreSQL está rodando"
echo ""

# Variáveis
DB_NAME="sanaris_pro"
DB_USER="sanaris_admin"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

log_info "Configurando banco de dados..."
echo ""
echo "   Banco: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Senha: $DB_PASSWORD"
echo ""

# Perguntar se quer continuar
read -p "Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    log_error "Cancelado pelo usuário"
    exit 1
fi

# Método 1: Criar usando SQL direto
log_info "Criando usuário e banco de dados..."

# Criar script SQL temporário
cat > /tmp/sanaris_setup.sql << EOF
-- Remover se já existir
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Criar usuário
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Criar banco
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Executar script
if sudo -u postgres psql -f /tmp/sanaris_setup.sql > /dev/null 2>&1; then
    log_success "Banco e usuário criados!"
else
    log_error "Erro ao criar banco/usuário"
    echo ""
    echo "Tentando método alternativo..."
    
    # Método 2: Comando por comando
    sudo -u postgres createuser --no-createdb --no-superuser --no-createrole $DB_USER 2>/dev/null
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
    sudo -u postgres createdb --owner=$DB_USER $DB_NAME 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Banco criado pelo método alternativo!"
    else
        log_error "Não foi possível criar o banco"
        rm /tmp/sanaris_setup.sql
        exit 1
    fi
fi

# Criar extensões
log_info "Criando extensões no banco..."

cat > /tmp/sanaris_extensions.sql << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF

if sudo -u postgres psql -d $DB_NAME -f /tmp/sanaris_extensions.sql > /dev/null 2>&1; then
    log_success "Extensões criadas!"
else
    log_error "Erro ao criar extensões (mas o banco está OK)"
fi

# Limpar arquivos temporários
rm /tmp/sanaris_setup.sql 2>/dev/null
rm /tmp/sanaris_extensions.sql 2>/dev/null

# Testar conexão
log_info "Testando conexão..."
if PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    log_success "Conexão testada com sucesso!"
else
    log_error "Não foi possível conectar ao banco"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              CONFIGURAÇÃO CONCLUÍDA!                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log_info "SALVE ESTAS CREDENCIAIS:"
echo ""
echo "   DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "   Banco: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Senha: $DB_PASSWORD"
echo ""

# Salvar credenciais em arquivo
CREDS_FILE="$HOME/sanaris_db_credentials.txt"
cat > "$CREDS_FILE" << EOF
SANARIS PRO - Credenciais do Banco de Dados
Gerado em: $(date)

Banco: $DB_NAME
Usuário: $DB_USER
Senha: $DB_PASSWORD

DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

⚠️ GUARDE ESTE ARQUIVO EM LOCAL SEGURO!
EOF

log_success "Credenciais salvas em: $CREDS_FILE"
echo ""

log_info "Próximo passo: Atualizar o arquivo .env"
echo ""
echo "Execute:"
echo "  nano /home/administrador/sanaris-pro/sanaris/.env"
echo ""
echo "E atualize a linha DATABASE_URL com:"
echo "  DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

log_success "Pronto! PostgreSQL configurado!"
