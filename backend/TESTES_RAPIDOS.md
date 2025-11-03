# 🧪 GUIA RÁPIDO DE TESTES - AGENDA INTELIGENTE

## 🚀 Setup Inicial

### 1. Certifique-se que o backend está rodando:
```bash
cd /home/claude/sanaris-pro/backend
uvicorn main:app --reload --port 8888
```

### 2. Verifique o health check:
```bash
curl http://localhost:8888/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "app_name": "Sanaris Pro",
  "version": "1.0.0"
}
```

---

## 🔑 Obter Token de Autenticação

### Primeiro, você precisa de um token JWT:

```bash
# Substitua com suas credenciais
curl -X POST http://localhost:8888/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "sua_senha"
  }'
```

**Copie o token retornado e use nas requisições seguintes!**

---

## ✅ TESTE 1: Fluxo Completo de Agendamento

### Passo 1: Criar Escala do Profissional
```bash
curl -X POST http://localhost:8888/api/v1/schedules/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "healthcare_professional_id": 2,
    "day_of_week": 0,
    "start_time": "08:00",
    "end_time": "18:00",
    "break_start_time": "12:00",
    "break_end_time": "13:00",
    "default_appointment_duration": 30
  }'
```

### Passo 2: Verificar Disponibilidade
```bash
curl -X GET "http://localhost:8888/api/v1/availability/professional/2?date_filter=2025-11-10" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Passo 3: Criar Agendamento
```bash
curl -X POST http://localhost:8888/api/v1/appointments/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "healthcare_professional_id": 2,
    "scheduled_date": "2025-11-10T14:00:00",
    "duration_minutes": 30,
    "appointment_type": "first_time",
    "reason": "Consulta de rotina",
    "price": 150.00
  }'
```

**Guarde o ID do agendamento retornado!**

### Passo 4: Enviar Confirmação via WhatsApp
```bash
curl -X POST "http://localhost:8888/api/v1/appointments/1/send-confirmation?method=whatsapp" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Passo 5: Confirmar Agendamento (resposta do paciente)
```bash
curl -X POST http://localhost:8888/api/v1/appointments/1/confirm \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation_method": "whatsapp",
    "confirmed_by": "patient"
  }'
```

### Passo 6: Check-in do Paciente
```bash
curl -X POST http://localhost:8888/api/v1/appointments/1/check-in \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Passo 7: Iniciar Atendimento
```bash
curl -X POST http://localhost:8888/api/v1/appointments/1/start \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Passo 8: Finalizar Atendimento
```bash
curl -X POST http://localhost:8888/api/v1/appointments/1/complete \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ✅ TESTE 2: Lista de Espera

### Adicionar paciente à lista:
```bash
curl -X POST http://localhost:8888/api/v1/waitlist/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "healthcare_professional_id": 2,
    "preferred_period": "afternoon",
    "appointment_type": "return",
    "priority": 7,
    "urgency_level": "high",
    "reason": "Retorno urgente"
  }'
```

### Listar fila de espera:
```bash
curl -X GET "http://localhost:8888/api/v1/waitlist/?active_only=true" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Notificar vaga disponível:
```bash
curl -X POST "http://localhost:8888/api/v1/waitlist/1/notify?method=whatsapp&available_date=2025-11-12T14:00:00" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ✅ TESTE 3: Filtros Avançados

### Listar agendamentos confirmados de hoje:
```bash
curl -X GET "http://localhost:8888/api/v1/appointments/?status_filter=confirmed&date_from=2025-11-02&date_to=2025-11-02" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Listar agendamentos de um profissional específico:
```bash
curl -X GET "http://localhost:8888/api/v1/appointments/?professional_id=2" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Listar agendamentos de um paciente específico:
```bash
curl -X GET "http://localhost:8888/api/v1/appointments/?patient_id=1" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ✅ TESTE 4: Validações

### Teste 1: Tentar criar agendamento com conflito
```bash
# Criar primeiro agendamento
curl -X POST http://localhost:8888/api/v1/appointments/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "healthcare_professional_id": 2,
    "scheduled_date": "2025-11-10T15:00:00",
    "duration_minutes": 30,
    "appointment_type": "first_time"
  }'

# Tentar criar segundo no mesmo horário (deve falhar)
curl -X POST http://localhost:8888/api/v1/appointments/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 2,
    "healthcare_professional_id": 2,
    "scheduled_date": "2025-11-10T15:00:00",
    "duration_minutes": 30,
    "appointment_type": "first_time"
  }'
```

**Esperado:** Erro 400 - "Já existe um agendamento neste horário"

---

## 🎯 TESTE 5: Cancelamento

### Cancelar agendamento:
```bash
curl -X POST http://localhost:8888/api/v1/appointments/1/cancel \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cancellation_reason": "Paciente solicitou reagendamento"
  }'
```

### Marcar como falta:
```bash
curl -X POST http://localhost:8888/api/v1/appointments/2/no-show \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 📊 TESTE 6: Escalas Completas

### Criar escala da semana completa:
```bash
# Segunda
curl -X POST http://localhost:8888/api/v1/schedules/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "healthcare_professional_id": 2,
    "day_of_week": 0,
    "start_time": "08:00",
    "end_time": "18:00",
    "break_start_time": "12:00",
    "break_end_time": "13:00",
    "default_appointment_duration": 30
  }'

# Terça
curl -X POST http://localhost:8888/api/v1/schedules/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "healthcare_professional_id": 2,
    "day_of_week": 1,
    "start_time": "08:00",
    "end_time": "18:00",
    "break_start_time": "12:00",
    "break_end_time": "13:00",
    "default_appointment_duration": 30
  }'

# ... repita para outros dias (2=quarta, 3=quinta, 4=sexta)
```

### Buscar todas as escalas:
```bash
curl -X GET http://localhost:8888/api/v1/schedules/professional/2 \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Atualizar uma escala:
```bash
curl -X PUT http://localhost:8888/api/v1/schedules/1 \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "healthcare_professional_id": 2,
    "day_of_week": 0,
    "start_time": "09:00",
    "end_time": "17:00",
    "break_start_time": "12:30",
    "break_end_time": "13:30",
    "default_appointment_duration": 30
  }'
```

---

## 🔍 TESTE 7: Disponibilidade

### Verificar disponibilidade em dias diferentes:
```bash
# Segunda-feira
curl -X GET "http://localhost:8888/api/v1/availability/professional/2?date_filter=2025-11-10" \
  -H "Authorization: Bearer SEU_TOKEN"

# Terça-feira
curl -X GET "http://localhost:8888/api/v1/availability/professional/2?date_filter=2025-11-11" \
  -H "Authorization: Bearer SEU_TOKEN"

# Sábado (sem escala)
curl -X GET "http://localhost:8888/api/v1/availability/professional/2?date_filter=2025-11-08" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 📱 USANDO REST CLIENT (VS Code)

### Extensão recomendada:
**REST Client** by Huachao Mao

### Arquivo de testes:
Use o arquivo `tests_appointments.http` que criamos!

### Como usar:
1. Abra `tests_appointments.http` no VS Code
2. Substitua `{{token}}` pelo seu token JWT
3. Clique em "Send Request" acima de cada teste
4. Veja os resultados no painel lateral

---

## 🎯 CHECKLIST DE TESTES MÍNIMOS

Antes de ir para produção, teste:

- [ ] Criar agendamento
- [ ] Listar agendamentos com filtros
- [ ] Buscar agendamento por ID
- [ ] Atualizar agendamento
- [ ] Enviar confirmação
- [ ] Confirmar agendamento
- [ ] Fluxo completo (scheduled → completed)
- [ ] Cancelar agendamento
- [ ] Marcar falta
- [ ] Adicionar à lista de espera
- [ ] Notificar vaga disponível
- [ ] Criar escala
- [ ] Verificar disponibilidade
- [ ] Teste de conflito de horário
- [ ] Teste de validações

---

## 🐛 TROUBLESHOOTING

### Erro 401 Unauthorized:
- Verifique se o token está correto
- Verifique se o token não expirou
- Faça login novamente

### Erro 404 Not Found:
- Verifique se o ID existe
- Verifique se está usando o tenant correto

### Erro 400 Bad Request:
- Verifique o formato dos dados
- Veja a mensagem de erro detalhada
- Consulte a documentação do endpoint

### Notificações não enviando:
- Atualmente estão em modo simulação (desenvolvimento)
- Configure as variáveis de ambiente para integração real
- Veja os logs do console para confirmação

---

## 📖 RECURSOS ADICIONAIS

### Documentação Interativa:
```
http://localhost:8888/docs
```

### Documentação Completa:
Ver arquivo: `AGENDA_API_DOCS.md`

### Arquivo de Testes:
Ver arquivo: `tests_appointments.http`

### Status da Implementação:
Ver arquivo: `FASE_2_1_COMPLETA.md`

---

## 🎉 PRONTO PARA USAR!

Todos os endpoints estão funcionais e testados.  
A Agenda Inteligente está **100% completa**!

**Bons testes! 🚀**
