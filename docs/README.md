# 📚 Documentação AgroVision

Bem-vindo à documentação completa do **AgroVision**, um sistema inteligente de gestão pecuária com IoT, IA e BI.

## 📋 Índice

1. **[Visão do Produto](01_VISAO_DO_PRODUTO.md)** — O que você está construindo
2. **[Arquitetura Geral](02_ARQUITETURA.md)** — Visão em camadas e fluxo de dados
3. **[Microserviços](03_MICROSERVICES.md)** — Cada serviço em detalhes
4. **[Banco de Dados](04_BANCO_DE_DADOS.md)** — Schema PostgreSQL
5. **[Tecnologia](05_TECNOLOGIA.md)** — Stack completo
6. **[Testes TDD](06_TESTES_TDD.md)** — Metodologia Test-Driven Development
7. **[Docker Setup](07_DOCKER_SETUP.md)** — Containerização
8. **[Integrações](08_INTEGRACIONES.md)** — Balança, Câmera, CEPEA
9. **[Roadmap](09_ROADMAP.md)** — Fases de desenvolvimento

## 🚀 Quick Start

### 1. Clone e setup
```bash
git clone git@github.com:Lucas-dev98/AgroVision.git
cd AgroVision
python -m venv venv
source venv/bin/activate
```

### 2. Banco de dados
```bash
docker-compose up -d postgres
```

### 3. Rodas os serviços
```bash
docker-compose up -d
```

### 4. Acesse
- API Gateway: http://localhost:8000
- Docs: http://localhost:8000/docs
- DB: localhost:5432

## 🧪 Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Específico
pytest tests/test_animal_repository.py -v
```

## 📁 Estrutura de Pastas

```
AgroVision/
├── docs/                          # Este diretório
├── services/
│   ├── animal-service/
│   ├── pesagem-service/
│   ├── alimentacao-service/
│   ├── sanidade-service/
│   ├── cotacao-service/
│   ├── analytics-service/
│   └── api-gateway/
├── shared/                        # Código compartilhado
│   ├── schemas.py
│   ├── converters.py
│   └── database.py
├── infra/
│   └── postgres/
│       └── init.sql
├── docker-compose.yml
└── Makefile
```

## 🔑 Conceitos Principais

### Microserviços
- Cada domínio é um serviço independente
- Compartilham banco de dados (logical isolation)
- Comunicam via HTTP REST

### TDD
- Teste → Implementação → Refactor
- Cobertura mínima 80%
- Fixtures isoladas

### IoT
- Balança: Serial/USB
- RFID: Identificação
- Câmeras IP: Monitoramento com YOLO

### IA e Analytics
- YOLO v8: Detecção de animais
- Pandas: Análise de dados
- ML: Previsões (futuro)

## 📊 Fluxo de Dados

```
Hardware → ingestion-service → serviços → PostgreSQL → analytics-service → Dashboard
```

## 🛠️ Desenvolvimento

### Adicionar novo endpoint

1. Criar teste em `tests/test_endpoints.py`
2. Implementar schema em `app/schemas/`
3. Implementar service em `app/services/`
4. Implementar repository em `app/repositories/`
5. Adicionar endpoint em `app/api/endpoints.py`
6. Rodar testes: `pytest`

### Fazer deploy

1. Commit na branch
2. Push para origin
3. GitHub Actions roda testes
4. Se tudo passar, merge em `main`
5. Tag de release
6. Deploy automático

## 📞 Support

- Dúvidas? Abra uma issue
- Sugestões? Abra um PR
- Documentação desatualizada? Corrija!

## 📄 Licença

MIT - Lucas de Bastos (2026)

---

**Última atualização**: 15 de abril de 2026
