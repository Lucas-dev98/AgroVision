package service

import (
	"context"
	"fmt"
	"time"

	"github.com/agrovision/animal-service/internal/models"
	"github.com/agrovision/animal-service/internal/repository"
	"go.uber.org/zap"
)

type AnimalService interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Animal, error)
	GetByID(ctx context.Context, id int) (*models.Animal, error)
	GetByEarTag(ctx context.Context, earTag string) (*models.Animal, error)
	Create(ctx context.Context, req *models.CreateAnimalRequest) (*models.Animal, error)
	Update(ctx context.Context, id int, req *models.UpdateAnimalRequest) (*models.Animal, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type animalService struct {
	repo   repository.AnimalRepository
	logger *zap.Logger
}

func NewAnimalService(repo repository.AnimalRepository, logger *zap.Logger) AnimalService {
	return &animalService{
		repo:   repo,
		logger: logger,
	}
}

func (s *animalService) GetAll(ctx context.Context, limit, offset int) ([]models.Animal, error) {
	s.logger.Debug("GetAll called", zap.Int("limit", limit), zap.Int("offset", offset))
	return s.repo.GetAll(ctx, limit, offset)
}

func (s *animalService) GetByID(ctx context.Context, id int) (*models.Animal, error) {
	s.logger.Debug("GetByID called", zap.Int("id", id))

	animal, err := s.repo.GetByID(ctx, id)
	if err != nil {
		s.logger.Error("Error getting animal by ID", zap.Int("id", id), zap.Error(err))
		return nil, err
	}

	if animal == nil {
		return nil, fmt.Errorf("animal not found")
	}

	return animal, nil
}

func (s *animalService) GetByEarTag(ctx context.Context, earTag string) (*models.Animal, error) {
	s.logger.Debug("GetByEarTag called", zap.String("earTag", earTag))

	animal, err := s.repo.GetByEarTag(ctx, earTag)
	if err != nil {
		s.logger.Error("Error getting animal by ear tag", zap.String("earTag", earTag), zap.Error(err))
		return nil, err
	}

	if animal == nil {
		return nil, fmt.Errorf("animal not found")
	}

	return animal, nil
}

func (s *animalService) Create(ctx context.Context, req *models.CreateAnimalRequest) (*models.Animal, error) {
	s.logger.Debug("Create called", zap.String("name", req.Name), 
		zap.Any("birth_date_input", req.BirthDate),
		zap.Any("notes_input", req.Notes))

	// Parse birth date if provided
	var birthDate *time.Time
	if req.BirthDate != nil {
		parsed, err := time.Parse("2006-01-02", *req.BirthDate)
		if err != nil {
			s.logger.Warn("Invalid birth date format", zap.String("birthDate", *req.BirthDate), zap.Error(err))
		} else {
			birthDate = &parsed
			s.logger.Debug("Birth date parsed successfully", zap.Time("parsed", parsed))
		}
	}

	// Set default status if not provided
	status := "ATIVO"
	if req.Status != nil {
		status = *req.Status
	}

	// Set detected_by_yolo if provided
	detectedByYOLO := false
	if req.DetectedByYOLO != nil {
		detectedByYOLO = *req.DetectedByYOLO
	}

	animal := &models.Animal{
		EarTag:         req.EarTag,
		Name:           req.Name,
		Breed:          req.Breed,
		BirthDate:      birthDate,
		Gender:         req.Gender,
		Status:         status,
		MotherID:       req.MotherID,
		FatherID:       req.FatherID,
		DetectedByYOLO: detectedByYOLO,
		Notes:          req.Notes,
	}

	s.logger.Debug("Before repo.Create", 
		zap.Any("birth_date_obj", animal.BirthDate),
		zap.Any("notes_obj", animal.Notes))

	return s.repo.Create(ctx, animal)
}

func (s *animalService) Update(ctx context.Context, id int, req *models.UpdateAnimalRequest) (*models.Animal, error) {
	s.logger.Debug("Update called", zap.Int("id", id))

	// Get existing animal
	animal, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if animal == nil {
		return nil, fmt.Errorf("animal not found")
	}

	// Apply updates
	if req.Name != nil {
		animal.Name = *req.Name
	}
	if req.Status != nil {
		animal.Status = *req.Status
	}
	if req.Notes != nil {
		animal.Notes = req.Notes
	}

	return s.repo.Update(ctx, animal)
}

func (s *animalService) Delete(ctx context.Context, id int) error {
	s.logger.Debug("Delete called", zap.Int("id", id))
	return s.repo.Delete(ctx, id)
}

func (s *animalService) Count(ctx context.Context) (int, error) {
	s.logger.Debug("Count called")
	return s.repo.Count(ctx)
}
