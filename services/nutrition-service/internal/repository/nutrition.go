package repository

import (
	"context"
	"database/sql"
	"fmt"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/nutrition-service/internal/models"
	"github.com/google/uuid"
)

type NutritionRepository struct {
	db      *sql.DB
	mu      sync.RWMutex
	records map[string]*models.NutritionRecord
}

func NewNutritionRepository(db *sql.DB) *NutritionRepository {
	return &NutritionRepository{db: db, records: make(map[string]*models.NutritionRecord)}
}

func EnsureSchema(ctx context.Context, db *sql.DB) error {
	if db == nil {
		return nil
	}

	const ddl = `
		CREATE TABLE IF NOT EXISTS nutrition_records (
			id VARCHAR(36) PRIMARY KEY,
			property_id VARCHAR(100) NOT NULL,
			animal_id VARCHAR(100) NOT NULL,
			feed_type VARCHAR(100) NOT NULL,
			quantity_kg NUMERIC(12,3) NOT NULL,
			meal_time TIMESTAMP NOT NULL,
			notes TEXT,
			created_at TIMESTAMP NOT NULL DEFAULT NOW(),
			updated_at TIMESTAMP NOT NULL DEFAULT NOW()
		);

		CREATE INDEX IF NOT EXISTS idx_nutrition_records_property_id ON nutrition_records(property_id);
		CREATE INDEX IF NOT EXISTS idx_nutrition_records_animal_id ON nutrition_records(animal_id);
		CREATE INDEX IF NOT EXISTS idx_nutrition_records_meal_time ON nutrition_records(meal_time);
	`

	if _, err := db.ExecContext(ctx, ddl); err != nil {
		return fmt.Errorf("ensure nutrition schema: %w", err)
	}

	return nil
}

func (r *NutritionRepository) Create(ctx context.Context, record *models.NutritionRecord) error {
	if r.db == nil {
		return r.createInMemory(record)
	}

	record.ID = uuid.NewString()

	const query = `
		INSERT INTO nutrition_records (id, property_id, animal_id, feed_type, quantity_kg, meal_time, notes)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		record.ID,
		record.PropertyID,
		record.AnimalID,
		record.FeedType,
		record.QuantityKg,
		record.MealTime,
		record.Notes,
	).Scan(&record.CreatedAt, &record.UpdatedAt)
	if err != nil {
		return fmt.Errorf("create nutrition record: %w", err)
	}

	return nil
}

func (r *NutritionRepository) createInMemory(record *models.NutritionRecord) error {
	now := time.Now().UTC()
	record.ID = uuid.NewString()
	record.CreatedAt = now
	record.UpdatedAt = now

	r.mu.Lock()
	r.records[record.ID] = cloneRecord(record)
	r.mu.Unlock()
	return nil
}

func (r *NutritionRepository) ListByPropertyID(ctx context.Context, propertyID string) ([]*models.NutritionRecord, error) {
	if r.db == nil {
		return r.listByPropertyIDInMemory(propertyID)
	}

	const query = `
		SELECT id, property_id, animal_id, feed_type, quantity_kg, meal_time, notes, created_at, updated_at
		FROM nutrition_records
		WHERE property_id = $1
		ORDER BY meal_time DESC
	`

	rows, err := r.db.QueryContext(ctx, query, propertyID)
	if err != nil {
		return nil, fmt.Errorf("list nutrition by property_id: %w", err)
	}
	defer rows.Close()

	records := make([]*models.NutritionRecord, 0)
	for rows.Next() {
		var rec models.NutritionRecord
		err = rows.Scan(
			&rec.ID,
			&rec.PropertyID,
			&rec.AnimalID,
			&rec.FeedType,
			&rec.QuantityKg,
			&rec.MealTime,
			&rec.Notes,
			&rec.CreatedAt,
			&rec.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan nutrition row: %w", err)
		}
		records = append(records, &rec)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate nutrition rows: %w", err)
	}

	return records, nil
}

func (r *NutritionRepository) listByPropertyIDInMemory(propertyID string) ([]*models.NutritionRecord, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	result := make([]*models.NutritionRecord, 0)
	for _, rec := range r.records {
		if rec.PropertyID == propertyID {
			result = append(result, cloneRecord(rec))
		}
	}

	sort.Slice(result, func(i, j int) bool {
		return result[i].MealTime.After(result[j].MealTime)
	})

	return result, nil
}

func (r *NutritionRepository) ListByAnimalID(ctx context.Context, animalID, propertyID string) ([]*models.NutritionRecord, error) {
	if r.db == nil {
		return r.listByAnimalIDInMemory(animalID, propertyID)
	}

	query := `
		SELECT id, property_id, animal_id, feed_type, quantity_kg, meal_time, notes, created_at, updated_at
		FROM nutrition_records
		WHERE animal_id = $1
	`
	args := []any{animalID}
	if propertyID != "" {
		query += ` AND property_id = $2`
		args = append(args, propertyID)
	}
	query += ` ORDER BY meal_time DESC`

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("list nutrition by animal_id: %w", err)
	}
	defer rows.Close()

	records := make([]*models.NutritionRecord, 0)
	for rows.Next() {
		var rec models.NutritionRecord
		err = rows.Scan(
			&rec.ID,
			&rec.PropertyID,
			&rec.AnimalID,
			&rec.FeedType,
			&rec.QuantityKg,
			&rec.MealTime,
			&rec.Notes,
			&rec.CreatedAt,
			&rec.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan nutrition row by animal: %w", err)
		}
		records = append(records, &rec)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate nutrition rows by animal: %w", err)
	}

	return records, nil
}

func (r *NutritionRepository) listByAnimalIDInMemory(animalID, propertyID string) ([]*models.NutritionRecord, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	result := make([]*models.NutritionRecord, 0)
	for _, rec := range r.records {
		if rec.AnimalID != animalID {
			continue
		}
		if propertyID != "" && rec.PropertyID != propertyID {
			continue
		}
		result = append(result, cloneRecord(rec))
	}

	sort.Slice(result, func(i, j int) bool {
		return result[i].MealTime.After(result[j].MealTime)
	})

	return result, nil
}

func (r *NutritionRepository) DailySummary(ctx context.Context, propertyID, animalID string, date time.Time) (*models.DailyNutritionSummary, error) {
	if r.db == nil {
		return r.dailySummaryInMemory(propertyID, animalID, date), nil
	}

	query := `
		SELECT id, property_id, animal_id, feed_type, quantity_kg, meal_time, notes, created_at, updated_at
		FROM nutrition_records
		WHERE property_id = $1
		  AND meal_time >= $2
		  AND meal_time < $3
	`
	start := time.Date(date.UTC().Year(), date.UTC().Month(), date.UTC().Day(), 0, 0, 0, 0, time.UTC)
	end := start.Add(24 * time.Hour)
	args := []any{propertyID, start, end}
	if animalID != "" {
		query += ` AND animal_id = $4`
		args = append(args, animalID)
	}

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("daily nutrition summary query: %w", err)
	}
	defer rows.Close()

	summary := &models.DailyNutritionSummary{
		Date:       date.UTC().Format("2006-01-02"),
		PropertyID: propertyID,
		AnimalID:   animalID,
		ByFeedType: make(map[string]float64),
		ByAnimal:   make(map[string]float64),
	}

	for rows.Next() {
		var rec models.NutritionRecord
		err = rows.Scan(
			&rec.ID,
			&rec.PropertyID,
			&rec.AnimalID,
			&rec.FeedType,
			&rec.QuantityKg,
			&rec.MealTime,
			&rec.Notes,
			&rec.CreatedAt,
			&rec.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scan daily nutrition summary row: %w", err)
		}

		summary.RecordsCount++
		summary.TotalQuantityKg += rec.QuantityKg
		summary.ByFeedType[rec.FeedType] += rec.QuantityKg
		if animalID == "" {
			summary.ByAnimal[rec.AnimalID] += rec.QuantityKg
		}
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterate daily nutrition summary rows: %w", err)
	}

	if animalID != "" {
		summary.ByAnimal = nil
	}

	return summary, nil
}

func (r *NutritionRepository) dailySummaryInMemory(propertyID, animalID string, date time.Time) *models.DailyNutritionSummary {
	r.mu.RLock()
	defer r.mu.RUnlock()

	summary := &models.DailyNutritionSummary{
		Date:       date.UTC().Format("2006-01-02"),
		PropertyID: propertyID,
		AnimalID:   animalID,
		ByFeedType: make(map[string]float64),
		ByAnimal:   make(map[string]float64),
	}

	for _, rec := range r.records {
		if rec.PropertyID != propertyID {
			continue
		}
		if animalID != "" && rec.AnimalID != animalID {
			continue
		}
		if !sameDayUTC(rec.MealTime, date) {
			continue
		}

		summary.RecordsCount++
		summary.TotalQuantityKg += rec.QuantityKg
		summary.ByFeedType[rec.FeedType] += rec.QuantityKg
		if animalID == "" {
			summary.ByAnimal[rec.AnimalID] += rec.QuantityKg
		}
	}

	if animalID != "" {
		summary.ByAnimal = nil
	}

	return summary
}

func (r *NutritionRepository) GetByID(ctx context.Context, id string) (*models.NutritionRecord, error) {
	if r.db == nil {
		return r.getByIDInMemory(id)
	}

	const query = `
		SELECT id, property_id, animal_id, feed_type, quantity_kg, meal_time, notes, created_at, updated_at
		FROM nutrition_records
		WHERE id = $1
	`

	var rec models.NutritionRecord
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&rec.ID,
		&rec.PropertyID,
		&rec.AnimalID,
		&rec.FeedType,
		&rec.QuantityKg,
		&rec.MealTime,
		&rec.Notes,
		&rec.CreatedAt,
		&rec.UpdatedAt,
	)
	if err == sql.ErrNoRows {
		return nil, models.ErrRecordNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("get nutrition by id: %w", err)
	}

	return &rec, nil
}

func (r *NutritionRepository) getByIDInMemory(id string) (*models.NutritionRecord, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	rec, ok := r.records[id]
	if !ok {
		return nil, models.ErrRecordNotFound
	}

	return cloneRecord(rec), nil
}

func (r *NutritionRepository) Update(ctx context.Context, record *models.NutritionRecord) error {
	if r.db == nil {
		return r.updateInMemory(record)
	}

	const query = `
		UPDATE nutrition_records
		SET feed_type = $1,
		    quantity_kg = $2,
		    meal_time = $3,
		    notes = $4,
		    updated_at = NOW()
		WHERE id = $5
		RETURNING created_at, updated_at
	`

	err := r.db.QueryRowContext(ctx, query,
		record.FeedType,
		record.QuantityKg,
		record.MealTime,
		record.Notes,
		record.ID,
	).Scan(&record.CreatedAt, &record.UpdatedAt)
	if err == sql.ErrNoRows {
		return models.ErrRecordNotFound
	}
	if err != nil {
		return fmt.Errorf("update nutrition record: %w", err)
	}

	return nil
}

func (r *NutritionRepository) updateInMemory(record *models.NutritionRecord) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	stored, ok := r.records[record.ID]
	if !ok {
		return models.ErrRecordNotFound
	}

	record.CreatedAt = stored.CreatedAt
	record.UpdatedAt = time.Now().UTC()
	r.records[record.ID] = cloneRecord(record)
	return nil
}

func (r *NutritionRepository) Delete(ctx context.Context, id string) error {
	if r.db == nil {
		return r.deleteInMemory(id)
	}

	const query = `DELETE FROM nutrition_records WHERE id = $1`

	result, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("delete nutrition record: %w", err)
	}

	rows, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("rows affected on nutrition delete: %w", err)
	}
	if rows == 0 {
		return models.ErrRecordNotFound
	}

	return nil
}

func (r *NutritionRepository) deleteInMemory(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, ok := r.records[id]; !ok {
		return models.ErrRecordNotFound
	}

	delete(r.records, id)
	return nil
}

func cloneRecord(src *models.NutritionRecord) *models.NutritionRecord {
	if src == nil {
		return nil
	}
	dst := *src
	return &dst
}

func sameDayUTC(a, b time.Time) bool {
	au := a.UTC()
	bu := b.UTC()
	return au.Year() == bu.Year() && au.Month() == bu.Month() && au.Day() == bu.Day()
}
