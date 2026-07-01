package models

import (
	"errors"
	"strings"
	"time"
)

type WeatherAlert struct {
	ID                string     `json:"id"`
	PropertyID        string     `json:"property_id"`
	AlertType         string     `json:"alert_type"`
	Severity          string     `json:"severity"`
	Description       string     `json:"description"`
	RecommendedAction string     `json:"recommended_action"`
	CreatedAt         time.Time  `json:"created_at"`
	ResolvedAt        *time.Time `json:"resolved_at,omitempty"`
}

type CreateWeatherAlertRequest struct {
	PropertyID        string `json:"property_id"`
	AlertType         string `json:"alert_type"`
	Severity          string `json:"severity"`
	Description       string `json:"description"`
	RecommendedAction string `json:"recommended_action"`
}

type UpdateWeatherAlertRequest struct {
	AlertType         string     `json:"alert_type"`
	Severity          string     `json:"severity"`
	Description       string     `json:"description"`
	RecommendedAction string     `json:"recommended_action"`
	ResolvedAt        *time.Time `json:"resolved_at,omitempty"`
}

var (
	ErrPropertyIDRequired = errors.New("property_id is required")
	ErrAlertTypeRequired  = errors.New("alert_type is required")
	ErrSeverityRequired   = errors.New("severity is required")
	ErrInvalidSeverity    = errors.New("severity must be one of: low, medium, high")
	ErrAlertNotFound      = errors.New("weather alert not found")
)

func (r *CreateWeatherAlertRequest) Validate() error {
	r.PropertyID = strings.TrimSpace(r.PropertyID)
	r.AlertType = strings.TrimSpace(r.AlertType)
	r.Severity = strings.TrimSpace(strings.ToLower(r.Severity))
	r.Description = strings.TrimSpace(r.Description)
	r.RecommendedAction = strings.TrimSpace(r.RecommendedAction)

	if r.PropertyID == "" {
		return ErrPropertyIDRequired
	}
	if r.AlertType == "" {
		return ErrAlertTypeRequired
	}
	if r.Severity == "" {
		return ErrSeverityRequired
	}
	if !isValidSeverity(r.Severity) {
		return ErrInvalidSeverity
	}
	return nil
}

func (r *UpdateWeatherAlertRequest) Validate() error {
	r.AlertType = strings.TrimSpace(r.AlertType)
	r.Severity = strings.TrimSpace(strings.ToLower(r.Severity))
	r.Description = strings.TrimSpace(r.Description)
	r.RecommendedAction = strings.TrimSpace(r.RecommendedAction)

	if r.AlertType == "" {
		return ErrAlertTypeRequired
	}
	if r.Severity == "" {
		return ErrSeverityRequired
	}
	if !isValidSeverity(r.Severity) {
		return ErrInvalidSeverity
	}
	return nil
}

func isValidSeverity(value string) bool {
	switch value {
	case "low", "medium", "high":
		return true
	default:
		return false
	}
}
