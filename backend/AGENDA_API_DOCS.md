# 📅 API de Agendamentos - Documentação Completa

## 🎯 Visão Geral

API completa para gestão de agendamentos com recursos avançados:
- ✅ CRUD completo de agendamentos
- ✅ Confirmações automáticas (WhatsApp, Email, SMS)
- ✅ Lista de espera inteligente
- ✅ Escalas configuráveis de profissionais
- ✅ Verificação de disponibilidade
- ✅ Controle de status do fluxo completo
- ✅ Multiprofissionais

---

## 📋 Endpoints de Agendamentos

### 1. Criar Agendamento
**POST** `/api/v1/appointments/`

Cria um novo agendamento com verificação automática de conflitos.

**Request Body:**
```json
{
  "patient_id": 1,
  "healthcare_professional_id": 2,
  "scheduled_date": "2025-11-10T14:00:00",
  "duration_minutes": 30,
  "appointment_type": "first_time",
  "reason": "Consulta de rotina",
  "notes": "Paciente com histórico de hipertensão",
  "price": 150.00
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "tenant_id": 1,
  "patient_id": 1,
  "healthcare_professional_id": 2,
  "scheduled_date": "2025-11-10T14:00:00",
  "duration_minutes": 30,
  "appointment_type": "first_time",
  "status": "scheduled",
  "confirmation_sent": false,
  "confirmed_at": null,
  "is_waitlist": false,
  "created_at": "2025-11-02T10:00:00"
}
```

---

### 2. Listar Agendamentos (com filtros avançados)
**GET** `/api/v1/appointments/?page=1&page_size=20`

Lista agendamentos com paginação e múltiplos filtros.

**Query Parameters:**
- `page` (int): Número da página (padrão: 1)
- `page_size` (int): Itens por página (padrão: 20, máx: 100)
- `status_filter` (enum): scheduled | confirmed | in_progress | completed | cancelled | no_show
- `professional_id` (int): Filtrar por profissional
- `patient_id` (int): Filtrar por paciente
- `date_from` (date): Data inicial (YYYY-MM-DD)
- `date_to` (date): Data final (YYYY-MM-DD)

**Exemplo:**
```
GET /api/v1/appointments/?status_filter=scheduled&date_from=2025-11-01&date_to=2025-11-30
```

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

### 3. Buscar Agendamento por ID
**GET** `/api/v1/appointments/{appointment_id}`

**Response:** `200 OK` (retorna objeto completo do agendamento)

---

### 4. Atualizar Agendamento
**PUT** `/api/v1/appointments/{appointment_id}`

Atualiza dados do agendamento. Não permite editar agendamentos concluídos ou cancelados.

**Request Body:**
```json
{
  "scheduled_date": "2025-11-10T15:00:00",
  "duration_minutes": 45,
  "notes": "Paciente solicitou mais tempo"
}
```

**Response:** `200 OK`

---

### 5. Deletar Agendamento
**DELETE** `/api/v1/appointments/{appointment_id}`

Realiza soft delete do agendamento.

**Response:** `200 OK`
```json
{
  "message": "Agendamento deletado com sucesso",
  "success": true
}
```

---

### 6. Enviar Confirmação
**POST** `/api/v1/appointments/{appointment_id}/send-confirmation?method=whatsapp`

Envia confirmação de agendamento via WhatsApp, Email ou SMS.

**Query Parameters:**
- `method` (enum): whatsapp | email | sms

**Response:** `200 OK`
```json
{
  "message": "Confirmação enviada via whatsapp",
  "success": true
}
```

---

### 7. Confirmar Agendamento (recebido do paciente)
**POST** `/api/v1/appointments/{appointment_id}/confirm`

Marca agendamento como confirmado após resposta do paciente.

**Request Body:**
```json
{
  "confirmation_method": "whatsapp",
  "confirmed_by": "patient"
}
```

**Response:** `200 OK`

---

### 8. Check-in do Paciente
**POST** `/api/v1/appointments/{appointment_id}/check-in`

Registra chegada do paciente na clínica.

**Response:** `200 OK`

---

### 9. Iniciar Atendimento
**POST** `/api/v1/appointments/{appointment_id}/start`

Inicia o atendimento médico.

**Response:** `200 OK` (status muda para `in_progress`)

---

### 10. Finalizar Atendimento
**POST** `/api/v1/appointments/{appointment_id}/complete`

Finaliza o atendimento.

**Response:** `200 OK` (status muda para `completed`)

---

### 11. Cancelar Agendamento
**POST** `/api/v1/appointments/{appointment_id}/cancel`

Cancela um agendamento.

**Request Body:**
```json
{
  "cancellation_reason": "Paciente solicitou reagendamento por motivos pessoais"
}
```

**Response:** `200 OK` (status muda para `cancelled`)

---

### 12. Marcar como Falta
**POST** `/api/v1/appointments/{appointment_id}/no-show`

Marca que paciente faltou ao agendamento.

**Response:** `200 OK` (status muda para `no_show`)

---

## 📋 Lista de Espera

### 13. Adicionar à Lista de Espera
**POST** `/api/v1/waitlist/`

**Request Body:**
```json
{
  "patient_id": 1,
  "healthcare_professional_id": 2,
  "preferred_date": "2025-11-15T14:00:00",
  "preferred_period": "afternoon",
  "appointment_type": "return",
  "priority": 5,
  "urgency_level": "medium",
  "reason": "Paciente aguardando retorno",
  "notes": "Preferência por horários após 14h"
}
```

**Response:** `201 Created`

---

### 14. Listar Fila de Espera
**GET** `/api/v1/waitlist/?active_only=true`

Lista pacientes na fila de espera ordenados por prioridade.

**Response:** `200 OK`

---

### 15. Buscar Entrada da Fila
**GET** `/api/v1/waitlist/{waitlist_id}`

**Response:** `200 OK`

---

### 16. Atualizar Entrada da Fila
**PUT** `/api/v1/waitlist/{waitlist_id}`

Atualiza dados da entrada na fila.

**Response:** `200 OK`

---

### 17. Remover da Fila
**DELETE** `/api/v1/waitlist/{waitlist_id}`

Remove paciente da lista de espera.

**Response:** `200 OK`

---

### 18. Notificar Vaga Disponível
**POST** `/api/v1/waitlist/{waitlist_id}/notify?method=whatsapp&available_date=2025-11-10T14:00:00`

Notifica paciente sobre vaga disponível.

**Response:** `200 OK`

---

## ⏰ Escalas de Profissionais

### 19. Criar Escala
**POST** `/api/v1/schedules/`

Define horário de trabalho de um profissional.

**Request Body:**
```json
{
  "healthcare_professional_id": 2,
  "day_of_week": 0,
  "start_time": "08:00",
  "end_time": "18:00",
  "break_start_time": "12:00",
  "break_end_time": "13:00",
  "default_appointment_duration": 30
}
```

**Nota:** `day_of_week`: 0=Segunda, 1=Terça, ..., 6=Domingo

**Response:** `201 Created`

---

### 20. Buscar Escala do Profissional
**GET** `/api/v1/schedules/professional/{professional_id}`

Retorna todas as escalas de um profissional.

**Response:** `200 OK`

---

### 21. Buscar Escala Específica
**GET** `/api/v1/schedules/{schedule_id}`

**Response:** `200 OK`

---

### 22. Atualizar Escala
**PUT** `/api/v1/schedules/{schedule_id}`

Atualiza horários de trabalho.

**Response:** `200 OK`

---

### 23. Remover Escala
**DELETE** `/api/v1/schedules/{schedule_id}`

Remove escala (soft delete).

**Response:** `200 OK`

---

## 🔍 Disponibilidade

### 24. Verificar Horários Disponíveis
**GET** `/api/v1/availability/professional/{professional_id}?date_filter=2025-11-10`

Retorna todos os horários livres de um profissional em uma data específica.

**Response:** `200 OK`
```json
{
  "date": "2025-11-10",
  "professional_id": 2,
  "day_of_week": 6,
  "work_hours": {
    "start": "08:00",
    "end": "18:00",
    "break_start": "12:00",
    "break_end": "13:00"
  },
  "appointment_duration": 30,
  "available_slots": [
    "08:00",
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "14:00",
    "14:30",
    "15:00",
    "16:00",
    "16:30",
    "17:00",
    "17:30"
  ],
  "total_slots": 12
}
```

---

## 🔄 Fluxo Completo de Agendamento

### Status e Transições:

```
1. SCHEDULED (agendado)
   ↓ POST /confirm
2. CONFIRMED (confirmado)
   ↓ POST /check-in
3. (checked_in_at registrado)
   ↓ POST /start
4. IN_PROGRESS (em atendimento)
   ↓ POST /complete
5. COMPLETED (concluído)

Ramificações:
- SCHEDULED/CONFIRMED → POST /cancel → CANCELLED
- SCHEDULED/CONFIRMED → POST /no-show → NO_SHOW
```

---

## 🔔 Tipos de Notificação

### Confirmação de Agendamento
Enviada após criação do agendamento ou via endpoint `/send-confirmation`.

**Conteúdo:**
- Data e hora do agendamento
- Nome do profissional
- Nome da clínica
- Instruções de chegada

### Lembrete (24h antes)
*A ser implementado com sistema de jobs/cron*

### Notificação de Vaga (Lista de Espera)
Enviada quando uma vaga fica disponível para pacientes na fila.

---

## 🛡️ Segurança e Validações

### Validações Automáticas:
- ✅ Verificação de conflito de horários
- ✅ Validação de profissional e paciente existentes
- ✅ Restrições de edição por status
- ✅ Soft delete preserva histórico
- ✅ Multi-tenancy (isolamento por clínica)

### Permissões:
- Requer autenticação JWT
- Todas as operações respeitam `tenant_id` do usuário

---

## 📊 Enums Disponíveis

### AppointmentStatus
- `scheduled` - Agendado
- `confirmed` - Confirmado
- `in_progress` - Em atendimento
- `completed` - Concluído
- `cancelled` - Cancelado
- `no_show` - Falta

### AppointmentType
- `first_time` - Primeira consulta
- `return` - Retorno
- `emergency` - Emergência
- `telemedicine` - Teleconsulta

### ConfirmationMethod
- `whatsapp` - WhatsApp
- `email` - Email
- `sms` - SMS
- `phone` - Telefone
- `none` - Nenhum

### Preferred Period (Lista de Espera)
- `morning` - Manhã
- `afternoon` - Tarde
- `evening` - Noite

### Urgency Level
- `low` - Baixa
- `medium` - Média
- `high` - Alta
- `urgent` - Urgente

---

## 🚀 Próximas Melhorias

- [ ] Sistema de lembretes automáticos (Celery + Redis)
- [ ] Integração real com WhatsApp Business API
- [ ] Integração com SendGrid/AWS SES para emails
- [ ] Webhooks para notificações em tempo real
- [ ] Relatórios de ocupação e faturamento
- [ ] Bloqueio de horários (férias, feriados)
- [ ] Agendamento recorrente
- [ ] Sala de espera virtual

---

## 📝 Notas Importantes

1. **Notificações**: Atualmente em modo simulação. Para produção, configure:
   - WhatsApp: Twilio ou Evolution API
   - Email: SendGrid, AWS SES ou Mailgun
   - SMS: Twilio, AWS SNS ou Zenvia

2. **Horários**: Todos os horários são armazenados em UTC no banco de dados.

3. **Soft Delete**: Registros nunca são removidos permanentemente, apenas marcados como `is_deleted=true`.

4. **Multi-tenancy**: Todas as queries automaticamente filtram por `tenant_id` do usuário autenticado.
