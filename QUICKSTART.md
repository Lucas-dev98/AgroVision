# 🚀 COMECE AQUI - Guia Rápido

## 3 Passos para Começar

### 1️⃣ Setup Ambiente (2 min)

```bash
cd boi
cp .env.example .env
make install
make db-up
```

### 2️⃣ Rodar Testes (1 min)

```bash
make test
# ou
make test-animal
make test-converter
```

### 3️⃣ Rodar App (1 min)

```bash
make run
# Acesse: http://localhost:8001/docs
```

---

## 📊 Status: O Que Está Pronto?

### ✅ Implementado (Pronto para Usar)

- [x] Estrutura completa de pastas
- [x] Docker Compose (PostgreSQL, MongoDB, Redis, MinIO)
- [x] SQLAlchemy ORM Models (Animals)
- [x] Animal Repository (50+ testes)
- [x] Converters (20+ testes)
- [x] Fixtures Pytest
- [x] Documentação TDD
- [x] FastAPI app scaffold

### 🟡 Em Desenvolvimento (Este Sprint)

- [ ] Endpoints FastAPI para Animal CRUD
- [ ] Integração tests com banco real
- [ ] Health Service inicial

### 🟤 Próximos (Próximos Sprints)

- [ ] Weighing Service (integração balança)
- [ ] Vision Service (YOLO)
- [ ] Market Service (CEPEA)
- [ ] Frontend Dashboard

---

## 🧑‍💻 Workflow TDD

### Adicione Novo Teste (RED)

```python
# services/animal-service/test_animal_repository.py
def test_novo_recurso(animal_repository):
    """Escrever teste que falha"""
    result = animal_repository.novo_metodo()
    assert result == esperado
```

### Rode Teste (Vê Falhar)

```bash
make test-animal
# ❌ FAILED - método não existe
```

### Implemente Código (GREEN)

```python
# services/animal-service/repository.py
def novo_metodo(self):
    return self.db.query(AnimalModel).all()
```

### Rode Teste (Passa)

```bash
make test-animal
# ✅ PASSED
```

### Refatore se Necessário (REFACTOR)

```python
# Melhorar documentação, adicionar validações, otimizar...
```

---

## 📚 Estrutura Arquivo

```
boi/
├── Makefile                 ← Comandos principais
├── README.md               ← Documentação completa
├── PLANEJAMENTO.md         ← Arquitetura e requisitos
├── QUICKSTART.md           ← VOCÊ ESTÁ AQUI
│
├── shared/
│   ├── schemas.py          ← DTOs (Pydantic)
│   ├── database.py         ← Config SQLAlchemy
│   ├── converters.py       ← Conversões kg ↔ arroba
│   └── test_converters.py  ← Testes converters (TDD)
│
├── services/animal-service/
│   ├── models.py           ← SQLAlchemy ORM
│   ├── repository.py       ← Data access layer
│   ├── conftest.py         ← Fixtures pytest
│   ├── test_animal_repository.py  ← Testes (TDD)
│   ├── app.py              ← FastAPI app
│   └── main.py             ← Run server
│
├── docker-compose.yml      ← Infraestrutura
└── infra/postgres/init.sql ← Schema DB
```

---

## 🐛 Comandos Úteis

```bash
# Testes
make test              # Todos
make test-animal       # Animal Service
make test-coverage     # Com relatório

# Banco de Dados
make db-up             # Iniciar
make db-down           # Parar
make db-reset          # Reset completo

# Desenvolvimento
make run               # Rodar app
make clean             # Limpar cache

# Setup completo
make setup             # install + db-up
```

---

## 💡 TDD em Nutshell

```
1. 🔴 RED:    Escreva teste que falha
2. 🟢 GREEN:  Escreva código para passar
3. 🔵 REFACTOR: Melhore sem quebrar testes

Repita infinitamente ♾️
```

---

## 🔗 Próximo?

Após confirm que `make test` passa com ✅:

1. Leia [PLANEJAMENTO.md](PLANEJAMENTO.md) - Arquitetura completa
2. Implemente endpoints FastAPI em Animal Service
3. Crie testes de integração
4. Implemente Weighing Service

---

**Tempo Estimado para Setup**: 10 min ⏱️

**Pronto? Execute**: `make setup && make test` 🚀
