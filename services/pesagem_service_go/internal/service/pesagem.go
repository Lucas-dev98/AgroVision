package service

import (
	"context"
	"fmt"

	"github.com/agrovision/pesagem-service/internal/models"
	"github.com/agrovision/pesagem-service/internal/repository"
	"go.uber.org/zap"
)

type PesagemService interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Pesagem, error)
	GetByID(ctx context.Context, id int) (*models.Pesagem, error)
	GetByAnimalID(ctx context.Context, animalID int) ([]models.Pesagem, error)
	GetLatestByAnimalID(ctx context.Context, animalID int) (*models.Pesagem, error)
	Create(ctx context.Context, req *models.CreatePesagemRequest) (*models.Pesagem, error)
	Update(ctx context.Context, id int, req *models.UpdatePesagemRequest) (*models.Pesagem, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type pesagemService struct {
	repo   repository.PesagemRepository
	logger *zap.Logger
}

func NewPesagemService(repo repository.PesagemRepository, logger *zap.Logger) PesagemService {
	return &pesagemService{
		repo:   repo,
		logger: logger,
	}
}

func (s *pesagemService) GetAll(ctx context.Context, limit, offset int) ([]models.Pesagem, error) {
	s.logger.Debug("GetAll called", zap.Int("limit", limit), zap.Int("offset", offset))
	return s.repo.GetAll(ctx, limit, offset)
}

func (s *pesagemService) GetByID(ctx context.Context, id int) (*models.Pesagem, error) {
	s.logger.Debug("GetByID called", zap.Int("id", id))

	pesagem, err := s.repo.GetByID(ctx, id)
	if err != nil {
		s.logger.Error("Error getting pesagem by ID", zap.Int("id", id), zap.Error(err))
		return nil, err
	}

	if pesagem == nil {
		return nil, fmt.Errorf("pesagem not found")
	}

	return pesagem, nil
}

func (s *pesagemService) GetByAnimalID(ctx context.Context, animalID int) ([]models.Pesagem, error) {
	s.logger.Debug("GetByAnimalID called", zap.Int("animalID", animalID))
	return s.repo.GetByAnimalID(ctx, animalID)
}

func (s *pesagemService) GetLatestByAnimalID(ctx context.Context, animalID int) (*models.Pesagem, error) {
	s.logger.Debug("GetLatestByAnimalID called", zap.Int("animalID", animalID))
	return s.repo.GetLatestByAnimalID(ctx, animalID)
}

func (s *pesagemService) Create(ctx context.Context, req *models.CreatePesagemRequest) (*models.Pesagem, error) {
	s.logger.Debug("Create called", zap.Int("animalID", req.AnimalID), zap.Float64("pesoKg", req.PesoKg))

	pesagem := &models.Pesagem{
		AnimalID:    req.AnimalID,
		PesoKg:      req.PesoKg,
		DataPesagem: req.DataPesagem,
		Observacoes: req.Observacoes,
	}

	return s.repo.Create(ctx, pesagem)
}

func (s *pesagemService) Update(ctx context.Context, id int, req *models.UpdatePesagemRequest) (*models.Pesagem, error) {
	s.logger.Debug("Update called", zap.Int("id", id))

	// Get existing pesagem
	pesagem, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if pesagem == nil {
		return nil, fmt.Errorf("pesagem not found")
	}

	// Apply updates
	if req.PesoKg != nil {
		pesagem.PesoKg = *req.PesoKg
	}
	if req.Observacoes != nil {
		pesagem.Observacoes = req.Observacoes
	}

	return s.repo.Update(ctx, pesagem)
}

func (s *pesagemService) Delete(ctx context.Context, id int) error {
	s.logger.Debug("Delete called", zap.Int("id", id))
	return s.repo.Delete(ctx, id)
}

func (s *pesagemService) Count(ctx context.Context) (int, error) {
	s.logger.Debug("Count called")
	return s.repo.Count(ctx)
}
