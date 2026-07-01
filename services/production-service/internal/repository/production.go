package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/production-service/internal/models"
	"github.com/google/uuid"
)

type ProductionRepository struct {
	db    *sql.DB
	mu    sync.RWMutex
	items map[string]models.Production
}

func NewProductionRepository(db *sql.DB) *ProductionRepository {
	return &ProductionRepository{
		db:    db,
		items: make(map[string]models.Production),
	}
}

func (r *ProductionRepository) Create(ctx context.Context, production *models.Production) error {
	if r.db == nil {
		return r.createInMemory(production)
	}

	production.ID = uuid.NewString()

	const query = `
		INSERT INTO production (id, plot_id, harvest_date, quantity_kg, quality_grade, notes)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING created_at
	`

	err := r.db.QueryRowContext(ctx, query,
		production.ID,
		production.PlotID,
		production.HarvestDate,
		production.QuantityKg,
		production.QualityGrade,
		production.Notes,
	).Scan(&production.CreatedAt)
	if err != nil {
		return fmt.Errorf("create production: %w", err)
	}

	return nil
}

func (r *ProductionRepository) GetByID(ctx context.Context, id string) (*models.Production, error) {
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

	const query = `
		SELECT id, plot_id, harvest_date, quantity_kg, quality_grade, notes, created_at
		FROM production
		WHERE id = $1
	`

	var production models.Production
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&production.ID,
		&production.PlotID,
		&production.HarvestDate,
		&production.QuantityKg,
		&production.QualityGrade,
		&production.Notes,
		&production.CreatedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrProductionNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get production by id: %w", err)
	}

	return &production, nil
}

func (r *ProductionRepository) ListByPlotID(ctx context.Context, plotID string) ([]models.Production, error) {
	if r.db == nil {
		return r.listByPlotIDInMemory(plotID), nil
	}

	const query = `
		SELECT id, plot_id, harvest_date, quantity_kg, quality_grade, notes, created_at
		FROM production
		WHERE plot_id = $1
		ORDER BY harvest_date DESC
	`

	rows, err := r.db.QueryContext(ctx, query, plotID)
	if err != nil {
		return nil, fmt.Errorf("list production by plot_id: %w", err)
	}
	defer rows.Close()

	items := make([]models.Production, 0)
	for rows.Next() {
		var production models.Production
		if err := rows.Scan(
			&production.ID,
			&production.PlotID,
			&production.HarvestDate,
			&production.QuantityKg,
			&production.QualityGrade,
			&production.Notes,
			&production.CreatedAt,
		); err != nil {
			return nil, fmt.Errorf("scan production row: %w", err)
		}
		items = append(items, production)
	}

	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate production rows: %w", err)
	}

	return items, nil
}

func (r *ProductionRepository) Update(ctx context.Context, production *models.Production) error {
	if r.db == nil {
		return r.updateInMemory(production)
	}

	const query = `
		UPDATE production
		SET harvest_date = $1,
			quantity_kg = $2,
			quality_grade = $3,
			notes = $4
		WHERE id = $5
	`

	result, err := r.db.ExecContext(ctx, query,
		production.HarvestDate,
		production.QuantityKg,
		production.QualityGrade,
		production.Notes,
		production.ID,
	)
	if err != nil {
		return fmt.Errorf("update production: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on update: %w", err)
	}
	if rows == 0 {
		return models.ErrProductionNotFound
	}

	return nil
}

func (r *ProductionRepository) Delete(ctx context.Context, id string) error {
	if r.db == nil {
		return r.deleteInMemory(id)
	}

	const query = `DELETE FROM production WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete production: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on delete: %w", err)
	}
	if rows == 0 {
		return models.ErrProductionNotFound
	}

	return nil
}

func (r *ProductionRepository) createInMemory(production *models.Production) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	production.ID = uuid.NewString()
	production.CreatedAt = time.Now().UTC()
	r.items[production.ID] = *production
	return nil
}

func (r *ProductionRepository) getByIDInMemory(id string) (*models.Production, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	production, ok := r.items[id]
	if !ok {
		return nil, models.ErrProductionNotFound
	}
	copy := production
	return &copy, nil
}

func (r *ProductionRepository) listByPlotIDInMemory(plotID string) []models.Production {
	r.mu.RLock()
	defer r.mu.RUnlock()

	items := make([]models.Production, 0)
	for _, item := range r.items {
		if item.PlotID == plotID {
			items = append(items, item)
		}
	}

	sort.Slice(items, func(i, j int) bool {
		if items[i].HarvestDate.Equal(items[j].HarvestDate) {
			return items[i].CreatedAt.After(items[j].CreatedAt)
		}
		return items[i].HarvestDate.After(items[j].HarvestDate)
	})

	return items
}

func (r *ProductionRepository) updateInMemory(production *models.Production) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	existing, ok := r.items[production.ID]
	if !ok {
		return models.ErrProductionNotFound
	}

	production.PlotID = existing.PlotID
	production.CreatedAt = existing.CreatedAt
	r.items[production.ID] = *production
	return nil
}

func (r *ProductionRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.items[id]; !ok {
		return models.ErrProductionNotFound
	}

	delete(r.items, id)
	return nil
}
