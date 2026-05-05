-- Migration: Create cotacoes table
CREATE TABLE IF NOT EXISTS cotacoes (
    id SERIAL PRIMARY KEY,
    tipo_gado VARCHAR(50) NOT NULL,
    preco_arroba DECIMAL(10, 2) NOT NULL,
    data_referencia DATE NOT NULL,
    fonte VARCHAR(100),
    notas TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_cotacoes_tipo_gado ON cotacoes(tipo_gado);
CREATE INDEX IF NOT EXISTS idx_cotacoes_data_referencia ON cotacoes(data_referencia);
CREATE INDEX IF NOT EXISTS idx_cotacoes_created_at ON cotacoes(created_at);
