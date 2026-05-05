package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/agrovision/pesagem-service/internal/models"
)

type PesagemRepository interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Pesagem, error)
	GetByID(ctx context.Context, id int) (*models.Pesagem, error)
	GetByAnimalID(ctx context.Context, animalID int) ([]models.Pesagem, error)
	GetLatestByAnimalID(ctx context.Context, animalID int) (*models.Pesagem, error)
	Create(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error)
	Update(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type pesagemRepository struct {
	db *sql.DB
}

func NewPesagemRepository(db *sql.DB) PesagemRepository {
	return &pesagemRepository{db: db}
}

func (r *pesagemRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Pesagem, error) {
	query := `
		SELECT id, animal_id, peso_kg, data_pesagem, responsavel_id, observacoes, created_at, updated_at
		FROM pesagens
		ORDER BY data_pesagem DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pesagens []models.Pesagem
	for rows.Next() {
		var pesagem models.Pesagem
		err := rows.Scan(
			&pesagem.ID, &pesagem.AnimalID, &pesagem.PesoKg, &pesagem.DataPesagem,
			&pesagem.ResponsavelID, &pesagem.Observacoes, &pesagem.CreatedAt, &pesagem.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		pesagens = append(pesagens, pesagem)
	}

	return pesagens, rows.Err()
}

func (r *pesagemRepository) GetByID(ctx context.Context, id int) (*models.Pesagem, error) {
	query := `
		SELECT id, animal_id, peso_kg, data_pesagem, responsavel_id, observacoes, created_at, updated_at
		FROM pesagens
		WHERE id = $1
	`

	var pesagem models.Pesagem
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&pesagem.ID, &pesagem.AnimalID, &pesagem.PesoKg, &pesagem.DataPesagem,
		&pesagem.ResponsavelID, &pesagem.Observacoes, &pesagem.CreatedAt, &pesagem.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &pesagem, nil
}

func (r *pesagemRepository) GetByAnimalID(ctx context.Context, animalID int) ([]models.Pesagem, error) {
	query := `
		SELECT id, animal_id, peso_kg, data_pesagem, responsavel_id, observacoes, created_at, updated_at
		FROM pesagens
		WHERE animal_id = $1
		ORDER BY data_pesagem DESC
	`

	rows, err := r.db.QueryContext(ctx, query, animalID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pesagens []models.Pesagem
	for rows.Next() {
		var pesagem models.Pesagem
		err := rows.Scan(
			&pesagem.ID, &pesagem.AnimalID, &pesagem.PesoKg, &pesagem.DataPesagem,
			&pesagem.ResponsavelID, &pesagem.Observacoes, &pesagem.CreatedAt, &pesagem.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		pesagens = append(pesagens, pesagem)
	}

	return pesagens, rows.Err()
}

func (r *pesagemRepository) GetLatestByAnimalID(ctx context.Context, animalID int) (*models.Pesagem, error) {
	query := `
		SELECT id, animal_id, peso_kg, data_pesagem, responsavel_id, observacoes, created_at, updated_at
		FROM pesagens
		WHERE animal_id = $1
		ORDER BY data_pesagem DESC
		LIMIT 1
	`

	var pesagem models.Pesagem
	err := r.db.QueryRowContext(ctx, query, animalID).Scan(
		&pesagem.ID, &pesagem.AnimalID, &pesagem.PesoKg, &pesagem.DataPesagem,
		&pesagem.ResponsavelID, &pesagem.Observacoes, &pesagem.CreatedAt, &pesagem.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &pesagem, nil
}

func (r *pesagemRepository) Create(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error) {
	query := `
		INSERT INTO pesagens (animal_id, peso_kg, data_pesagem, responsavel_id, observacoes, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
		RETURNING id, created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		pesagem.AnimalID, pesagem.PesoKg, pesagem.DataPesagem, pesagem.ResponsavelID, pesagem.Observacoes,
	).Scan(&pesagem.ID, &pesagem.CreatedAt, &pesagem.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return pesagem, nil
}

func (r *pesagemRepository) Update(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error) {
	query := `
		UPDATE pesagens
		SET peso_kg = COALESCE($1, peso_kg),
		    observacoes = COALESCE($2, observacoes),
		    updated_at = NOW()
		WHERE id = $3
		RETURNING id, peso_kg, observacoes, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		pesagem.PesoKg, pesagem.Observacoes, pesagem.ID,
	).Scan(&pesagem.ID, &pesagem.PesoKg, &pesagem.Observacoes, &pesagem.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return pesagem, nil
}

func (r *pesagemRepository) Delete(ctx context.Context, id int) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM pesagens WHERE id = $1", id)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return fmt.Errorf("pesagem not found")
	}

	return nil
}

func (r *pesagemRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM pesagens").Scan(&count)
	return count, err
}
