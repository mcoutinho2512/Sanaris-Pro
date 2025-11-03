# 🔧 GUIA DE RECUPERAÇÃO - Instalação Parou no PostgreSQL

## 📍 Situação Atual

A instalação parou em:
```
[INFO] 3/10 - Configurando banco de dados PostgreSQL...
```

O script criou a estrutura de diretórios mas não conseguiu configurar o PostgreSQL.

---

## 🎯 SOLUÇÃO RÁPIDA (3 Passos)

### 1️⃣ Baixe e Execute o Diagnóstico

**Baixe:** [diagnostico_postgres.sh](computer:///mnt/user-data/outputs/diagnostico_postgres.sh)

```bash
cd ~/sanaris-pro
chmod +x diagnostico_postgres.sh
./diagnostico_postgres.sh
```

**Isso vai mostrar:** O que está errado com o PostgreSQL

---

### 2️⃣ Configure o PostgreSQL Manualmente

**Baixe:** [configurar_postgres.sh](computer:///mnt/user-data/outputs/configurar_postgres.sh)

```bash
cd ~/sanaris-pro
chmod +x configurar_postgres.sh
./configurar_postgres.sh
```

**Isso vai:**
- ✅ Criar o banco `sanaris_pro`
- ✅ Criar o usuário `sanaris_admin`
- ✅ Gerar senha segura
- ✅ Configurar extensões
- ✅ Salvar credenciais em arquivo

---

### 3️⃣ Atualizar o .env e Continuar

```bash
# Editar o arquivo .env
nano /home/administrador/sanaris-pro/sanaris/.env
```

**Localize a linha:**
```
DATABASE_URL=postgresql+asyncpg://...
```

**Substitua pela URL que o script mostrou** (algo como):
```
DATABASE_URL=postgresql+asyncpg://sanaris_admin:SENHA_GERADA@localhost:5432/sanaris_pro
```

**Salve:** `Ctrl+O` → Enter → `Ctrl+X`

---

## 🚀 Continuar a Instalação

Depois de configurar o PostgreSQL, você tem duas opções:

### Opção A: Instalar Dependências Manualmente

```bash
cd /home/administrador/sanaris-pro/sanaris

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Frontend
cd ../frontend
npm install --legacy-peer-deps

# Scripts
cd ../scripts
chmod +x *.sh

# Git
cd ..
git add .
git commit -m "Initial commit - Sanaris Pro"
```

### Opção B: Executar Script Simplificado (VOU CRIAR)

Vou criar um script que continua de onde parou!

---

## 📊 Status da Instalação

Até agora, o que FOI criado:

✅ **Estrutura de diretórios:**
- `/home/administrador/sanaris-pro/sanaris/backend/`
- `/home/administrador/sanaris-pro/sanaris/frontend/`
- `/home/administrador/sanaris-pro/sanaris/docs/`
- `/home/administrador/sanaris-pro/sanaris/scripts/`
- `/home/administrador/sanaris-pro/sanaris/logs/`

✅ **Arquivos de configuração:**
- `backend/requirements.txt`
- `frontend/package.json`
- `.gitignore`
- `README.md`

❌ **O que NÃO foi feito ainda:**
- Banco de dados PostgreSQL
- Arquivo `.env` (pode estar vazio ou incompleto)
- Instalação de dependências Python
- Instalação de dependências Node.js
- Scripts de gerenciamento

---

## 🆘 Se Nada Funcionar

**Opção última:** Começar do zero

```bash
# Remover tudo
rm -rf /home/administrador/sanaris-pro

# Executar o script de instalação novamente
cd ~
mkdir sanaris-pro
cd sanaris-pro
# Baixar sanaris_install_FIXED.sh
chmod +x sanaris_install_FIXED.sh
./sanaris_install_FIXED.sh

# Quando perguntar o diretório, use:
/opt/sanaris-pro
```

---

## 📞 Próximos Passos

**Agora faça:**

1. ✅ Execute o diagnóstico: `./diagnostico_postgres.sh`
2. ✅ Me envie o resultado (copie e cole aqui)
3. ✅ Execute a configuração: `./configurar_postgres.sh`
4. ✅ Me avise quando terminar

Aí eu te ajudo a continuar a instalação! 🚀

---

## 💡 Por que isso aconteceu?

Possíveis causas:
- PostgreSQL pode ter permissões diferentes no seu sistema
- Pode ter usuário/banco com o mesmo nome já existente
- Configuração de `pg_hba.conf` pode estar restritiva
- O script não teve permissão para executar comandos como `postgres`

**A solução manual vai contornar todos esses problemas!** ✅
