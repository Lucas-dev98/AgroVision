package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/agrovision/cotacao-service/internal/models"
)

type CotacaoRepository interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Cotacao, error)
	GetByID(ctx context.Context, id int) (*models.Cotacao, error)
	GetLatestByTipo(ctx context.Context, tipoGado string) (*models.Cotacao, error)
	GetByTipoAndData(ctx context.Context, tipoGado string, dataReferencia string) ([]models.Cotacao, error)
	Create(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error)
	Update(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type cotacaoRepository struct {
	db *sql.DB
}

func NewCotacaoRepository(db *sql.DB) CotacaoRepository {
	return &cotacaoRepository{db: db}
}

func (r *cotacaoRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Cotacao, error) {
	query := `
		SELECT id, tipo_gado, preco_arroba, data_referencia, fonte, notas, created_at, updated_at
		FROM cotacoes
		ORDER BY data_referencia DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var cotacoes []models.Cotacao
	for rows.Next() {
		var cotacao models.Cotacao
		err := rows.Scan(
			&cotacao.ID, &cotacao.TipoGado, &cotacao.PrecoArroba, &cotacao.DataReferencia,
			&cotacao.Fonte, &cotacao.Notas, &cotacao.CreatedAt, &cotacao.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		cotacoes = append(cotacoes, cotacao)
	}

	return cotacoes, rows.Err()
}

func (r *cotacaoRepository) GetByID(ctx context.Context, id int) (*models.Cotacao, error) {
	query := `
		SELECT id, tipo_gado, preco_arroba, data_referencia, fonte, notas, created_at, updated_at
		FROM cotacoes
		WHERE id = $1
	`

	var cotacao models.Cotacao
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&cotacao.ID, &cotacao.TipoGado, &cotacao.PrecoArroba, &cotacao.DataReferencia,
		&cotacao.Fonte, &cotacao.Notas, &cotacao.CreatedAt, &cotacao.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &cotacao, nil
}

func (r *cotacaoRepository) GetLatestByTipo(ctx context.Context, tipoGado string) (*models.Cotacao, error) {
	query := `
		SELECT id, tipo_gado, preco_arroba, data_referencia, fonte, notas, created_at, updated_at
		FROM cotacoes
		WHERE tipo_gado = $1
		ORDER BY data_referencia DESC
		LIMIT 1
	`

	var cotacao models.Cotacao
	err := r.db.QueryRowContext(ctx, query, tipoGado).Scan(
		&cotacao.ID, &cotacao.TipoGado, &cotacao.PrecoArroba, &cotacao.DataReferencia,
		&cotacao.Fonte, &cotacao.Notas, &cotacao.CreatedAt, &cotacao.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &cotacao, nil
}

func (r *cotacaoRepository) GetByTipoAndData(ctx context.Context, tipoGado string, dataReferencia string) ([]models.Cotacao, error) {
	query := `
		SELECT id, tipo_gado, preco_arroba, data_referencia, fonte, notas, created_at, updated_at
		FROM cotacoes
		WHERE tipo_gado = $1 AND DATE(data_referencia) >= $2
		ORDER BY data_referencia DESC
	`

	rows, err := r.db.QueryContext(ctx, query, tipoGado, dataReferencia)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var cotacoes []models.Cotacao
	for rows.Next() {
		var cotacao models.Cotacao
		err := rows.Scan(
			&cotacao.ID, &cotacao.TipoGado, &cotacao.PrecoArroba, &cotacao.DataReferencia,
			&cotacao.Fonte, &cotacao.Notas, &cotacao.CreatedAt, &cotacao.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		cotacoes = append(cotacoes, cotacao)
	}

	return cotacoes, rows.Err()
}

func (r *cotacaoRepository) Create(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error) {
	query := `
		INSERT INTO cotacoes (tipo_gado, preco_arroba, data_referencia, fonte, notas, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
		RETURNING id, created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		cotacao.TipoGado, cotacao.PrecoArroba, cotacao.DataReferencia, cotacao.Fonte, cotacao.Notas,
	).Scan(&cotacao.ID, &cotacao.CreatedAt, &cotacao.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return cotacao, nil
}

func (r *cotacaoRepository) Update(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error) {
	query := `
		UPDATE cotacoes
		SET preco_arroba = COALESCE($1, preco_arroba),
		    notas = COALESCE($2, notas),
		    updated_at = NOW()
		WHERE id = $3
		RETURNING id, preco_arroba, notas, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		cotacao.PrecoArroba, cotacao.Notas, cotacao.ID,
	).Scan(&cotacao.ID, &cotacao.PrecoArroba, &cotacao.Notas, &cotacao.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return cotacao, nil
}

func (r *cotacaoRepository) Delete(ctx context.Context, id int) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM cotacoes WHERE id = $1", id)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return fmt.Errorf("cotacao not found")
	}

	return nil
}

func (r *cotacaoRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM cotacoes").Scan(&count)
	return count, err
}
