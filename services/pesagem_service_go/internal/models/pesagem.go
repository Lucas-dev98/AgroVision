package models

import "time"

type Pesagem struct {
	ID             int       `json:"id" db:"id"`
	AnimalID       int       `json:"animal_id" db:"animal_id"`
	PesoKg         float64   `json:"peso_kg" db:"peso_kg"`
	DataPesagem    time.Time `json:"data_pesagem" db:"data_pesagem"`
	ResponsavelID  *int      `json:"responsavel_id" db:"responsavel_id"`
	Observacoes    *string   `json:"observacoes" db:"observacoes"`
	CreatedAt      time.Time `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time `json:"updated_at" db:"updated_at"`
}

type CreatePesagemRequest struct {
	AnimalID    int       `json:"animal_id" binding:"required"`
	PesoKg      float64   `json:"peso_kg" binding:"required"`
	DataPesagem time.Time `json:"data_pesagem" binding:"required"`
	Observacoes *string   `json:"observacoes"`
}

type UpdatePesagemRequest struct {
	PesoKg      *float64 `json:"peso_kg"`
	Observacoes *string  `json:"observacoes"`
}
