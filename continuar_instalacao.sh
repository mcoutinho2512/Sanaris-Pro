#!/bin/bash

##############################################
# SANARIS PRO - Continuar Instalação
# Continue de onde o script parou
##############################################

set -e

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

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║     SANARIS PRO - Continuar Instalação                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Detectar diretório de instalação
INSTALL_DIR="/home/administrador/sanaris-pro/sanaris"

if [ ! -d "$INSTALL_DIR" ]; then
    log_error "Diretório $INSTALL_DIR não encontrado!"
    echo ""
    echo "Possíveis localizações:"
    find ~ -type d -name "sanaris" 2>/dev/null | head -5
    echo ""
    read -p "Digite o caminho completo do diretório: " INSTALL_DIR
    
    if [ ! -d "$INSTALL_DIR" ]; then
        log_error "Diretório não existe!"
        exit 1
    fi
fi

log_info "Usando diretório: $INSTALL_DIR"
cd "$INSTALL_DIR"
echo ""

# ============================================
# 1. VERIFICAR SE POSTGRES ESTÁ OK
# ============================================
log_info "1/6 - Verificando PostgreSQL..."

if ! sudo -u postgres psql -c "\l" > /dev/null 2>&1; then
    log_error "PostgreSQL não está acessível"
    echo "Execute primeiro: ./configurar_postgres.sh"
    exit 1
fi

if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw sanaris_pro; then
    log_success "Banco 'sanaris_pro' existe!"
else
    log_error "Banco 'sanaris_pro' não encontrado"
    echo "Execute primeiro: ./configurar_postgres.sh"
    exit 1
fi

# ============================================
# 2. VERIFICAR/CRIAR ARQUIVO .ENV
# ============================================
log_info "2/6 - Verificando arquivo .env..."

if [ ! -f ".env" ]; then
    log_error "Arquivo .env não encontrado. Criando..."
    
    # Pegar credenciais do arquivo salvo
    if [ -f "$HOME/sanaris_db_credentials.txt" ]; then
        DB_URL=$(grep "DATABASE_URL=" "$HOME/sanaris_db_credentials.txt" | cut -d= -f2-)
    else
        log_error "Credenciais não encontradas!"
        echo "Execute primeiro: ./configurar_postgres.sh"
        exit 1
    fi
    
    # Gerar secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Criar .env
    cat > .env << EOF
# SANARIS PRO - Configurações
ENVIRONMENT=development
DEBUG=true
APP_NAME=Sanaris Pro
APP_VERSION=1.0.0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL=$DB_URL
DATABASE_ECHO=false
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Segurança
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=true

# Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=$INSTALL_DIR/uploads

# Logs
LOG_LEVEL=INFO
LOG_FILE=$INSTALL_DIR/logs/backend/sanaris.log
EOF
    
    cp .env backend/.env
    log_success "Arquivo .env criado!"
else
    log_success "Arquivo .env já existe"
fi

# ============================================
# 3. INSTALAR DEPENDÊNCIAS PYTHON
# ============================================
log_info "3/6 - Instalando dependências Python..."

if [ ! -f "backend/requirements.txt" ]; then
    log_error "backend/requirements.txt não encontrado!"
    exit 1
fi

cd backend

# Detectar Python
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    PYTHON_CMD="python3"
fi

log_info "Usando: $PYTHON_CMD"

# Criar venv
if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual..."
    $PYTHON_CMD -m venv venv
fi

log_info "Instalando pacotes Python (pode demorar alguns minutos)..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

log_success "Dependências Python instaladas!"
cd ..

# ============================================
# 4. INSTALAR DEPENDÊNCIAS NODE
# ============================================
log_info "4/6 - Instalando dependências Node.js..."

if [ ! -f "frontend/package.json" ]; then
    log_error "frontend/package.json não encontrado!"
    exit 1
fi

cd frontend

if [ ! -d "node_modules" ]; then
    log_info "Instalando pacotes Node.js (pode demorar alguns minutos)..."
    npm install --legacy-peer-deps -q
    log_success "Dependências Node.js instaladas!"
else
    log_success "node_modules já existe"
fi

cd ..

# ============================================
# 5. CRIAR SCRIPTS DE GERENCIAMENTO
# ============================================
log_info "5/6 - Criando scripts de gerenciamento..."

mkdir -p scripts

# Start backend
cat > scripts/start_backend.sh << EOF
#!/bin/bash
cd "$INSTALL_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Start frontend
cat > scripts/start_frontend.sh << EOF
#!/bin/bash
cd "$INSTALL_DIR/frontend"
npm run dev
EOF

# Start all
cat > scripts/start_all.sh << EOF
#!/bin/bash
echo "🚀 Iniciando Sanaris Pro..."
echo ""

# Backend em background
echo "📡 Iniciando backend..."
$INSTALL_DIR/scripts/start_backend.sh > $INSTALL_DIR/logs/backend/uvicorn.log 2>&1 &
BACKEND_PID=\$!

# Aguardar
sleep 5

# Frontend
echo "🎨 Iniciando frontend..."
$INSTALL_DIR/scripts/start_frontend.sh

# Cleanup
trap "kill \$BACKEND_PID" EXIT
EOF

chmod +x scripts/*.sh

log_success "Scripts criados!"

# ============================================
# 6. CONFIGURAR GIT
# ============================================
log_info "6/6 - Configurando Git..."

if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/mcoutinho2512/Sanaris-Pro.git
    log_success "Git inicializado!"
else
    log_success "Git já configurado"
fi

# ============================================
# FINALIZAÇÃO
# ============================================
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              INSTALAÇÃO CONCLUÍDA! ✅                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log_success "Sanaris Pro instalado em: $INSTALL_DIR"
echo ""

log_info "🚀 PARA INICIAR O SISTEMA:"
echo ""
echo "   cd $INSTALL_DIR"
echo "   ./scripts/start_all.sh"
echo ""

log_info "🌐 ACESSAR:"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Docs API: http://localhost:8000/docs"
echo ""

log_info "📝 PRÓXIMO PASSO:"
echo ""
echo "   Siga o arquivo CHECKLIST.md para configurar o sistema"
echo ""

log_success "Instalação finalizada com sucesso! 🎉"
