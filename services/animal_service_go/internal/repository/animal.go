package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/agrovision/animal-service/internal/models"
)

type AnimalRepository interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Animal, error)
	GetByID(ctx context.Context, id int) (*models.Animal, error)
	GetByEarTag(ctx context.Context, earTag string) (*models.Animal, error)
	Create(ctx context.Context, animal *models.Animal) (*models.Animal, error)
	Update(ctx context.Context, animal *models.Animal) (*models.Animal, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type animalRepository struct {
	db *sql.DB
}

func NewAnimalRepository(db *sql.DB) AnimalRepository {
	return &animalRepository{db: db}
}

func (r *animalRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Animal, error) {
	query := `
		SELECT id, ear_tag, name, breed, birth_date, gender, status, 
		       mother_id, father_id, detected_by_yolo, notes, created_at, updated_at
		FROM animals
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2
	`

	rows, err := r.db.QueryContext(ctx, query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var animals []models.Animal
	for rows.Next() {
		var animal models.Animal
		err := rows.Scan(
			&animal.ID, &animal.EarTag, &animal.Name, &animal.Breed,
			&animal.BirthDate, &animal.Gender, &animal.Status,
			&animal.MotherID, &animal.FatherID, &animal.DetectedByYOLO,
			&animal.Notes, &animal.CreatedAt, &animal.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		animals = append(animals, animal)
	}

	return animals, rows.Err()
}

func (r *animalRepository) GetByID(ctx context.Context, id int) (*models.Animal, error) {
	query := `
		SELECT id, ear_tag, name, breed, birth_date, gender, status,
		       mother_id, father_id, detected_by_yolo, notes, created_at, updated_at
		FROM animals
		WHERE id = $1
	`

	var animal models.Animal
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&animal.ID, &animal.EarTag, &animal.Name, &animal.Breed,
		&animal.BirthDate, &animal.Gender, &animal.Status,
		&animal.MotherID, &animal.FatherID, &animal.DetectedByYOLO,
		&animal.Notes, &animal.CreatedAt, &animal.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &animal, nil
}

func (r *animalRepository) GetByEarTag(ctx context.Context, earTag string) (*models.Animal, error) {
	query := `
		SELECT id, ear_tag, name, breed, birth_date, gender, status,
		       mother_id, father_id, detected_by_yolo, notes, created_at, updated_at
		FROM animals
		WHERE ear_tag = $1
	`

	var animal models.Animal
	err := r.db.QueryRowContext(ctx, query, earTag).Scan(
		&animal.ID, &animal.EarTag, &animal.Name, &animal.Breed,
		&animal.BirthDate, &animal.Gender, &animal.Status,
		&animal.MotherID, &animal.FatherID, &animal.DetectedByYOLO,
		&animal.Notes, &animal.CreatedAt, &animal.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	return &animal, nil
}

func (r *animalRepository) Create(ctx context.Context, animal *models.Animal) (*models.Animal, error) {
	query := `
		INSERT INTO animals (ear_tag, name, breed, birth_date, gender, status, mother_id, father_id, detected_by_yolo, notes, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
		RETURNING id, ear_tag, name, breed, birth_date, gender, status, mother_id, father_id, detected_by_yolo, notes, created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		animal.EarTag, animal.Name, animal.Breed, animal.BirthDate,
		animal.Gender, animal.Status, animal.MotherID, animal.FatherID, animal.DetectedByYOLO, animal.Notes,
	).Scan(&animal.ID, &animal.EarTag, &animal.Name, &animal.Breed, &animal.BirthDate,
		&animal.Gender, &animal.Status, &animal.MotherID, &animal.FatherID, &animal.DetectedByYOLO,
		&animal.Notes, &animal.CreatedAt, &animal.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return animal, nil
}

func (r *animalRepository) Update(ctx context.Context, animal *models.Animal) (*models.Animal, error) {
	query := `
		UPDATE animals
		SET ear_tag = COALESCE($1, ear_tag),
		    name = COALESCE($2, name),
		    breed = COALESCE($3, breed),
		    birth_date = COALESCE($4, birth_date),
		    gender = COALESCE($5, gender),
		    status = COALESCE($6, status),
		    mother_id = COALESCE($7, mother_id),
		    father_id = COALESCE($8, father_id),
		    detected_by_yolo = COALESCE($9, detected_by_yolo),
		    notes = COALESCE($10, notes),
		    updated_at = NOW()
		WHERE id = $11
		RETURNING id, ear_tag, name, breed, birth_date, gender, status, mother_id, father_id, detected_by_yolo, notes, created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		animal.EarTag, animal.Name, animal.Breed, animal.BirthDate,
		animal.Gender, animal.Status, animal.MotherID, animal.FatherID, animal.DetectedByYOLO, animal.Notes, animal.ID,
	).Scan(&animal.ID, &animal.EarTag, &animal.Name, &animal.Breed, &animal.BirthDate,
		&animal.Gender, &animal.Status, &animal.MotherID, &animal.FatherID, &animal.DetectedByYOLO,
		&animal.Notes, &animal.CreatedAt, &animal.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return animal, nil
}

func (r *animalRepository) Delete(ctx context.Context, id int) error {
	result, err := r.db.ExecContext(ctx, "DELETE FROM animals WHERE id = $1", id)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return fmt.Errorf("animal not found")
	}

	return nil
}

func (r *animalRepository) Count(ctx context.Context) (int, error) {
	var count int
	err := r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM animals").Scan(&count)
	return count, err
}
