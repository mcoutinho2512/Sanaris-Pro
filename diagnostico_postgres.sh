#!/bin/bash

echo "🔍 DIAGNÓSTICO POSTGRESQL - SANARIS PRO"
echo "========================================"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. Verificando se PostgreSQL está rodando..."
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓${NC} PostgreSQL está rodando"
else
    echo -e "${RED}✗${NC} PostgreSQL NÃO está rodando"
    echo "   Execute: sudo systemctl start postgresql"
fi
echo ""

echo "2. Verificando versão do PostgreSQL..."
psql --version
echo ""

echo "3. Verificando se consegue conectar como postgres..."
if sudo -u postgres psql -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Conexão OK"
    sudo -u postgres psql -c "SELECT version();" | head -n 3
else
    echo -e "${RED}✗${NC} Não conseguiu conectar"
fi
echo ""

echo "4. Verificando bancos existentes..."
sudo -u postgres psql -l 2>/dev/null | grep -E "Name|sanaris"
echo ""

echo "5. Verificando usuários existentes..."
sudo -u postgres psql -c "\du" 2>/dev/null | grep -E "Role name|sanaris"
echo ""

echo "6. Testando criação de banco (teste)..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS teste_sanaris;
DROP USER IF EXISTS teste_user;
CREATE USER teste_user WITH PASSWORD 'teste123';
CREATE DATABASE teste_sanaris OWNER teste_user;
DROP DATABASE teste_sanaris;
DROP USER teste_user;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Consegue criar banco e usuário!"
else
    echo -e "${RED}✗${NC} Erro ao criar banco/usuário"
fi
echo ""

echo "7. Verificando logs do PostgreSQL..."
sudo tail -n 20 /var/log/postgresql/postgresql-*.log 2>/dev/null || echo "Logs não encontrados"
echo ""

echo "========================================"
echo "Diagnóstico concluído!"
