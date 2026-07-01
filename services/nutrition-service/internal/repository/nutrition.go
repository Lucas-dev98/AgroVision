package repository

import (
	"context"
	"sort"
	"sync"
	"time"

	"github.com/agrovision/nutrition-service/internal/models"
	"github.com/google/uuid"
)

type NutritionRepository struct {
	mu      sync.RWMutex
	records map[string]*models.NutritionRecord
}

func NewNutritionRepository() *NutritionRepository {
	return &NutritionRepository{records: make(map[string]*models.NutritionRecord)}
}

func (r *NutritionRepository) Create(_ context.Context, record *models.NutritionRecord) error {
	now := time.Now().UTC()
	record.ID = uuid.NewString()
	record.CreatedAt = now
	record.UpdatedAt = now

	r.mu.Lock()
	r.records[record.ID] = cloneRecord(record)
	r.mu.Unlock()
	return nil
}

func (r *NutritionRepository) ListByPropertyID(_ context.Context, propertyID string) ([]*models.NutritionRecord, error) {
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

func (r *NutritionRepository) ListByAnimalID(_ context.Context, animalID, propertyID string) ([]*models.NutritionRecord, error) {
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

func (r *NutritionRepository) GetByID(_ context.Context, id string) (*models.NutritionRecord, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	rec, ok := r.records[id]
	if !ok {
		return nil, models.ErrRecordNotFound
	}

	return cloneRecord(rec), nil
}

func (r *NutritionRepository) Update(_ context.Context, record *models.NutritionRecord) error {
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

func (r *NutritionRepository) Delete(_ context.Context, id string) error {
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
