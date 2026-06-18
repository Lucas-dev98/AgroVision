package models

import (
	"errors"
	"strings"
	"time"
)

type Property struct {
	ID          string    `json:"id"`
	UserID      string    `json:"user_id"`
	Name        string    `json:"name"`
	TotalArea   float64   `json:"total_area"`
	PlantedArea float64   `json:"planted_area"`
	LocationLat float64   `json:"location_lat"`
	LocationLng float64   `json:"location_lng"`
	SoilType    string    `json:"soil_type"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type CreatePropertyRequest struct {
	UserID      string  `json:"user_id"`
	Name        string  `json:"name"`
	TotalArea   float64 `json:"total_area"`
	PlantedArea float64 `json:"planted_area"`
	LocationLat float64 `json:"location_lat"`
	LocationLng float64 `json:"location_lng"`
	SoilType    string  `json:"soil_type"`
}

type UpdatePropertyRequest struct {
	Name        string  `json:"name"`
	TotalArea   float64 `json:"total_area"`
	PlantedArea float64 `json:"planted_area"`
	LocationLat float64 `json:"location_lat"`
	LocationLng float64 `json:"location_lng"`
	SoilType    string  `json:"soil_type"`
}

var (
	ErrPropertyNameRequired        = errors.New("property name is required")
	ErrInvalidArea                 = errors.New("total area must be greater than 0")
	ErrPlantedAreaExceedsTotalArea = errors.New("planted area cannot exceed total area")
	ErrUserIDRequired              = errors.New("user_id is required")
	ErrPropertyNotFound            = errors.New("property not found")
)

func (r *CreatePropertyRequest) Validate() error {
	r.Name = strings.TrimSpace(r.Name)
	r.UserID = strings.TrimSpace(r.UserID)

	if r.UserID == "" {
		return ErrUserIDRequired
	}
	if r.Name == "" {
		return ErrPropertyNameRequired
	}
	if r.TotalArea <= 0 {
		return ErrInvalidArea
	}
	if r.PlantedArea < 0 || r.PlantedArea > r.TotalArea {
		return ErrPlantedAreaExceedsTotalArea
	}
	return nil
}

func (r *UpdatePropertyRequest) Validate() error {
	r.Name = strings.TrimSpace(r.Name)
	if r.Name == "" {
		return ErrPropertyNameRequired
	}
	if r.TotalArea <= 0 {
		return ErrInvalidArea
	}
	if r.PlantedArea < 0 || r.PlantedArea > r.TotalArea {
		return ErrPlantedAreaExceedsTotalArea
	}
	return nil
}
