# 🛣️ Roadmap - Fases de Desenvolvimento

## 🔹 Fase 1: Fundação (Semanas 1-2)

**Objetivo**: Estrutura base do projeto

### Tasks
- [x] Criar repositório GitHub
- [ ] Subir PostgreSQL com schema
- [ ] Criar animal-service base
- [ ] Criar pesagem-service base
- [ ] Implementar TDD básico
- [ ] Docker Compose rodando

### Entregas
✅ Estrutura de microserviços pronta
✅ Testes básicos rodando
✅ Banco de dados funcional
✅ Docker Compose levantando todos os serviços

### Commits
```
[WIP] Fase 1: Fundação
- Setup animal-service
- Setup pesagem-service
- Schema PostgreSQL criado
- Docker Compose funcionando
```

---

## 🔹 Fase 2: Core Pesagem (Semanas 3-4)

**Objetivo**: Sistema de pesagem funcional

### Tasks
- [ ] Implementar leitura da balança (mock)
- [ ] Calcular arroba
- [ ] Endpoints de pesagem
- [ ] Validações
- [ ] Testes unitários 90%+
- [ ] Integrar com animal-service

### Funcionalidades
```
POST /pesagens
{
  "animal_id": 10,
  "peso_kg": 450
}

Response:
{
  "id": 1,
  "animal_id": 10,
  "peso_kg": 450,
  "peso_arroba": 30,
  "data": "2026-04-15",
  "hora": "10:30:00"
}
```

### Entregas
✅ Pesagem funcionando
✅ Cálculos precisos
✅ Histórico salvo
✅ API documentada

---

## 🔹 Fase 3: Cotação (Semanas 5-6)

**Objetivo**: Integração com CEPEA

### Tasks
- [ ] Scraper do CEPEA
- [ ] Job diário (Celery/APScheduler)
- [ ] Histórico de cotações
- [ ] Cálculo de valor (KB × arroba)
- [ ] Dashboard de valor

### Funcionalidades
```
GET /cotacao/atual
{
  "preco": 280.50,
  "data": "2026-04-15",
  "fonte": "CEPEA"
}

GET /cotacao/valor-rebanho
{
  "valor_total": 45000,
  "num_animais": 50,
  "valor_medio": 900
}
```

### Entregas
✅ Cotações atualizadas diariamente
✅ Valor do rebanho calculado
✅ Histórico disponível
✅ Alertas de variação

---

## 🔹 Fase 4: Monitoramento Alimentar (Semanas 7-8)

**Objetivo**: Câmeras + IA

### Tasks
- [ ] Integração RTSP
- [ ] YOLO v8 modelo
- [ ] Detecção de vacas
- [ ] Detecção no cocho
- [ ] Tempo de alimentação

### Funcionalidades
```
POST /alimentacao
{
  "animal_id": 10,
  "tempo_inicio": "2026-04-15T08:00:00Z",
  "tempo_fim": "2026-04-15T08:15:00Z"
}

GET /alimentacao/animal/{id}/dia
{
  "animal_id": 10,
  "total_minutos": 120,
  "num_visitas": 4
}
```

### Entregas
✅ Câmera capturando dados
✅ IA detectando corretamente
✅ Tempo de cocho registrado
✅ Alertas de não-alimentação

---

## 🔹 Fase 5: Saúde e Vacinas (Semanas 9-10)

**Objetivo**: Gerenciamento sanitário

### Tasks
- [ ] CRUD de vacinas
- [ ] Alertas de próxima dose
- [ ] Histórico de doenças
- [ ] Isolamento de animais

### Funcionalidades
```
POST /vacinas
{
  "animal_id": 10,
  "tipo_vacina": "Raiva",
  "data_aplicacao": "2026-04-15",
  "proxima_dose": "2027-04-15"
}

GET /vacinas/alertas
[
  {
    "animal_id": 10,
    "tipo_vacina": "Aftosa",
    "proxima_dose": "2026-05-15",
    "dias_restantes": 30
  }
]
```

### Entregas
✅ Controle de vacinas
✅ Alertas funcionando
✅ Histórico completo
✅ Zero missed doses

---

## 🔹 Fase 6: Analytics e BI (Semanas 11-12)

**Objetivo**: Dashboard inteligente

### Tasks
- [ ] KPIs do rebanho
- [ ] Ganho de peso
- [ ] Eficiência alimentar
- [ ] Valor total
- [ ] Alertas inteligentes

### Endpoints
```
GET /analytics/rebanho
{
  "ganho_medio": 1.2,
  "valor_total": 45000,
  "saude_score": 95,
  "alimentacao_score": 88
}

GET /analytics/alertas
[
  {
    "tipo": "saude",
    "animal_id": 10,
    "mensagem": "Próxima dose de aftosa vence em 5 dias"
  },
  {
    "tipo": "ganho",
    "animal_id": 15,
    "mensagem": "Ganho negativo nos últimos 7 dias"
  }
]
```

### Entregas
✅ Dashboard funcional
✅ KPIs em tempo real
✅ Alertas inteligentes
✅ Exportar relatórios

---

## 🔹 Fase 7: Frontend (Semanas 13-16)

**Objetivo**: Interface do usuário

### Stack
- React 18
- TypeScript
- Recharts (gráficos)
- Tailwind CSS

### Páginas
- Dashboard principal
- Detalhes do animal
- Histórico de pesagens
- Cotações
- Alertas
- Configurações

### Entregas
✅ UI responsiva
✅ Gráficos em tempo real
✅ PWA (offline)
✅ Mobile-first

---

## 🔹 Fase 8: DevOps e Produção (Semanas 17-18)

**Objetivo**: Pronto para produção

### Tasks
- [ ] CI/CD com GitHub Actions
- [ ] Testes automatizados em PRs
- [ ] Coverage mínimo 80%
- [ ] Deploy automatizado
- [ ] Monitoramento (Prometheus/Grafana)
- [ ] Logs (ELK Stack)
- [ ] Backup automático

### Entregas
✅ Deploy automático
✅ Zero downtime updates
✅ Monitoramento full-stack
✅ Alertas de problemas
✅ Rollback automático

---

## 📊 Timeline Estimada

```
Fase 1: ████ (2 semanas)
Fase 2: ████ (2 semanas)
Fase 3: ████ (2 semanas)
Fase 4: ████ (2 semanas)
Fase 5: ████ (2 semanas)
Fase 6: ████ (2 semanas)
Fase 7: ████████ (4 semanas)
Fase 8: ████ (2 semanas)

Total: ~18 semanas (4.5 meses)
```

## 🎯 Marcos Críticos

| Marco | Fase | Semana | Status |
|-------|------|--------|--------|
| MVP Pesagem | 1-2 | 4 | Planejado |
| Cotação Funcionando | 3 | 6 | Planejado |
| IA Detectando | 4 | 8 | Planejado |
| Dashboard Beta | 6 | 12 | Planejado |
| Frontend Launch | 7 | 16 | Planejado |
| Produção | 8 | 18 | Planejado |

## 🚀 Como Executar

A cada fim de fase:
1. Fazer merge na `main`
2. Tag de release (`v0.1.0`, `v0.2.0`, etc.)
3. Deploy para staging
4. Testes E2E
5. Release notes

## 💡 Adaptações

- Risco de delay: +2 semanas
- Se houver pivot: Replanejar
- Features podem ser reordenadas
- Feedback de usuário é prioridade
