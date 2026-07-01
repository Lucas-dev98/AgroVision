-- Migration: 003_unify_go_schema.sql
-- Goal: normalize schema expected by Go microservices

CREATE TABLE IF NOT EXISTS animals (
    id SERIAL PRIMARY KEY,
    ear_tag VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    breed VARCHAR(50) NOT NULL,
    birth_date DATE,
    gender VARCHAR(20) DEFAULT 'unknown',
    status VARCHAR(20) DEFAULT 'active',
    mother_id INTEGER,
    father_id INTEGER,
    detected_by_yolo BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO animals (ear_tag, name, breed, birth_date, status, notes)
SELECT a.rfid, a.nome, a.raca, a.data_nascimento,
       CASE
           WHEN a.status = 'ATIVO' THEN 'active'
           WHEN a.status = 'VENDIDO' THEN 'sold'
           WHEN a.status = 'FALECIDO' THEN 'dead'
           ELSE LOWER(a.status)
       END,
       'migrated from animais'
FROM animais a
WHERE NOT EXISTS (SELECT 1 FROM animals g WHERE g.ear_tag = a.rfid);

ALTER TABLE pesagens ADD COLUMN IF NOT EXISTS data_pesagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE pesagens ADD COLUMN IF NOT EXISTS responsavel_id INTEGER;
ALTER TABLE pesagens ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE pesagens ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

UPDATE pesagens SET data_pesagem = COALESCE(data_pesagem, data);
UPDATE pesagens SET created_at = COALESCE(created_at, criada_em);
UPDATE pesagens SET updated_at = COALESCE(updated_at, atualizada_em);

ALTER TABLE cotacoes ADD COLUMN IF NOT EXISTS tipo_gado VARCHAR(50) DEFAULT 'boi_gordo';
ALTER TABLE cotacoes ADD COLUMN IF NOT EXISTS fonte VARCHAR(100) DEFAULT 'seed';
ALTER TABLE cotacoes ADD COLUMN IF NOT EXISTS notas TEXT;
ALTER TABLE cotacoes ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE cotacoes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

UPDATE cotacoes SET created_at = COALESCE(created_at, criada_em);
UPDATE cotacoes SET updated_at = COALESCE(updated_at, atualizada_em);
