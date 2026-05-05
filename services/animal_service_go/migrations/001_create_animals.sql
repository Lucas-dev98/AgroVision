-- Migration: Create animals table
CREATE TABLE IF NOT EXISTS animals (
    id SERIAL PRIMARY KEY,
    ear_tag VARCHAR(20) UNIQUE,
    name VARCHAR(100) NOT NULL,
    breed VARCHAR(50) NOT NULL,
    birth_date DATE,
    gender VARCHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'VENDIDO', 'FALECIDO')),
    mother_id INTEGER REFERENCES animals(id),
    father_id INTEGER REFERENCES animals(id),
    detected_by_yolo BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_animals_ear_tag ON animals(ear_tag);
CREATE INDEX IF NOT EXISTS idx_animals_status ON animals(status);
CREATE INDEX IF NOT EXISTS idx_animals_created_at ON animals(created_at);
CREATE INDEX IF NOT EXISTS idx_animals_gender ON animals(gender);
