package models

import (
	"time"
)

type Animal struct {
	ID             int        `json:"id" db:"id"`
	EarTag         *string    `json:"ear_tag" db:"ear_tag"`
	Name           string     `json:"name" db:"name"`
	Breed          string     `json:"breed" db:"breed"`
	BirthDate      *time.Time `json:"birth_date" db:"birth_date"`
	Gender         string     `json:"gender" db:"gender"`
	Status         string     `json:"status" db:"status"`
	MotherID       *int       `json:"mother_id" db:"mother_id"`
	FatherID       *int       `json:"father_id" db:"father_id"`
	DetectedByYOLO bool       `json:"detected_by_yolo" db:"detected_by_yolo"`
	Notes          *string    `json:"notes" db:"notes"`
	CreatedAt      time.Time  `json:"created_at" db:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at" db:"updated_at"`
}

type CreateAnimalRequest struct {
	EarTag         *string `json:"ear_tag" binding:"omitempty,max=20"`
	Name           string  `json:"name" binding:"required,max=100"`
	Breed          string  `json:"breed" binding:"required,max=50"`
	BirthDate      *string `json:"birth_date" binding:"omitempty"`
	Gender         string  `json:"gender" binding:"required,oneof=M F"`
	Status         *string `json:"status" binding:"omitempty,oneof=ATIVO VENDIDO FALECIDO"`
	MotherID       *int    `json:"mother_id" binding:"omitempty"`
	FatherID       *int    `json:"father_id" binding:"omitempty"`
	DetectedByYOLO *bool   `json:"detected_by_yolo" binding:"omitempty"`
	Notes          *string `json:"notes" binding:"omitempty"`
}

type UpdateAnimalRequest struct {
	Name   *string `json:"name" binding:"omitempty,max=100"`
	Status *string `json:"status" binding:"omitempty,oneof=ATIVO VENDIDO FALECIDO"`
	Notes  *string `json:"notes" binding:"omitempty"`
}
