# ⚡ SOLUÇÃO RÁPIDA - 3 COMANDOS

## 📍 Você está aqui:
```
Instalação parou no PostgreSQL (passo 3/10)
```

## ✅ FAÇA ISSO AGORA (copie e cole):

### 1️⃣ Configure o PostgreSQL:
```bash
cd ~/sanaris-pro
chmod +x configurar_postgres.sh
./configurar_postgres.sh
```

**O que vai acontecer:**
- Cria o banco `sanaris_pro`
- Cria o usuário `sanaris_admin`
- Gera senha automática
- Salva credenciais em arquivo

**Quando terminar:** Copie a senha que aparecer!

---

### 2️⃣ Continue a instalação:
```bash
cd ~/sanaris-pro
chmod +x continuar_instalacao.sh
./continuar_instalacao.sh
```

**O que vai acontecer:**
- Verifica se PostgreSQL está OK
- Cria arquivo .env
- Instala dependências Python (~5 min)
- Instala dependências Node.js (~5 min)
- Cria scripts de gerenciamento
- Configura Git

**Aguarde:** ~10 minutos no total

---

### 3️⃣ Inicie o sistema:
```bash
cd /home/administrador/sanaris-pro/sanaris
./scripts/start_all.sh
```

**Acesse:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

---

## 🎯 Resumo dos Arquivos

Baixe estes 2 scripts para `~/sanaris-pro/`:

1. **configurar_postgres.sh** ⭐ - Configura o banco
2. **continuar_instalacao.sh** ⭐ - Termina a instalação

---

## 📞 Me avise quando:

✅ Terminar o passo 1 (PostgreSQL)  
✅ Terminar o passo 2 (instalação)  
✅ O sistema iniciar

---

**É só isso! 3 comandos e está pronto! 🚀**
