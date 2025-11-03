# 🚀 FASE 2 - GUIA DE INSTALAÇÃO

## 📦 O QUE SERÁ CRIADO

### Módulos:
1. ✅ **Pacientes** - CRUD completo
2. ✅ **Agendamentos** - Sistema de agenda
3. ⏳ **Prontuários** - (próxima etapa)
4. ⏳ **Prescrições** - (próxima etapa)

### Endpoints da API:
- `POST /api/v1/patients` - Criar paciente
- `GET /api/v1/patients` - Listar pacientes
- `GET /api/v1/patients/{id}` - Buscar paciente
- `POST /api/v1/appointments` - Criar agendamento
- `GET /api/v1/appointments` - Listar agendamentos
- `GET /api/v1/appointments/{id}` - Buscar agendamento

---

## ⚡ INSTALAÇÃO RÁPIDA (3 Comandos)

### 1️⃣ Instalar o código:
```bash
cd ~
chmod +x fase2_completo.sh
./fase2_completo.sh
```

### 2️⃣ Criar tabelas no banco:
```bash
cd /home/administrador/sanaris-pro/sanaris/backend
python3 create_tables.py
```

### 3️⃣ Reiniciar o backend:
```bash
# Pare o backend atual (Ctrl+C)
# Depois reinicie:
cd /home/administrador/sanaris-pro/sanaris/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

---

## 🧪 TESTAR OS ENDPOINTS

Acesse: http://localhost:8888/docs

### Criar um paciente:
```json
POST /api/v1/patients
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "full_name": "João da Silva",
  "cpf": "123.456.789-00",
  "phone": "(21) 98765-4321",
  "email": "joao@email.com",
  "birth_date": "1990-01-15"
}
```

### Criar um agendamento:
```json
POST /api/v1/appointments
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "patient_id": "ID_DO_PACIENTE_CRIADO",
  "professional_id": "00000000-0000-0000-0000-000000000002",
  "appointment_date": "2025-11-05T10:00:00",
  "duration_minutes": 30,
  "appointment_type": "consulta"
}
```

### Listar pacientes:
```
GET /api/v1/patients
```

### Listar agendamentos:
```
GET /api/v1/appointments
```

---

## 📊 ESTRUTURA CRIADA

```
backend/app/
├── core/
│   └── database.py          # Configuração do banco
├── models/
│   ├── __init__.py
│   ├── patient.py           # Modelo de Paciente
│   └── appointment.py       # Modelo de Agendamento
├── schemas/
│   ├── patient.py           # Validação de Paciente
│   └── appointment.py       # Validação de Agendamento
└── api/endpoints/
    ├── patients.py          # Rotas de Pacientes
    └── appointments.py      # Rotas de Agendamentos
```

---

## 🗄️ TABELAS NO BANCO

### `patients`
- id, tenant_id, full_name, cpf, birth_date
- phone, email, is_active
- created_at, updated_at

### `appointments`
- id, tenant_id, patient_id, professional_id
- appointment_date, duration_minutes
- status, appointment_type
- created_at

---

## ✅ VERIFICAR SE FUNCIONOU

1. Backend iniciou sem erros?
2. Acessa http://localhost:8888/docs ?
3. Vê os novos endpoints de patients e appointments?
4. Consegue criar um paciente?
5. Consegue criar um agendamento?

---

## 🆘 PROBLEMAS COMUNS

### Erro: "No module named 'app.models'"
```bash
# Verificar se os arquivos foram criados:
ls -la /home/administrador/sanaris-pro/sanaris/backend/app/models/
```

### Erro: "Table already exists"
```bash
# Tabelas já existem, tudo OK!
# Apenas reinicie o backend
```

### Erro ao conectar no banco:
```bash
# Verificar se PostgreSQL está rodando:
sudo systemctl status postgresql

# Verificar credenciais no .env:
cat /home/administrador/sanaris-pro/sanaris/backend/.env | grep DATABASE_URL
```

---

## 📝 PRÓXIMOS PASSOS - FASE 2.1

Depois de testar, vamos adicionar:
- 📋 **Prontuários Médicos** - Histórico completo
- 💊 **Prescrições Digitais** - Receitas e medicamentos
- 📎 **Upload de Arquivos** - Anexos e documentos
- 🔍 **Busca Avançada** - Filtros e pesquisa

---

## 🎯 RESUMO

### Arquivos para baixar:
1. **fase2_completo.sh** ⭐ - Instala todo o código
2. **create_tables.py** ⭐ - Cria tabelas no banco

### Comandos para executar:
```bash
# 1. Instalar código
chmod +x fase2_completo.sh
./fase2_completo.sh

# 2. Criar tabelas
cd /home/administrador/sanaris-pro/sanaris/backend
python3 create_tables.py

# 3. Reiniciar backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

### Testar:
- http://localhost:8888/docs
- Criar paciente
- Criar agendamento
- Listar tudo

---

**Boa implementação! 🚀**
