package models

import (
	"errors"
	"strings"
	"time"
)

type Production struct {
	ID           string    `json:"id"`
	PlotID       string    `json:"plot_id"`
	HarvestDate  time.Time `json:"harvest_date"`
	QuantityKg   float64   `json:"quantity_kg"`
	QualityGrade string    `json:"quality_grade"`
	Notes        string    `json:"notes"`
	CreatedAt    time.Time `json:"created_at"`
}

type CreateProductionRequest struct {
	PlotID       string    `json:"plot_id"`
	HarvestDate  time.Time `json:"harvest_date"`
	QuantityKg   float64   `json:"quantity_kg"`
	QualityGrade string    `json:"quality_grade"`
	Notes        string    `json:"notes"`
}

type UpdateProductionRequest struct {
	HarvestDate  time.Time `json:"harvest_date"`
	QuantityKg   float64   `json:"quantity_kg"`
	QualityGrade string    `json:"quality_grade"`
	Notes        string    `json:"notes"`
}

var (
	ErrPlotIDRequired         = errors.New("plot_id is required")
	ErrHarvestDateRequired    = errors.New("harvest date is required")
	ErrQuantityMustBePositive = errors.New("quantity_kg must be greater than 0")
	ErrProductionNotFound     = errors.New("production not found")
)

func (r *CreateProductionRequest) Validate() error {
	r.PlotID = strings.TrimSpace(r.PlotID)
	if r.PlotID == "" {
		return ErrPlotIDRequired
	}
	if r.HarvestDate.IsZero() {
		return ErrHarvestDateRequired
	}
	if r.QuantityKg <= 0 {
		return ErrQuantityMustBePositive
	}
	return nil
}

func (r *UpdateProductionRequest) Validate() error {
	if r.HarvestDate.IsZero() {
		return ErrHarvestDateRequired
	}
	if r.QuantityKg <= 0 {
		return ErrQuantityMustBePositive
	}
	return nil
}
