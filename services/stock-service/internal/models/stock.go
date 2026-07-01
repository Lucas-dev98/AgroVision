package models

import (
	"errors"
	"strings"
	"time"
)

type StockItem struct {
	ID              string     `json:"id"`
	PropertyID      string     `json:"property_id"`
	ItemName        string     `json:"item_name"`
	Category        string     `json:"category"`
	Quantity        float64    `json:"quantity"`
	Unit            string     `json:"unit"`
	MinimumQuantity float64    `json:"minimum_quantity"`
	ExpiryDate      *time.Time `json:"expiry_date,omitempty"`
	CreatedAt       time.Time  `json:"created_at"`
	UpdatedAt       time.Time  `json:"updated_at"`
}

type CreateStockRequest struct {
	PropertyID      string     `json:"property_id"`
	ItemName        string     `json:"item_name"`
	Category        string     `json:"category"`
	Quantity        float64    `json:"quantity"`
	Unit            string     `json:"unit"`
	MinimumQuantity float64    `json:"minimum_quantity"`
	ExpiryDate      *time.Time `json:"expiry_date,omitempty"`
}

type UpdateStockRequest struct {
	ItemName        string     `json:"item_name"`
	Category        string     `json:"category"`
	Quantity        float64    `json:"quantity"`
	Unit            string     `json:"unit"`
	MinimumQuantity float64    `json:"minimum_quantity"`
	ExpiryDate      *time.Time `json:"expiry_date,omitempty"`
}

var (
	ErrPropertyIDRequired = errors.New("property_id is required")
	ErrItemNameRequired   = errors.New("item_name is required")
	ErrUnitRequired       = errors.New("unit is required")
	ErrInvalidQuantity    = errors.New("quantity must be greater than or equal to 0")
	ErrInvalidMinimum     = errors.New("minimum_quantity must be greater than or equal to 0")
	ErrStockNotFound      = errors.New("stock item not found")
)

func (r *CreateStockRequest) Validate() error {
	r.PropertyID = strings.TrimSpace(r.PropertyID)
	r.ItemName = strings.TrimSpace(r.ItemName)
	r.Unit = strings.TrimSpace(r.Unit)
	r.Category = strings.TrimSpace(r.Category)

	if r.PropertyID == "" {
		return ErrPropertyIDRequired
	}
	if r.ItemName == "" {
		return ErrItemNameRequired
	}
	if r.Unit == "" {
		return ErrUnitRequired
	}
	if r.Quantity < 0 {
		return ErrInvalidQuantity
	}
	if r.MinimumQuantity < 0 {
		return ErrInvalidMinimum
	}
	return nil
}

func (r *UpdateStockRequest) Validate() error {
	r.ItemName = strings.TrimSpace(r.ItemName)
	r.Unit = strings.TrimSpace(r.Unit)
	r.Category = strings.TrimSpace(r.Category)

	if r.ItemName == "" {
		return ErrItemNameRequired
	}
	if r.Unit == "" {
		return ErrUnitRequired
	}
	if r.Quantity < 0 {
		return ErrInvalidQuantity
	}
	if r.MinimumQuantity < 0 {
		return ErrInvalidMinimum
	}
	return nil
}
