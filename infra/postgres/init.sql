-- Tabela de Animais (cattle registry)
CREATE TABLE IF NOT EXISTS animais (
    id SERIAL PRIMARY KEY,
    rfid VARCHAR(50) UNIQUE,
    nome VARCHAR(100) NOT NULL,
    raca VARCHAR(50) NOT NULL,
    data_nascimento DATE,
    status VARCHAR(20) DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'VENDIDO', 'FALECIDO')),
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Lotes (cattle batches)
CREATE TABLE IF NOT EXISTS lotes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    status VARCHAR(20) DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'FINALIZADO', 'CANCELADO')),
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Pesagens (cattle weighings)
CREATE TABLE IF NOT EXISTS pesagens (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    peso_kg DECIMAL(8, 2) NOT NULL,
    peso_arroba DECIMAL(8, 2) GENERATED ALWAYS AS (peso_kg / 15) STORED,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Alimentação
CREATE TABLE IF NOT EXISTS alimentacao (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    tipo_alimento VARCHAR(100) NOT NULL,
    quantidade_kg DECIMAL(8, 2) NOT NULL,
    data_alimento DATE NOT NULL,
    observacoes TEXT,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Vacinação/Sanidade
CREATE TABLE IF NOT EXISTS vacinas (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animais(id) ON DELETE CASCADE,
    nome_vacina VARCHAR(100) NOT NULL,
    data_aplicacao DATE NOT NULL,
    proxima_dose DATE,
    veterinario VARCHAR(100),
    observacoes TEXT,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Cotações (cattle pricing)
CREATE TABLE IF NOT EXISTS cotacoes (
    id SERIAL PRIMARY KEY,
    preco_arroba DECIMAL(8, 2) NOT NULL,
    data_referencia DATE NOT NULL,
    criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_animais_rfid ON animais(rfid);
CREATE INDEX IF NOT EXISTS idx_animais_status ON animais(status);
CREATE INDEX IF NOT EXISTS idx_pesagens_animal_id ON pesagens(animal_id);
CREATE INDEX IF NOT EXISTS idx_pesagens_data ON pesagens(data);
CREATE INDEX IF NOT EXISTS idx_alimentacao_animal_id ON alimentacao(animal_id);
CREATE INDEX IF NOT EXISTS idx_vacinas_animal_id ON vacinas(animal_id);
CREATE INDEX IF NOT EXISTS idx_cotacoes_data ON cotacoes(data_referencia);
CREATE INDEX IF NOT EXISTS idx_cotacoes_preco ON cotacoes(preco_arroba);

-- Dados de teste
INSERT INTO animais (rfid, nome, raca, data_nascimento, status)
VALUES 
    ('RF001', 'Touro A', 'Nelore', '2023-01-15', 'ATIVO'),
    ('RF002', 'Vaca B', 'Brahman', '2022-06-20', 'ATIVO'),
    ('RF003', 'Bezerro C', 'Guzerá', '2024-03-10', 'ATIVO')
ON CONFLICT (rfid) DO NOTHING;

INSERT INTO cotacoes (preco_arroba, data_referencia)
VALUES 
    (250.50, '2026-04-15'),
    (248.75, '2026-04-14'),
    (252.00, '2026-04-13')
ON CONFLICT DO NOTHING;
