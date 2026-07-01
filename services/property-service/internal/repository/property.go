package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/property-service/internal/models"
	"github.com/google/uuid"
)

type PropertyRepository struct {
	db    *sql.DB
	mu    sync.RWMutex
	items map[string]models.Property
}

func NewPropertyRepository(db *sql.DB) *PropertyRepository {
	return &PropertyRepository{
		db:    db,
		items: make(map[string]models.Property),
	}
}

func (r *PropertyRepository) Create(ctx context.Context, prop *models.Property) error {
	if r.db == nil {
		return r.createInMemory(prop)
	}

	prop.ID = uuid.NewString()

	const query = `
		INSERT INTO properties (id, user_id, name, total_area, planted_area, location_lat, location_lng, soil_type)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		prop.ID,
		prop.UserID,
		prop.Name,
		prop.TotalArea,
		prop.PlantedArea,
		prop.LocationLat,
		prop.LocationLng,
		prop.SoilType,
	).Scan(&prop.CreatedAt, &prop.UpdatedAt)
	if err != nil {
		return fmt.Errorf("create property: %w", err)
	}

	return nil
}

func (r *PropertyRepository) GetByID(ctx context.Context, id string) (*models.Property, error) {
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

	const query = `
		SELECT id, user_id, name, total_area, planted_area, location_lat, location_lng, soil_type, created_at, updated_at
		FROM properties
		WHERE id = $1
	`

	var prop models.Property
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&prop.ID,
		&prop.UserID,
		&prop.Name,
		&prop.TotalArea,
		&prop.PlantedArea,
		&prop.LocationLat,
		&prop.LocationLng,
		&prop.SoilType,
		&prop.CreatedAt,
		&prop.UpdatedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrPropertyNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get property by id: %w", err)
	}

	return &prop, nil
}

func (r *PropertyRepository) ListByUserID(ctx context.Context, userID string) ([]models.Property, error) {
	if r.db == nil {
		return r.listByUserIDInMemory(userID), nil
	}

	const query = `
		SELECT id, user_id, name, total_area, planted_area, location_lat, location_lng, soil_type, created_at, updated_at
		FROM properties
		WHERE user_id = $1
		ORDER BY created_at DESC
	`

	rows, err := r.db.QueryContext(ctx, query, userID)
	if err != nil {
		return nil, fmt.Errorf("list properties by user_id: %w", err)
	}
	defer rows.Close()

	properties := make([]models.Property, 0)
	for rows.Next() {
		var prop models.Property
		err = rows.Scan(
			&prop.ID,
			&prop.UserID,
			&prop.Name,
			&prop.TotalArea,
			&prop.PlantedArea,
			&prop.LocationLat,
			&prop.LocationLng,
			&prop.SoilType,
			&prop.CreatedAt,
			&prop.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan property row: %w", err)
		}
		properties = append(properties, prop)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate property rows: %w", err)
	}

	return properties, nil
}

func (r *PropertyRepository) Update(ctx context.Context, prop *models.Property) error {
	if r.db == nil {
		return r.updateInMemory(prop)
	}

	const query = `
		UPDATE properties
		SET name = $1,
			total_area = $2,
			planted_area = $3,
			location_lat = $4,
			location_lng = $5,
			soil_type = $6,
			updated_at = NOW()
		WHERE id = $7
		RETURNING updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		prop.Name,
		prop.TotalArea,
		prop.PlantedArea,
		prop.LocationLat,
		prop.LocationLng,
		prop.SoilType,
		prop.ID,
	).Scan(&prop.UpdatedAt)
	if err == sql.ErrNoRows {
		return models.ErrPropertyNotFound
	}
	if err != nil {
		return fmt.Errorf("update property: %w", err)
	}

	return nil
}

func (r *PropertyRepository) Delete(ctx context.Context, id string) error {
	if r.db == nil {
		return r.deleteInMemory(id)
	}

	const query = `DELETE FROM properties WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete property: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on delete: %w", err)
	}
	if rows == 0 {
		return models.ErrPropertyNotFound
	}

	return nil
}

func (r *PropertyRepository) createInMemory(prop *models.Property) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	now := time.Now().UTC()
	prop.ID = uuid.NewString()
	prop.CreatedAt = now
	prop.UpdatedAt = now
	r.items[prop.ID] = *prop
	return nil
}

func (r *PropertyRepository) getByIDInMemory(id string) (*models.Property, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	prop, ok := r.items[id]
	if !ok {
		return nil, models.ErrPropertyNotFound
	}
	copy := prop
	return &copy, nil
}

func (r *PropertyRepository) listByUserIDInMemory(userID string) []models.Property {
	r.mu.RLock()
	defer r.mu.RUnlock()

	properties := make([]models.Property, 0)
	for _, item := range r.items {
		if item.UserID == userID {
			properties = append(properties, item)
		}
	}

	sort.Slice(properties, func(i, j int) bool {
		return properties[i].CreatedAt.After(properties[j].CreatedAt)
	})

	return properties
}

func (r *PropertyRepository) updateInMemory(prop *models.Property) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	existing, ok := r.items[prop.ID]
	if !ok {
		return models.ErrPropertyNotFound
	}

	prop.UserID = existing.UserID
	prop.CreatedAt = existing.CreatedAt
	prop.UpdatedAt = time.Now().UTC()
	r.items[prop.ID] = *prop
	return nil
}

func (r *PropertyRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.items[id]; !ok {
		return models.ErrPropertyNotFound
	}

	delete(r.items, id)
	return nil
}
