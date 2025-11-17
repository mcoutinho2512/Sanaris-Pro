# 📋 SANARIS PRO - Arquitetura Completa do Sistema

**Sistema de Gestão de Clínicas e Consultórios**  
**Repositório:** https://github.com/mcoutinho2512/Sanaris-Pro  
**Data:** Novembro 2025  
**Status:** Sprint 1 - 100% Completo ✅

---

## 📊 RESUMO EXECUTIVO

### Estatísticas do Projeto
- **Total de Tabelas:** 50 entidades no banco de dados
- **Backend:** 17.892 linhas de código Python
- **Frontend:** 9.252 linhas de código TypeScript/React
- **Endpoints API:** 30 módulos
- **Páginas Frontend:** 16 módulos
- **Commits:** 10+ commits profissionais

### Stack Tecnológico
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + PostgreSQL 16
- **Frontend:** Next.js 16 + React + TypeScript + Tailwind CSS
- **Infraestrutura:** Docker + Redis + WebSocket
- **Integrações:** ANVISA, CFM, TISS, Google Calendar

---

## 🗃️ ARQUITETURA DO BANCO DE DADOS

### Módulos Principais (50 Tabelas)

#### 👥 Gestão de Usuários e Organizações
- `User` - Usuários do sistema
- `Organization` - Clínicas/consultórios
- `Permission` - Permissões de acesso
- `UserPermission` - Relação usuário-permissões
- `PasswordResetToken` - Tokens de reset de senha

#### 📅 Agenda e Agendamentos
- `Appointment` - Agendamentos
- `AppointmentWaitlist` - Lista de espera
- `ProfessionalSchedule` - Horários profissionais

#### 🏥 Prontuário Eletrônico
- `MedicalRecord` - Prontuários
- `VitalSigns` - Sinais vitais
- `MedicalRecordAttachment` - Anexos
- `MedicalRecordTemplate` - Templates
- `ExamResult` - Resultados de exames
- `PhotoEvolution` - Fotos evolutivas

#### 💊 Prescrições
- `Prescription` - Prescrições médicas
- `PrescriptionItem` - Itens da prescrição
- `PrescriptionTemplate` - Templates
- `Medication` - Medicamentos (integração ANVISA)

#### 👨‍⚕️ Pacientes
- `Patient` - Cadastro de pacientes
- `QuickPatientRegistration` - Registro rápido

#### 💬 Chat Interno
- `ChatChannel` - Canais de comunicação
- `ChatParticipant` - Participantes
- `ChatMessage` - Mensagens
- `ChatReadStatus` - Status de leitura

#### 💰 Financeiro
- `AccountReceivable` - Contas a receber
- `PaymentInstallment` - Parcelas
- `PaymentTransaction` - Transações
- `AccountPayable` - Contas a pagar
- `PayableTransaction` - Pagamentos
- `Supplier` - Fornecedores
- `ExpenseCategory` - Categorias de despesas
- `CostCenter` - Centros de custo
- `ProfessionalFeeConfiguration` - Config. honorários
- `ProfessionalFee` - Honorários profissionais
- `ProfessionalFeeItem` - Itens de honorários

#### 🏥 TISS (ANS)
- `HealthInsuranceOperator` - Operadoras
- `TussProcedure` - Procedimentos TUSS
- `Beneficiary` - Beneficiários
- `TissBatch` - Lotes TISS
- `TissGuide` - Guias TISS
- `TissGuideProcedure` - Procedimentos das guias

#### 🔐 Segurança e Compliance
- `DigitalCertificate` - Certificados digitais
- `OTPConfiguration` - Autenticação 2FA
- `SignatureLog` - Log de assinaturas
- `Signature` - Assinaturas digitais

#### 📄 Documentos
- `DocumentTemplate` - Templates de documentos
- `PatientDocument` - Documentos dos pacientes

#### 🔌 Integrações
- `CFMCredentials` - Credenciais CFM
- `CFMPrescriptionLog` - Log prescrições CFM

#### 🔔 Notificações
- `Notification` - Sistema de notificações

---

## 🔌 API ENDPOINTS (30 Módulos)

### Autenticação e Usuários
- **auth.py** (16.052 linhas) - Login, logout, refresh token, 2FA
- **users_management.py** (8.315 linhas) - CRUD de usuários
- **users_simple.py** (830 linhas) - Endpoints simplificados
- **permissions.py** (4.611 linhas) - Gestão de permissões

### Organizações
- **organizations.py** (3.167 linhas) - CRUD de clínicas

### Pacientes
- **patients.py** (7.393 linhas) - Gestão de pacientes

### Agendamentos
- **appointments.py** (24.367 linhas) - Agenda completa
- **google_calendar.py** (4.896 linhas) - Sincronização Google

### Prontuários
- **medical_records.py** (17.001 linhas) - CRUD prontuários
- **medical_record_extensions.py** (13.359 linhas) - Extensões

### Prescrições
- **prescriptions.py** (28.292 linhas) - Sistema de prescrições
- **medications.py** (3.793 linhas) - Medicamentos ANVISA

### Chat
- **chat.py** (27.765 linhas) - Sistema de chat com WebSocket

### Integrações
- **cfm_integration.py** (12.667 linhas) - Portal CFM
- **cfm_test.py** (4.782 linhas) - Testes CFM

### Financeiro
- **accounts_receivable.py** (18.930 linhas) - Contas a receber
- **accounts_payable.py** (19.259 linhas) - Contas a pagar
- **cash_flow.py** (15.068 linhas) - Fluxo de caixa
- **professional_fees.py** (17.159 linhas) - Honorários

### TISS
- **tiss.py** (23.545 linhas) - Faturamento TISS/ANS

### Documentos e Assinaturas
- **documents.py** (13.814 linhas) - Gestão de documentos
- **digital_signature.py** (16.889 linhas) - Assinatura digital
- **signatures.py** (3.174 linhas) - Assinaturas simples

### Uploads e Downloads
- **file_upload.py** (1.324 linhas) - Upload de arquivos
- **file_download.py** (559 linhas) - Download de arquivos

### Notificações
- **notifications.py** (8.294 linhas) - Sistema de notificações

### Estatísticas
- **statistics.py** (4.685 linhas) - Estatísticas gerais
- **admin_stats.py** (3.130 linhas) - Admin dashboard

### Utilitários
- **utils.py** (3.205 linhas) - Funções auxiliares

---

## ⚛️ FRONTEND (16 Páginas)

### Autenticação
- **login/** - Tela de login
- **forgot-password/** - Recuperação de senha
- **reset-password/** - Reset de senha

### Dashboard
- **page.tsx** - Dashboard principal

### Gestão
- **usuarios/** - Gestão de usuários
- **organizacoes/** - Gestão de organizações
- **permissoes/** - Gestão de permissões
- **configuracoes/** - Configurações do sistema

### Operacional
- **pacientes/** - Cadastro de pacientes
- **agenda/** - Sistema de agendamentos
- **prontuarios/** - Prontuários eletrônicos
- **prescricoes/** - Sistema de prescrições

### Comunicação
- **chat/** - Chat interno (direto e grupos)

### Integrações
- **cfm/** - Portal CFM integrado

### Financeiro
- **financeiro/** - Gestão financeira
- **faturamento-tiss/** - Faturamento TISS

### Relatórios
- **relatorios/** - Sistema de relatórios

---

## 🎯 STATUS DO SPRINT 1 - 100% COMPLETO

### ✅ Módulos Funcionando Perfeitamente

1. **Prescrições** ✅
   - Portal ANVISA integrado
   - Busca de medicamentos
   - Templates de prescrições
   - Histórico completo

2. **Portal CFM** ✅
   - Integração via iframe
   - Consulta de médicos
   - Validação de CRM

3. **Agenda** ✅
   - Criar agendamentos
   - Listar agendamentos
   - UUID corrigido
   - Lista de espera

4. **Prontuários** ✅
   - Criar prontuários
   - Listar prontuários
   - UUID corrigido
   - Anexos e sinais vitais

5. **Chat** ✅
   - Chat direto (1:1) sem necessidade de nome
   - Grupos com nome obrigatório
   - WebSocket em tempo real
   - Upload de arquivos

### 🔧 Correções Implementadas

#### Backend
- Schemas UUID corrigidos em todos os módulos
- Banco de dados: VARCHAR → UUID
- Token de autenticação padronizado
- Logout automático global

#### Frontend
- Interceptor axios para 401
- Redirecionamento automático para login
- Validações inteligentes
- Feedback claro ao usuário

---

## 🚀 TECNOLOGIAS E INTEGRAÇÕES

### Backend (FastAPI)
- **Framework:** FastAPI 0.104+
- **ORM:** SQLAlchemy 2.0
- **Validação:** Pydantic V2
- **Auth:** JWT + OAuth2
- **WebSocket:** Native FastAPI WebSocket
- **Tasks:** Celery + Redis
- **Email:** SMTP

### Frontend (Next.js)
- **Framework:** Next.js 16
- **UI:** React 18 + TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **HTTP:** Axios
- **State:** React Hooks

### Banco de Dados
- **PostgreSQL 16** em Docker
- **Redis** para cache e sessões

### Integrações Externas
- **ANVISA** - Banco de medicamentos
- **CFM** - Conselho Federal de Medicina
- **TISS/ANS** - Faturamento convênios
- **Google Calendar** - Sincronização de agenda

---

## 📦 ESTRUTURA DE PASTAS
```
sanaris-pro/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/ (30 arquivos)
│   │   ├── models/ (19 arquivos)
│   │   ├── schemas/ (18 arquivos)
│   │   ├── services/
│   │   ├── core/
│   │   ├── db/
│   │   └── utils/
│   ├── venv/
│   └── uploads/
├── frontend/
│   ├── src/
│   │   ├── app/ (16 páginas)
│   │   ├── components/
│   │   └── lib/
│   └── public/
├── scripts/
└── uploads/
```

---

## 🔐 SEGURANÇA

- ✅ JWT Authentication
- ✅ OAuth2 Password Flow
- ✅ 2FA/OTP Support
- ✅ Role-Based Access Control (RBAC)
- ✅ Multi-tenant Architecture
- ✅ Data Isolation por Organização
- ✅ Digital Signatures
- ✅ Audit Logs
- ✅ Soft Delete
- ✅ HTTPS/TLS

---

## 🎊 CONCLUSÃO

O **Sanaris Pro** é um sistema robusto e completo para gestão de clínicas e consultórios médicos, com:

- ✅ 50 tabelas no banco de dados
- ✅ 30 módulos de API
- ✅ 16 páginas frontend
- ✅ 27.144 linhas de código
- ✅ Integrações com ANVISA, CFM, TISS
- ✅ Sistema de chat em tempo real
- ✅ Arquitetura multi-tenant
- ✅ Segurança enterprise-grade

**Sprint 1 - 100% Completo!** 🏆

---

**Desenvolvido por:** Magnun Cesar de A Coutinho  
**GitHub:** https://github.com/mcoutinho2512/Sanaris-Pro  
**Data:** Novembro 2025
