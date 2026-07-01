package models

import (
	"errors"
	"strings"
	"time"
)

var (
	ErrPropertyIDRequired = errors.New("property_id is required")
	ErrAnimalIDRequired   = errors.New("animal_id is required")
	ErrFeedTypeRequired   = errors.New("feed_type is required")
	ErrQuantityInvalid    = errors.New("quantity_kg must be greater than zero")
	ErrRecordNotFound     = errors.New("nutrition record not found")
)

type NutritionRecord struct {
	ID         string    `json:"id"`
	PropertyID string    `json:"property_id"`
	AnimalID   string    `json:"animal_id,omitempty"`
	FeedType   string    `json:"feed_type"`
	QuantityKg float64   `json:"quantity_kg"`
	MealTime   time.Time `json:"meal_time"`
	Notes      string    `json:"notes,omitempty"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  time.Time `json:"updated_at"`
}

type CreateNutritionRequest struct {
	PropertyID string    `json:"property_id"`
	AnimalID   string    `json:"animal_id,omitempty"`
	FeedType   string    `json:"feed_type"`
	QuantityKg float64   `json:"quantity_kg"`
	MealTime   time.Time `json:"meal_time"`
	Notes      string    `json:"notes,omitempty"`
}

type UpdateNutritionRequest struct {
	FeedType   string    `json:"feed_type"`
	QuantityKg float64   `json:"quantity_kg"`
	MealTime   time.Time `json:"meal_time"`
	Notes      string    `json:"notes,omitempty"`
}

func (r CreateNutritionRequest) Validate() error {
	if strings.TrimSpace(r.PropertyID) == "" {
		return ErrPropertyIDRequired
	}
	if strings.TrimSpace(r.FeedType) == "" {
		return ErrFeedTypeRequired
	}
	if r.QuantityKg <= 0 {
		return ErrQuantityInvalid
	}
	return nil
}

func (r UpdateNutritionRequest) Validate() error {
	if strings.TrimSpace(r.FeedType) == "" {
		return ErrFeedTypeRequired
	}
	if r.QuantityKg <= 0 {
		return ErrQuantityInvalid
	}
	return nil
}
