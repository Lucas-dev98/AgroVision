# 🗄️ Banco de Dados (PostgreSQL)

Um único banco, separado **logicamente** por domínio.

## Schema

### 🐂 Tabela: animais

```sql
CREATE TABLE animais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    raca VARCHAR(50),
    data_nascimento DATE,
    rfid VARCHAR(50) UNIQUE,
    lote_id INTEGER REFERENCES lotes(id),
    status VARCHAR(20) DEFAULT 'ativo' CHECK (status IN ('ativo', 'vendido', 'falecido')),
    peso_inicial DECIMAL(10, 2),
    data_entrada DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_animais_rfid ON animais(rfid);
CREATE INDEX idx_animais_lote ON animais(lote_id);
```

### 👥 Tabela: lotes

```sql
CREATE TABLE lotes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_criacao DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### ⚖️ Tabela: pesagens

```sql
CREATE TABLE pesagens (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id),
    peso_kg DECIMAL(10, 2) NOT NULL,
    peso_arroba DECIMAL(10, 2) GENERATED ALWAYS AS (peso_kg / 15) STORED,
    data DATE NOT NULL,
    hora TIME,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pesagens_animal ON pesagens(animal_id);
CREATE INDEX idx_pesagens_data ON pesagens(data);
```

### 🍽️ Tabela: alimentacao

```sql
CREATE TABLE alimentacao (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id),
    tempo_inicio TIMESTAMP,
    tempo_fim TIMESTAMP,
    duracao_minutos INTEGER GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (tempo_fim - tempo_inicio))/60) STORED,
    data DATE NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alimentacao_animal ON alimentacao(animal_id);
CREATE INDEX idx_alimentacao_data ON alimentacao(data);
```

### 💉 Tabela: vacinas

```sql
CREATE TABLE vacinas (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id),
    tipo_vacina VARCHAR(100) NOT NULL,
    data_aplicacao DATE NOT NULL,
    proxima_dose DATE,
    veterinario VARCHAR(100),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vacinas_animal ON vacinas(animal_id);
CREATE INDEX idx_vacinas_proxima_dose ON vacinas(proxima_dose);
```

### 💰 Tabela: cotacao_arroba

```sql
CREATE TABLE cotacao_arroba (
    id SERIAL PRIMARY KEY,
    preco DECIMAL(10, 2) NOT NULL,
    data_referencia DATE UNIQUE NOT NULL,
    fonte VARCHAR(50) DEFAULT 'CEPEA',
    variacao DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cotacao_data ON cotacao_arroba(data_referencia);
```

### ⚠️ Tabela: alertas

```sql
CREATE TABLE alertas (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id),
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('saude', 'ganho', 'alimentacao', 'cotacao')),
    mensagem TEXT NOT NULL,
    severidade VARCHAR(20) DEFAULT 'info' CHECK (severidade IN ('info', 'warning', 'critical')),
    lido BOOLEAN DEFAULT FALSE,
    data_alerta TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alertas_animal ON alertas(animal_id);
CREATE INDEX idx_alertas_data ON alertas(data_alerta);
```

## Relacionamentos

```
animais ──┬── pesagens
          ├── alimentacao
          ├── vacinas
          └── alertas

lotes ─── animais

cotacao_arroba (sem FK)
```

## Queries Comuns

### Ganho de peso por animal
```sql
SELECT 
    a.id,
    a.nome,
    p1.peso_kg AS peso_inicial,
    p2.peso_kg AS peso_final,
    (p2.peso_kg - p1.peso_kg) AS ganho_kg
FROM animais a
JOIN pesagens p1 ON a.id = p1.animal_id AND p1.data = CURRENT_DATE - INTERVAL '30 days'
JOIN pesagens p2 ON a.id = p2.animal_id AND p2.data = CURRENT_DATE
ORDER BY ganho_kg DESC;
```

### Valor total do rebanho
```sql
SELECT 
    SUM((p.peso_kg / 15) * c.preco) AS valor_total
FROM animais a
JOIN pesagens p ON a.id = p.animal_id AND p.data = CURRENT_DATE
JOIN cotacao_arroba c ON c.data_referencia = CURRENT_DATE
WHERE a.status = 'ativo';
```

### Próximas vacinas faltando
```sql
SELECT 
    a.id,
    a.nome,
    v.tipo_vacina,
    v.proxima_dose
FROM animais a
JOIN vacinas v ON a.id = v.animal_id
WHERE v.proxima_dose <= CURRENT_DATE + INTERVAL '7 days'
AND a.status = 'ativo'
ORDER BY v.proxima_dose;
```

### Tempo no cocho por animal (hoje)
```sql
SELECT 
    animal_id,
    SUM(duracao_minutos) AS total_minutos,
    COUNT(*) AS num_visitas
FROM alimentacao
WHERE data = CURRENT_DATE
GROUP BY animal_id
ORDER BY total_minutos DESC;
```
