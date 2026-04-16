# PostgreSQL Migrations com Alembic

## 📋 Estrutura de Migrações

```
infra/
├── alembic/
│   ├── env.py           # Configuração do Alembic
│   ├── script.py.mako   # Template de migration
│   └── versions/        # Histórico de migrations
│       └── 001_initial_schema.py
├── alembic.ini          # Configuração do Alembic
├── postgres/
│   └── init.sql         # Schema manual (backup)
└── test_migrations.py   # Script de teste
```

## 🚀 Usando Migrations

### Configurar DATABASE_URL

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/agrovision"
```

### 📤 Upgrade (Aplicar Migrations)

Aplicar todas as migrations pendentes:
```bash
alembic upgrade head
```

Aplicar uma migration específica:
```bash
alembic upgrade +1
```

### 📥 Downgrade (Reverter Migrations)

Reverter última migration:
```bash
alembic downgrade -1
```

Reverter para versão específica:
```bash
alembic downgrade 001_initial_schema
```

### 📝 Criar Nova Migration

Criar migration automática (requer modelos no app):
```bash
alembic revision --autogenerate -m "Descrição da mudança"
```

Criar migration manual:
```bash
alembic revision -m "Descrição da mudança"
```

### 📋 Ver Histórico

```bash
alembic history
```

Ver current version:
```bash
alembic current
```

### 🧪 Testar Migrations

```bash
python infra/test_migrations.py
```

## 🗄️ Tabelas do Schema

1. **animais** - Registro de animais (gado)
   - id, rfid (unique), nome, raca, data_nascimento, status
   - Índices: rfid, status

2. **lotes** - Grupos de animais
   - id, nome, descricao, data_inicio, data_fim, status
   
3. **pesagens** - Registro de pesagens
   - id, animal_id (FK), peso_kg, peso_arroba (calculated), data, observacoes
   - Índices: animal_id, data

4. **alimentacao** - Consumo de alimento
   - id, animal_id (FK), tipo_alimento, quantidade_kg, data_ali mento
   - Índices: animal_id

5. **vacinas** - Registro de vacinação
   - id, animal_id (FK), nome_vacina, data_aplicacao, proxima_dose, veterinario
   - Índices: animal_id

6. **cotacoes** - Preços de arroba
   - id, preco_arroba, data_referencia
   - Índices: data_referencia, preco_arroba

## ⚙️ Configuração do env.py

O arquivo `env.py` lê a variável de ambiente `DATABASE_URL`:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agrovision:agrovision@localhost/agrovision")
```

## 🔄 Workflow Típico

1. **Desenvolvimento**: Usar SQLite (conftest.py)
2. **Testes**: Rodar migrations no banco de teste
3. **Produção**: Rodar migrations antes de deploy

```bash
# Antes de fazer deploy
alembic upgrade head  # Aplica todas as migrations

# Se algo der errado
alembic downgrade -1  # Volta uma version
```

## 📊 Dados de Teste (init.sql)

O arquivo `init.sql` contém:
- 3 animais de teste (Touro A, Vaca B, Bezerro C)
- 3 cotações de teste

Execute nele manualmente:
```bash
psql -U postgres -d agrovision -f infra/postgres/init.sql
```

Ou dentro do container:
```bash
docker exec agrovision-db psql -U agrovision -d agrovision -f /docker-entrypoint-initdb.d/init.sql
```

## 🐛 Troubleshooting

### "target_metadata could not be imported"
Certifique-se que `env.py` consegue importar `from app.models import Base`

### "no such table"
Rode `alembic upgrade head` para criar as tabelas

### "Connection refused"
Verifique se o PostgreSQL está rodando:
```bash
psql -U postgres -c "SELECT version();"
```

## 📚 Referências

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
