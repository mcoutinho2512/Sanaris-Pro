# 📋 BACKLOG ATUALIZADO - SANARIS PRO
**Última Atualização:** 22/11/2025 (após implementação XML TISS)  
**Versão do Sistema:** 1.0.0  
**Repositório:** https://github.com/mcoutinho2512/Sanaris-Pro

---

## ✅ SISTEMA ATUAL - 100% IMPLEMENTADO

### 📊 ESTATÍSTICAS
| Métrica | Valor |
|---------|-------|
| **Total de Endpoints** | 279 |
| **Total de Tabelas** | 48 |
| **Módulos Completos** | 11 |
| **Progresso Geral** | ~90% |

---

### 🎯 MÓDULOS IMPLEMENTADOS

#### 1. **CORE & AUTENTICAÇÃO** ✅
- Google OAuth 2.0 integrado
- JWT + bcrypt para segurança
- Sistema multi-tenant (por organização)
- Roles: super_admin, admin, user
- Gerenciamento de usuários
- Sistema de permissões por módulo
- Logout automático após inatividade

#### 2. **GESTÃO DE PACIENTES** ✅
- CRUD completo de pacientes
- Busca global inteligente
- Histórico completo
- Dashboard de estatísticas
- Soft delete (recuperação)

#### 3. **AGENDA INTELIGENTE** ✅
- Calendário visual completo
- Agendamento rápido
- Sistema de cargos (médicos, secretárias, etc)
- Filtros por profissional
- Lista de espera
- Confirmações automáticas (WhatsApp/Email/SMS)
- Status de controle (confirmado, aguardando, cancelado, etc)
- Integração Google Calendar

#### 4. **PRONTUÁRIOS ELETRÔNICOS** ✅
- CRUD completo
- Interface intuitiva
- Linha do tempo do paciente
- Sinais vitais
- Anexos (imagens, PDFs)
- Histórico completo de atendimentos
- Assinatura digital

#### 5. **PRESCRIÇÕES DIGITAIS** ✅
- Integração com base ANVISA (13.000+ medicamentos)
- Múltiplos medicamentos por prescrição
- Templates customizáveis
- Envio digital (Email/WhatsApp)
- Histórico completo
- Assinatura digital

#### 6. **PORTAL CFM** ✅
- Integração via iframe
- Consulta de médicos
- Validação de CRM
- Acesso direto ao portal

#### 7. **NOTIFICAÇÕES** ✅
- WhatsApp (Twilio)
- SMS (Twilio)
- Email (SMTP configurável)
- Templates personalizáveis
- Histórico de envios
- Confirmações de agendamento
- Lembretes automáticos

#### 8. **CHAT INTERNO** ✅
- Chat direto entre usuários
- Chat em grupo
- WebSocket em tempo real
- Histórico de mensagens
- Notificações

#### 9. **GESTÃO FINANCEIRA** ✅
- **Contas a Receber:**
  - CRUD completo
  - Status (pendente, pago, cancelado)
  - Filtros avançados
  - Ações em lote
  - Relatórios

- **Contas a Pagar:**
  - CRUD completo
  - Gestão de fornecedores
  - Categorias de despesas
  - Aprovação de pagamentos
  - Controle de vencimentos

- **Fluxo de Caixa:**
  - Dashboard em tempo real
  - Análises diárias/mensais
  - Projeções futuras
  - Gráficos interativos

- **Repasse Profissionais:**
  - Configuração individual
  - Percentual ou valor fixo
  - Retenções (INSS, IR, ISS)
  - Geração automática
  - Relatórios completos

#### 10. **FATURAMENTO TISS** ✅ (COMPLETO)
- **Operadoras de Planos:**
  - CRUD completo
  - Código ANS (6 dígitos)
  - 4 tipos: Medicina de Grupo, Cooperativa, Filantropia, Autogestão
  - Configurações TISS (versão, prazos)
  - Dados bancários

- **Tabela TUSS:**
  - Importação CSV de procedimentos
  - 13.000+ procedimentos cadastrados
  - Códigos e descrições oficiais
  - Valores padrão
  - 5 tipos de procedimentos

- **Lotes TISS:**
  - Criação e gerenciamento
  - Agrupamento de guias
  - Status (rascunho, fechado, enviado, processado)
  - Controle de protocolo

- **Guias TISS:**
  - 5 tipos de guias (Consulta, SP/SADT, Internação, etc)
  - Múltiplos procedimentos por guia
  - Vinculação com pacientes
  - CID-10
  - Sistema de glosas

- **GERAÇÃO XML TISS:** ✅ **NOVO!**
  - Padrão ANS 4.03.00
  - Validação pré-geração
  - Download automático
  - Nomenclatura: TISS_{OPERADORA}_{LOTE}_{DATA}.xml
  - Hash MD5 para validação
  - Feedback visual de erros/avisos

#### 11. **DASHBOARD ANALÍTICO** ✅
- Cards de métricas em tempo real
- Gráficos de pizza (Chart.js)
- Gráficos de barra
- Estatísticas agregadas
- Visual profissional
- Análise por período
- Distribuição por gênero

---

## 🚀 BACKLOG - O QUE FALTA FAZER

### 🔴 PRIORIDADE CRÍTICA (1-2 semanas)

#### 1. **RELATÓRIOS DE FATURAMENTO TISS** ⏳
**Tempo estimado:** 30 minutos  
**Complexidade:** Baixa  
**Descrição:**
- Dashboard de faturamento por período
- Gráficos de valores por operadora
- Análise de glosas
- Exportação Excel/PDF
- Resumo mensal de envios

**Entregáveis:**
- Página: `/faturamento-tiss/relatorios`
- Gráficos interativos
- Filtros por data/operadora
- Exportações

---

### 🟡 PRIORIDADE ALTA (2-4 semanas)

#### 2. **PORTAL DO PACIENTE + AGENDAMENTO ONLINE** ⏳
**Tempo estimado:** 6-8 horas  
**Complexidade:** Alta  
**Descrição:**
- Portal React autônomo
- Login com CPF + data nascimento
- Agendar/Cancelar/Reagendar online
- Escolha de profissional e convênio
- Confirmação automática
- Dashboard do paciente
- Histórico de consultas
- Visualização de prescrições

**Entregáveis:**
- Subdomínio: `portal.sanaris.com.br`
- App mobile-first (PWA)
- Notificações push
- Sistema de avaliação

**Impacto:** Reduz ligações telefônicas em 60%+

---

#### 3. **PAGAMENTO ONLINE** ⏳
**Tempo estimado:** 4-6 horas  
**Complexidade:** Média-Alta  
**Descrição:**
- Integração Mercado Pago
- PIX
- Cartão de crédito/débito
- Boleto bancário
- Webhooks para confirmação
- Relatório de pagamentos
- Conciliação automática
- Pagamento na confirmação de agendamento

**Entregáveis:**
- Checkout integrado
- Confirmação automática de recebimento
- Relatórios financeiros
- Baixa automática de contas

**Impacto:** Reduz inadimplência em 40%+

---

#### 4. **EMISSÃO DE NFS-e** ⏳
**Tempo estimado:** 5-7 horas  
**Complexidade:** Alta  
**Descrição:**
- Integração com prefeituras (API)
- Suporte aos principais municípios brasileiros
- Emissão automática pós-atendimento
- Configuração de série e alíquota
- Logs e retorno do envio
- Envio automático ao paciente (Email/WhatsApp)
- Cancelamento de notas
- Relatório de notas emitidas

**Entregáveis:**
- Configuração por município
- Emissão em lote
- Reemissão de 2ª via
- Relatório mensal para contabilidade

**Municípios prioritários:** São Paulo, Rio de Janeiro, Brasília, Belo Horizonte

---

### 🟢 PRIORIDADE MÉDIA (1-2 meses)

#### 5. **NPS / PESQUISA DE SATISFAÇÃO** ⏳
**Tempo estimado:** 3-4 horas  
**Complexidade:** Média  
**Descrição:**
- Envio automático pós-atendimento
- Templates customizáveis
- Escala NPS (0-10)
- Perguntas adicionais opcionais
- Dashboard de satisfação
- Cálculo de NPS
- Análise de tendências
- Relatórios gerenciais
- Alertas para avaliações negativas

**Entregáveis:**
- Sistema completo de pesquisas
- Dashboard NPS em tempo real
- Respostas automáticas
- Integração com chat

---

#### 6. **E-MAIL MARKETING** ⏳
**Tempo estimado:** 4-5 horas  
**Complexidade:** Média  
**Descrição:**
- Editor de templates (WYSIWYG)
- Segmentação de pacientes
- Campanhas programadas
- Histórico de envios
- Métricas (aberturas, cliques)
- Landing pages
- Formulários de captura
- Automações (aniversários, retorno, etc)

**Entregáveis:**
- Editor visual de emails
- Biblioteca de templates
- Analytics completo
- Integração com SMTP

---

#### 7. **TOTEM DE AUTOATENDIMENTO** ⏳
**Tempo estimado:** 6-8 horas  
**Complexidade:** Alta  
**Descrição:**
- Interface touch-screen
- Check-in automático
- Busca por CPF ou telefone
- Impressão de comprovantes
- Confirmação de dados
- Atualização de cadastro
- Integração com agenda
- Modo kiosk (fullscreen, sem navegação)

**Entregáveis:**
- App React dedicado
- Suporte a impressora térmica
- Leitor de código de barras
- Modo offline

---

#### 8. **GESTÃO DE ESTOQUE** ⏳
**Tempo estimado:** 4-6 horas  
**Complexidade:** Média  
**Descrição:**
- Cadastro de insumos e medicamentos
- Controle de lotes
- Validade e alertas
- Entrada e saída
- Requisições internas
- Inventário
- Relatórios de consumo
- Integração com prescrições

**Entregáveis:**
- CRUD completo
- Dashboard de estoque
- Alertas de vencimento
- Relatório de consumo por profissional

---

### ⚪ PRIORIDADE BAIXA (Backlog futuro)

#### 9. **APP WHITE LABEL / MOBILE** ⏳
**Tempo estimado:** 15-20 horas  
**Complexidade:** Muito Alta  
**Descrição:**
- React Native
- iOS + Android
- Branding personalizado por clínica
- Todas as funcionalidades do portal
- Notificações push
- Agenda do profissional
- Prontuário móvel
- Offline-first

---

#### 10. **INTEGRAÇÃO COM LABORATÓRIOS** ⏳
**Tempo estimado:** 4-6 horas  
**Complexidade:** Alta  
**Descrição:**
- Envio de pedidos de exames
- Recebimento de resultados
- Anexar resultados ao prontuário
- Notificação ao paciente
- Principais labs: Fleury, Dasa, etc

---

#### 11. **TELEMEDICINA** ⏳
**Tempo estimado:** 8-10 horas  
**Complexidade:** Muito Alta  
**Descrição:**
- Videochamadas integradas
- Agendamento específico para telemedicina
- Gravação de consultas (opcional)
- Prontuário durante a chamada
- Prescrição online
- Conformidade CFM

---

## 📊 CRONOGRAMA SUGERIDO

### **MÊS 1 - Consolidação**
- Semana 1-2: Relatórios de Faturamento TISS
- Semana 3-4: Testes e correções gerais

### **MÊS 2 - Crescimento Comercial**
- Semana 1-2: Portal do Paciente
- Semana 3-4: Pagamento Online

### **MÊS 3 - Compliance**
- Semana 1-2: NFS-e
- Semana 3-4: NPS/Satisfação

### **MÊS 4 - Expansão**
- Semana 1-2: E-mail Marketing
- Semana 3-4: Totem de Autoatendimento

### **MÊS 5 - Operacional**
- Semana 1-2: Gestão de Estoque
- Semana 3-4: Integração Laboratórios

### **MÊS 6+ - Mobile & Avançado**
- App Mobile (White Label)
- Telemedicina
- Inteligência Artificial (sugestões diagnósticas)

---

## 🎯 MELHORIAS CONTÍNUAS

### **UX/UI**
- [ ] Tema escuro
- [ ] Customização de cores por clínica
- [ ] Tour guiado para novos usuários
- [ ] Atalhos de teclado
- [ ] Modo compacto/expandido

### **Performance**
- [ ] Cache Redis otimizado
- [ ] Lazy loading de componentes
- [ ] Compressão de imagens
- [ ] CDN para assets estáticos
- [ ] Server-Side Rendering (SSR)

### **Segurança**
- [ ] 2FA (Two-Factor Authentication)
- [ ] Biometria
- [ ] Auditoria completa de ações
- [ ] Backup automático diário
- [ ] Criptografia end-to-end para chat

### **Integrações**
- [ ] Zoom/Meet para telemedicina
- [ ] Memed API (alternativa ANVISA)
- [ ] RD Station (CRM)
- [ ] Google Analytics
- [ ] Hotjar (heatmaps)

---

## 📈 MÉTRICAS DE SUCESSO

### **Técnicas**
- Uptime > 99.9%
- Tempo de resposta < 200ms
- Taxa de erro < 0.1%
- Cobertura de testes > 80%

### **Negócio**
- Redução de 60% em ligações telefônicas
- Redução de 40% em inadimplência
- NPS > 50
- Taxa de adoção > 90%

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **AGORA:** Relatórios de Faturamento (~30min)
2. **Esta Semana:** Testes completos do TISS XML
3. **Próxima Semana:** Portal do Paciente (início)

---

**Desenvolvido por:** Magnun Cesar de A. Coutinho  
**GitHub:** https://github.com/mcoutinho2512/Sanaris-Pro  
**Contato:** magnun@sanarispro.com.br

