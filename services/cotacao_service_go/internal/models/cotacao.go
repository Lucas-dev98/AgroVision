package models

import "time"

type Cotacao struct {
	ID               int       `json:"id" db:"id"`
	TipoGado         string    `json:"tipo_gado" db:"tipo_gado"`
	PrecoArroba      float64   `json:"preco_arroba" db:"preco_arroba"`
	DataReferencia   time.Time `json:"data_referencia" db:"data_referencia"`
	Fonte            string    `json:"fonte" db:"fonte"`
	Notas            *string   `json:"notas" db:"notas"`
	CreatedAt        time.Time `json:"created_at" db:"created_at"`
	UpdatedAt        time.Time `json:"updated_at" db:"updated_at"`
}

type CreateCotacaoRequest struct {
	TipoGado       string    `json:"tipo_gado" binding:"required"`
	PrecoArroba    float64   `json:"preco_arroba" binding:"required"`
	DataReferencia time.Time `json:"data_referencia" binding:"required"`
	Fonte          string    `json:"fonte" binding:"required"`
	Notas          *string   `json:"notas"`
}

type UpdateCotacaoRequest struct {
	PrecoArroba *float64 `json:"preco_arroba"`
	Notas       *string  `json:"notas"`
}
