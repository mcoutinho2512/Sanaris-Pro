# 📋 BACKLOG - SANARIS PRO

**Última atualização:** 18/11/2025
**Versão:** 1.0.0

---

## ✅ CONCLUÍDO

### FASE 1 - Core & Autenticação
- [x] Sistema de autenticação (Google OAuth + JWT)
- [x] Gestão de usuários e organizações
- [x] Permissões por módulos
- [x] Dashboard analítico com estatísticas
- [x] Pacientes (CRUD completo)
- [x] Prontuários eletrônicos
- [x] Prescrições digitais com ANVISA
- [x] Chat em tempo real (WebSocket)
- [x] Assinatura digital
- [x] Portal CFM

---

## 🚧 EM DESENVOLVIMENTO

### FASE 2 - Agendamento Completo

#### 📅 Sistema de Agenda Visual
**Prioridade:** ALTA
**Descrição:** Ao clicar em "Agendar" ou "Agenda", abrir interface visual com:

**Requisitos:**
1. **Visualização por Profissional:**
   - Selecionar médico/profissional
   - Ver agenda do profissional selecionado
   - Filtro por especialidade

2. **Grade de Horários:**
   - Visualização por dia/semana/mês
   - Horários disponíveis em verde
   - Horários ocupados em vermelho
   - Horários bloqueados em cinza
   - Hover mostrando detalhes (paciente, tipo de consulta)

3. **Configuração de Agenda:**
   - Definir horário de trabalho de cada profissional
   - Duração padrão das consultas (configurável por profissional)
   - Intervalos (almoço, coffee break)
   - Dias de folga/férias
   - Bloqueio de horários específicos

4. **Agendamento Rápido:**
   - Clicar em horário disponível abre modal
   - Buscar paciente (autocomplete)
   - Selecionar tipo de consulta
   - Adicionar observações
   - Confirmar agendamento

5. **Recursos Adicionais:**
   - Drag & drop para reagendar
   - Visualização de múltiplos profissionais simultaneamente
   - Legenda de cores e status
   - Filtros por status, tipo de consulta, paciente
   - Exportar agenda (PDF/Excel)

**Tecnologias Sugeridas:**
- FullCalendar ou React Big Calendar
- Drag & drop: react-dnd ou similar
- Backend: endpoints para disponibilidade e bloqueios

**Endpoints Necessários:**
```
GET  /api/v1/schedule/availability?professional_id=X&date=Y
POST /api/v1/schedule/block-time
GET  /api/v1/schedule/calendar?professional_id=X&start=Y&end=Z
PUT  /api/v1/appointments/{id}/reschedule
```

---

## �� BACKLOG - FASE 3 (Financeiro)

### 1. 💰 Gestão Financeira Completa
**Prioridade:** ALTA
**Status:** Pendente

**Funcionalidades:**
- [ ] Contas a Receber
  - [ ] Geração automática ao agendar consulta
  - [ ] Parcelamento
  - [ ] Controle de inadimplência
  - [ ] Cobrança automática via e-mail/SMS
  
- [ ] Contas a Pagar
  - [ ] Fornecedores
  - [ ] Despesas recorrentes
  - [ ] Centro de custos
  
- [ ] Fluxo de Caixa
  - [ ] Visão diária/mensal/anual
  - [ ] Projeções
  - [ ] Gráficos de entrada/saída
  
- [ ] Relatórios Financeiros
  - [ ] DRE (Demonstração de Resultado)
  - [ ] Inadimplência
  - [ ] Faturamento por profissional
  - [ ] Faturamento por convênio

**Estimativa:** 4-6 semanas

---

### 2. 🏥 Faturamento TISS
**Prioridade:** ALTA
**Status:** Parcialmente implementado (modelos criados)

**Funcionalidades:**
- [ ] Geração de lotes TISS
- [ ] Validação XML conforme padrão TISS
- [ ] Envio para operadoras
- [ ] Acompanhamento de glosas
- [ ] Recurso de glosas
- [ ] Integração com convênios principais:
  - [ ] Unimed
  - [ ] Bradesco Saúde
  - [ ] SulAmérica
  - [ ] Amil
  - [ ] Porto Seguro

**Estimativa:** 6-8 semanas

---

### 3. 💳 Pagamento Online
**Prioridade:** MÉDIA
**Status:** Pendente

**Funcionalidades:**
- [ ] Integração com gateways de pagamento:
  - [ ] Mercado Pago
  - [ ] PagSeguro
  - [ ] Stripe
  - [ ] Rede/Cielo
  
- [ ] Formas de pagamento:
  - [ ] Cartão de crédito
  - [ ] PIX
  - [ ] Boleto
  - [ ] Débito online
  
- [ ] Recursos:
  - [ ] Link de pagamento via WhatsApp/E-mail
  - [ ] QR Code PIX
  - [ ] Parcelamento no cartão
  - [ ] Cashback/desconto à vista
  - [ ] Recibo automático

**Estimativa:** 3-4 semanas

---

### 4. 🧾 Emissão NFS-e
**Prioridade:** MÉDIA
**Status:** Pendente

**Funcionalidades:**
- [ ] Integração com prefeituras (RPS)
- [ ] Geração automática após consulta
- [ ] Envio automático por e-mail
- [ ] Cancelamento de NF
- [ ] Relatórios de NFs emitidas
- [ ] Controle de ISS

**Municípios Prioritários:**
- [ ] São Paulo
- [ ] Rio de Janeiro
- [ ] Belo Horizonte
- [ ] Brasília
- [ ] Curitiba

**Estimativa:** 4-5 semanas

---

### 5. 📧 E-mail Marketing
**Prioridade:** BAIXA
**Status:** Pendente

**Funcionalidades:**
- [ ] Criador de campanhas
- [ ] Templates prontos
- [ ] Segmentação de pacientes
- [ ] Agendamento de envios
- [ ] Relatórios de abertura/cliques
- [ ] Integração com:
  - [ ] Mailchimp
  - [ ] SendGrid
  - [ ] Amazon SES

**Casos de Uso:**
- Aniversariantes do mês
- Lembretes de check-up
- Novidades da clínica
- Campanhas de prevenção

**Estimativa:** 2-3 semanas

---

### 6. 📱 Lembretes Automáticos - SMS/WhatsApp
**Prioridade:** ALTA
**Status:** Infraestrutura criada, precisa ativação

**Funcionalidades:**
- [ ] WhatsApp Business API
  - [ ] Mensagem 24h antes da consulta
  - [ ] Mensagem 1h antes da consulta
  - [ ] Confirmação por WhatsApp
  - [ ] Cancelamento por WhatsApp
  
- [ ] SMS
  - [ ] Integração com Twilio
  - [ ] Integração com Total Voice
  
- [ ] Configurações:
  - [ ] Horários de envio
  - [ ] Templates personalizáveis
  - [ ] Opt-out de pacientes
  - [ ] Relatório de envios

**Estimativa:** 2-3 semanas

---

## 🆕 NOVAS FUNCIONALIDADES

### 7. 👔 Sistema de Cargos/Funções
**Prioridade:** ALTA
**Status:** Pendente

**Descrição:** 
Adicionar campo "cargo" no cadastro de usuários, complementando o "role" existente.

**Diferença entre Role e Cargo:**
- **Role:** Nível de acesso (super_admin, admin, user)
- **Cargo:** Função específica na clínica

**Cargos Sugeridos:**
- Médico(a)
- Enfermeiro(a)
- Técnico(a) de Enfermagem
- Psicólogo(a)
- Fisioterapeuta
- Nutricionista
- Dentista
- Recepcionista
- Secretária
- Assistente Administrativo
- Financeiro
- Faturista TISS
- Gerente
- Diretor(a)

**Implementação:**

1. **Backend:**
```python
# Adicionar campo na tabela users
cargo = Column(String(100))

# Criar tabela de cargos pré-definidos
class JobTitle(Base):
    __tablename__ = "job_titles"
    id = Column(UUID, primary_key=True)
    name = Column(String(100), unique=True)
    department = Column(String(50))  # Médico, Administrativo, etc
    is_healthcare_professional = Column(Boolean, default=False)
    can_schedule_appointments = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Frontend:**
- Dropdown no cadastro de usuários
- Filtro por cargo no gerenciamento
- Badge visual mostrando o cargo

3. **Benefícios:**
- Relatórios por cargo
- Filtrar agenda por tipo de profissional
- Atribuições específicas por cargo
- Organograma da clínica

**Estimativa:** 1 semana

---

## 📊 MELHORIAS FUTURAS

### Interface & UX
- [ ] Tema escuro (dark mode)
- [ ] Customização de cores por organização
- [ ] Dashboard personalizável (widgets arrastáveis)
- [ ] Atalhos de teclado
- [ ] Tour guiado para novos usuários

### Relatórios
- [ ] Relatórios customizáveis
- [ ] Agendamento de relatórios por e-mail
- [ ] Exportação para Excel/PDF
- [ ] Business Intelligence (BI) integrado

### Mobile
- [ ] App mobile nativo (React Native)
- [ ] Versão PWA otimizada
- [ ] Notificações push

### Integrações
- [ ] Google Calendar (sincronização bidirecional)
- [ ] Zoom/Meet para telemedicina
- [ ] Laboratórios (integração de resultados)
- [ ] Farmácias (envio de receitas)

### Segurança
- [ ] Autenticação de dois fatores (2FA)
- [ ] Biometria
- [ ] Auditoria completa de ações
- [ ] Backup automático

---

## 🎯 PRIORIZAÇÃO SUGERIDA

### Sprint 2 (Próximo)
1. ✅ Sistema de Cargos
2. ✅ Agenda Visual Completa
3. ✅ Lembretes WhatsApp (ativação)

### Sprint 3
1. Gestão Financeira Completa
2. Faturamento TISS (fase 1)
3. Relatórios Financeiros

### Sprint 4
1. Pagamento Online
2. NFS-e (municípios principais)
3. E-mail Marketing

---

## 📝 NOTAS

- Sempre priorizar funcionalidades que agregam valor direto ao cliente
- Manter foco em conformidade com LGPD e regulamentações de saúde
- Testar extensivamente antes de deploy em produção
- Documentar todas as integrações externas
- Manter código limpo e bem comentado

---

**Responsável:** Magnun Cesar de Azeredo Coutinho
**Última revisão:** 18/11/2025
