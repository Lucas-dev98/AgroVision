-- Migration: Create pesagens table
CREATE TABLE IF NOT EXISTS pesagens (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    peso_kg DECIMAL(10, 2) NOT NULL,
    data_pesagem TIMESTAMP NOT NULL,
    responsavel_id INTEGER,
    observacoes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_pesagens_animal_id ON pesagens(animal_id);
CREATE INDEX IF NOT EXISTS idx_pesagens_data_pesagem ON pesagens(data_pesagem);
CREATE INDEX IF NOT EXISTS idx_pesagens_created_at ON pesagens(created_at);
