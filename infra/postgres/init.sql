-- Criar extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
CREATE TYPE animal_status AS ENUM ('active', 'sold', 'dead');
CREATE TYPE animal_gender AS ENUM ('M', 'F');
CREATE TYPE user_role AS ENUM ('admin', 'operator', 'viewer');
CREATE TYPE vaccine_status AS ENUM ('applied', 'pending', 'overdue');

-- Tabela: Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Animals
CREATE TABLE IF NOT EXISTS animals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ear_tag VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    breed VARCHAR(50) NOT NULL,
    birth_date DATE,
    gender animal_gender NOT NULL,
    status animal_status NOT NULL DEFAULT 'active',
    mother_id UUID REFERENCES animals(id) ON DELETE SET NULL,
    father_id UUID REFERENCES animals(id) ON DELETE SET NULL,
    detected_by_yolo BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Weighing Records
CREATE TABLE IF NOT EXISTS weighing_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    weight_kg DECIMAL(8,2) NOT NULL,
    weight_arrobas DECIMAL(8,2) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    recorded_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Vaccines
CREATE TABLE IF NOT EXISTS vaccines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    vaccine_name VARCHAR(100) NOT NULL,
    application_date DATE NOT NULL,
    next_dose_date DATE,
    status vaccine_status DEFAULT 'applied',
    veterinarian VARCHAR(100),
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Feeding Records
CREATE TABLE IF NOT EXISTS feeding_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    feed_type VARCHAR(100) NOT NULL,
    quantity_kg DECIMAL(8,2) NOT NULL,
    fed_at TIMESTAMP NOT NULL,
    recorded_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Cattle Prices (Cotações)
CREATE TABLE IF NOT EXISTS cattle_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50) NOT NULL, -- 'fat_cattle', 'calf', etc
    price_per_arroba DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'BRL',
    date DATE NOT NULL,
    daily_change DECIMAL(5,2),
    monthly_change DECIMAL(5,2),
    price_usd DECIMAL(10,2),
    source VARCHAR(50) NOT NULL DEFAULT 'CEPEA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicator_type, date)
);

-- Tabela: Farm Settings
CREATE TABLE IF NOT EXISTS farm_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_name VARCHAR(100),
    farm_size_alqueiros INT,
    location VARCHAR(100),
    currency_default VARCHAR(3) DEFAULT 'BRL',
    arroba_kg DECIMAL(5,2) DEFAULT 15.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_animals_status ON animals(status);
CREATE INDEX idx_animals_breed ON animals(breed);
CREATE INDEX idx_animals_ear_tag ON animals(ear_tag);
CREATE INDEX idx_weighing_animal_id ON weighing_records(animal_id);
CREATE INDEX idx_weighing_recorded_at ON weighing_records(recorded_at);
CREATE INDEX idx_vaccines_animal_id ON vaccines(animal_id);
CREATE INDEX idx_vaccines_status ON vaccines(status);
CREATE INDEX idx_feeding_animal_id ON feeding_records(animal_id);
CREATE INDEX idx_cattle_prices_date ON cattle_prices(date);
CREATE INDEX idx_cattle_prices_type_date ON cattle_prices(indicator_type, date);

-- Insert initial admin user (password: admin123)
INSERT INTO users (email, name, role, password_hash)
VALUES (
    'admin@boi.local',
    'Administrador',
    'admin',
    '$2b$12$K2W7xjV.Fz1vqZg3V.Z.eO5HvSZh8yQ7z3Q6M9R8T9K2L0N1O2P3'
) ON CONFLICT (email) DO NOTHING;
