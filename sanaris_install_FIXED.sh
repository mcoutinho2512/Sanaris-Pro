#!/bin/bash

##############################################
# SANARIS PRO - Script de Instalação
# Sistema de Gestão de Clínicas e Consultórios
# Versão: 1.0.1 (CORRIGIDO)
##############################################

set -e  # Para na primeira falha

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Banner
clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗ █████╗ ███╗   ██╗ █████╗ ██████╗ ██╗███████╗ ║
║   ██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██║██╔════╝ ║
║   ███████╗███████║██╔██╗ ██║███████║██████╔╝██║███████╗ ║
║   ╚════██║██╔══██║██║╚██╗██║██╔══██║██╔══██╗██║╚════██║ ║
║   ███████║██║  ██║██║ ╚████║██║  ██║██║  ██║██║███████║ ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ║
║                                                           ║
║              PRO - Sistema de Gestão Médica               ║
║                    Instalação v1.0.1                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo ""
log_info "Iniciando instalação do Sanaris Pro..."
echo ""

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    log_warning "Este script precisa de privilégios sudo para instalar dependências do sistema."
    log_info "Você será solicitado a inserir sua senha quando necessário."
fi

# Diretório de instalação
read -p "Digite o diretório de instalação [/opt/sanaris-pro]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/opt/sanaris-pro}

# Se o usuário digitou um caminho relativo, converter para absoluto
if [[ "$INSTALL_DIR" != /* ]]; then
    INSTALL_DIR="$(pwd)/$INSTALL_DIR"
fi

# Confirmar
echo ""
log_info "Diretório de instalação: $INSTALL_DIR"
read -p "Confirma? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    log_error "Instalação cancelada."
    exit 1
fi

# ============================================
# 1. VERIFICAR DEPENDÊNCIAS DO SISTEMA
# ============================================
echo ""
log_info "1/10 - Verificando dependências do sistema..."

check_command() {
    if command -v $1 &> /dev/null; then
        log_success "$1 está instalado"
        return 0
    else
        log_warning "$1 NÃO está instalado"
        return 1
    fi
}

# Lista de dependências obrigatórias
MISSING_DEPS=()

if ! check_command "python3.11" && ! check_command "python3.10" && ! check_command "python3"; then
    MISSING_DEPS+=("python3")
fi

if ! check_command "node"; then
    MISSING_DEPS+=("nodejs")
fi

if ! check_command "npm"; then
    MISSING_DEPS+=("npm")
fi

if ! check_command "psql"; then
    MISSING_DEPS+=("postgresql")
fi

if ! check_command "redis-cli"; then
    MISSING_DEPS+=("redis-server")
fi

if ! check_command "git"; then
    MISSING_DEPS+=("git")
fi

# Instalar dependências faltantes
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    log_warning "Instalando dependências faltantes: ${MISSING_DEPS[*]}"
    
    sudo apt update
    
    for dep in "${MISSING_DEPS[@]}"; do
        case $dep in
            python3)
                sudo apt install -y python3 python3-venv python3-dev python3-pip
                ;;
            nodejs)
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                sudo apt install -y nodejs
                ;;
            npm)
                sudo apt install -y npm
                ;;
            postgresql)
                sudo apt install -y postgresql postgresql-contrib
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
                ;;
            redis-server)
                sudo apt install -y redis-server
                sudo systemctl start redis-server
                sudo systemctl enable redis-server
                ;;
            git)
                sudo apt install -y git
                ;;
        esac
    done
    
    log_success "Dependências instaladas!"
fi

# ============================================
# 2. CRIAR ESTRUTURA DO PROJETO
# ============================================
echo ""
log_info "2/10 - Criando estrutura do projeto..."

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Estrutura de diretórios
mkdir -p backend/{app/{api/{endpoints,deps},core,models,schemas,services,utils},tests,alembic/versions}
mkdir -p frontend/{src/{app,components,contexts,hooks,lib,services,styles},public}
mkdir -p mobile
mkdir -p totem
mkdir -p docs/{api,user,admin}
mkdir -p scripts/{backup,deploy,maintenance}
mkdir -p docker
mkdir -p logs/{backend,frontend}
mkdir -p uploads/{documents,images,temp}

log_success "Estrutura de diretórios criada!"

# ============================================
# 3. CONFIGURAR BANCO DE DADOS
# ============================================
echo ""
log_info "3/10 - Configurando banco de dados PostgreSQL..."

# Variáveis do banco
DB_NAME="sanaris_pro"
DB_USER="sanaris_admin"
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Criar usuário e banco
sudo -u postgres psql > /dev/null 2>&1 << EOF
-- Criar usuário
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Criar banco
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Conectar ao banco e criar extensões
sudo -u postgres psql -d $DB_NAME > /dev/null 2>&1 << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF

log_success "Banco de dados configurado!"
log_info "Usuário: $DB_USER"
log_info "Banco: $DB_NAME"

# ============================================
# 4. GERAR ARQUIVO .ENV
# ============================================
echo ""
log_info "4/10 - Gerando arquivos de configuração..."

# Gerar secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

cat > "$INSTALL_DIR/.env" << EOF
# SANARIS PRO - Configurações
# Gerado automaticamente em $(date)

# Ambiente
ENVIRONMENT=development
DEBUG=true
APP_NAME=Sanaris Pro
APP_VERSION=1.0.0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
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

# Email (configurar depois)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@sanarispro.com.br

# WhatsApp (configurar depois)
WHATSAPP_API_URL=
WHATSAPP_API_TOKEN=

# Pagamento (configurar depois)
PAYMENT_GATEWAY=
PAYMENT_API_KEY=

# TISS
TISS_VERSION=4.00.00
TISS_PADRAO=1

# NFS-e (configurar depois)
NFSE_AMBIENTE=homologacao
NFSE_MUNICIPIO=

# Logs
LOG_LEVEL=INFO
LOG_FILE=$INSTALL_DIR/logs/backend/sanaris.log

EOF

log_success "Arquivo .env criado!"

# Copiar para backend
cp "$INSTALL_DIR/.env" "$INSTALL_DIR/backend/.env"

# ============================================
# 5. INICIALIZAR GIT E GITHUB
# ============================================
echo ""
log_info "5/10 - Configurando Git e GitHub..."

cd "$INSTALL_DIR"

# Inicializar repositório
git init

# Criar .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Node
node_modules/
.next/
out/
build/
.DS_Store
*.pem
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Env
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Uploads
uploads/*
!uploads/.gitkeep

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

EOF

# Criar README
cat > README.md << 'EOF'
# 🏥 Sanaris Pro

Sistema completo de gestão para clínicas e consultórios médicos.

## 📋 Módulos

- ✅ Agenda Inteligente
- ✅ Prontuário Eletrônico
- ✅ Prescrição Digital
- ✅ Gestão Financeira
- ✅ Faturamento TISS
- ✅ Pagamento Online
- ✅ Emissão de NFS-e
- ✅ Agendamento Online
- ✅ Pesquisa de Satisfação
- ✅ E-mail Marketing
- ✅ Gestão de Estoque
- ✅ Totem de Autoatendimento
- ✅ App White Label
- ✅ Gestão Clínica

## 🚀 Tecnologias

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React + Next.js 14 + Tailwind CSS
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Mobile**: React Native

## 📦 Instalação

Consulte a documentação em `/docs/INSTALL.md`

## 📝 Licença

Todos os direitos reservados © 2025 Sanaris Pro

EOF

# Adicionar remote do GitHub
git remote add origin https://github.com/mcoutinho2512/Sanaris-Pro.git

log_success "Git configurado!"

# ============================================
# 6. CRIAR BACKEND - ESTRUTURA BASE
# ============================================
echo ""
log_info "6/10 - Criando estrutura do backend..."

cat > "$INSTALL_DIR/backend/requirements.txt" << 'EOF'
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
PyJWT==2.8.0

# Redis
redis==5.0.1
hiredis==2.3.2

# HTTP
httpx==0.26.0
aiohttp==3.9.1

# Utils
python-dotenv==1.0.0
email-validator==2.1.0
phonenumbers==8.13.27
python-dateutil==2.8.2
pytz==2023.3

# Excel/PDF
openpyxl==3.1.2
reportlab==4.0.8
PyPDF2==3.0.1

# Validação BR
validate-docbr==1.10.0

# Tasks
celery==5.3.4

# Monitoring
prometheus-fastapi-instrumentator==6.1.0

EOF

cat > "$INSTALL_DIR/backend/pyproject.toml" << 'EOF'
[tool.poetry]
name = "sanaris-pro-backend"
version = "1.0.0"
description = "Sistema de Gestão de Clínicas e Consultórios"
authors = ["Sanaris Team <dev@sanarispro.com.br>"]

[tool.poetry.dependencies]
python = "^3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

EOF

log_success "Arquivos base do backend criados!"

# ============================================
# 7. CRIAR FRONTEND - ESTRUTURA BASE
# ============================================
echo ""
log_info "7/10 - Criando estrutura do frontend..."

cat > "$INSTALL_DIR/frontend/package.json" << 'EOF'
{
  "name": "sanaris-pro-frontend",
  "version": "1.0.0",
  "description": "Sanaris Pro - Sistema de Gestão de Clínicas",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.5",
    "date-fns": "^3.2.0",
    "zustand": "^4.5.0",
    "react-hook-form": "^7.49.3",
    "zod": "^3.22.4",
    "@hookform/resolvers": "^3.3.4",
    "lucide-react": "^0.312.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "@types/node": "^20.11.5",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.1.0"
  }
}
EOF

log_success "Arquivos base do frontend criados!"

# ============================================
# 8. INSTALAR DEPENDÊNCIAS
# ============================================
echo ""
log_info "8/10 - Instalando dependências (pode demorar alguns minutos)..."

# Detectar versão do Python
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    PYTHON_CMD="python3"
fi

# Backend
cd "$INSTALL_DIR/backend"
log_info "Criando ambiente virtual Python com $PYTHON_CMD..."
$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
deactivate
log_success "Dependências do backend instaladas!"

# Frontend
cd "$INSTALL_DIR/frontend"
log_info "Instalando pacotes Node.js..."
npm install --legacy-peer-deps > /dev/null 2>&1
log_success "Dependências do frontend instaladas!"

# ============================================
# 9. CRIAR SCRIPTS DE GERENCIAMENTO
# ============================================
echo ""
log_info "9/10 - Criando scripts de gerenciamento..."

# Script para iniciar backend
cat > "$INSTALL_DIR/scripts/start_backend.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

chmod +x "$INSTALL_DIR/scripts/start_backend.sh"

# Script para iniciar frontend
cat > "$INSTALL_DIR/scripts/start_frontend.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR/frontend"
npm run dev
EOF

chmod +x "$INSTALL_DIR/scripts/start_frontend.sh"

# Script para iniciar ambos
cat > "$INSTALL_DIR/scripts/start_all.sh" << EOF
#!/bin/bash
SCRIPT_DIR="\$(dirname "\$0")"

echo "🚀 Iniciando Sanaris Pro..."
echo ""

# Iniciar backend em background
echo "📡 Iniciando backend..."
\$SCRIPT_DIR/start_backend.sh > $INSTALL_DIR/logs/backend/uvicorn.log 2>&1 &
BACKEND_PID=\$!

# Aguardar backend iniciar
sleep 5

# Iniciar frontend
echo "🎨 Iniciando frontend..."
\$SCRIPT_DIR/start_frontend.sh

# Cleanup ao sair
trap "kill \$BACKEND_PID" EXIT

EOF

chmod +x "$INSTALL_DIR/scripts/start_all.sh"

log_success "Scripts de gerenciamento criados!"

# ============================================
# 10. CRIAR DOCUMENTAÇÃO
# ============================================
echo ""
log_info "10/10 - Gerando documentação..."

cat > "$INSTALL_DIR/docs/INSTALL.md" << EOF
# 📦 Instalação do Sanaris Pro

## ✅ Instalação Concluída!

O Sanaris Pro foi instalado em: \`$INSTALL_DIR\`

### 🔐 Credenciais do Banco de Dados

- **Banco:** $DB_NAME
- **Usuário:** $DB_USER  
- **Senha:** \`$DB_PASSWORD\`

> ⚠️ **IMPORTANTE**: Salve estas credenciais em local seguro!

### 🚀 Como Iniciar

#### Opção 1: Iniciar tudo de uma vez
\`\`\`bash
cd $INSTALL_DIR
./scripts/start_all.sh
\`\`\`

#### Opção 2: Iniciar separadamente

**Backend:**
\`\`\`bash
cd $INSTALL_DIR
./scripts/start_backend.sh
\`\`\`

**Frontend:**
\`\`\`bash
cd $INSTALL_DIR
./scripts/start_frontend.sh
\`\`\`

### 🌐 Acessar o Sistema

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs

### 📝 Próximos Passos

1. Configurar variáveis de ambiente no arquivo \`.env\`
2. Executar migrations do banco de dados
3. Criar usuário administrador inicial
4. Configurar integrações (Email, WhatsApp, etc)

### 🔧 Comandos Úteis

**Ver logs:**
\`\`\`bash
tail -f $INSTALL_DIR/logs/backend/sanaris.log
tail -f $INSTALL_DIR/logs/backend/uvicorn.log
\`\`\`

**Backup do banco:**
\`\`\`bash
pg_dump $DB_NAME > backup_\$(date +%Y%m%d_%H%M%S).sql
\`\`\`

### 📚 Documentação Completa

Consulte a documentação completa em: \`$INSTALL_DIR/docs/\`

EOF

log_success "Documentação criada!"

# ============================================
# FINALIZAÇÃO
# ============================================
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║  ✅  INSTALAÇÃO CONCLUÍDA COM SUCESSO!               ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

log_success "Sanaris Pro instalado em: $INSTALL_DIR"
echo ""

log_info "📋 CREDENCIAIS DO BANCO DE DADOS:"
echo "   Banco: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Senha: $DB_PASSWORD"
echo ""

log_warning "⚠️  IMPORTANTE: Salve estas credenciais em local seguro!"
echo ""

log_info "📖 Documentação completa: $INSTALL_DIR/docs/INSTALL.md"
echo ""

log_info "🚀 PRÓXIMOS PASSOS:"
echo ""
echo "   1. Revisar configurações:"
echo "      nano $INSTALL_DIR/.env"
echo ""
echo "   2. Enviar código para o GitHub:"
echo "      cd $INSTALL_DIR"
echo "      git add ."
echo "      git commit -m 'Initial commit - Sanaris Pro v1.0.0'"
echo "      git push -u origin main"
echo ""
echo "   3. Iniciar o sistema:"
echo "      cd $INSTALL_DIR"
echo "      ./scripts/start_all.sh"
echo ""

log_success "Instalação finalizada! 🎉"
echo ""
