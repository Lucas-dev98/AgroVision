package service

import (
	"context"
	"fmt"

	"github.com/agrovision/cotacao-service/internal/models"
	"github.com/agrovision/cotacao-service/internal/repository"
	"go.uber.org/zap"
)

type CotacaoService interface {
	GetAll(ctx context.Context, limit, offset int) ([]models.Cotacao, error)
	GetByID(ctx context.Context, id int) (*models.Cotacao, error)
	GetLatestByTipo(ctx context.Context, tipoGado string) (*models.Cotacao, error)
	GetByTipoAndData(ctx context.Context, tipoGado string, dataReferencia string) ([]models.Cotacao, error)
	Create(ctx context.Context, req *models.CreateCotacaoRequest) (*models.Cotacao, error)
	Update(ctx context.Context, id int, req *models.UpdateCotacaoRequest) (*models.Cotacao, error)
	Delete(ctx context.Context, id int) error
	Count(ctx context.Context) (int, error)
}

type cotacaoService struct {
	repo   repository.CotacaoRepository
	logger *zap.Logger
}

func NewCotacaoService(repo repository.CotacaoRepository, logger *zap.Logger) CotacaoService {
	return &cotacaoService{
		repo:   repo,
		logger: logger,
	}
}

func (s *cotacaoService) GetAll(ctx context.Context, limit, offset int) ([]models.Cotacao, error) {
	s.logger.Debug("GetAll called", zap.Int("limit", limit), zap.Int("offset", offset))
	return s.repo.GetAll(ctx, limit, offset)
}

func (s *cotacaoService) GetByID(ctx context.Context, id int) (*models.Cotacao, error) {
	s.logger.Debug("GetByID called", zap.Int("id", id))

	cotacao, err := s.repo.GetByID(ctx, id)
	if err != nil {
		s.logger.Error("Error getting cotacao by ID", zap.Int("id", id), zap.Error(err))
		return nil, err
	}

	if cotacao == nil {
		return nil, fmt.Errorf("cotacao not found")
	}

	return cotacao, nil
}

func (s *cotacaoService) GetLatestByTipo(ctx context.Context, tipoGado string) (*models.Cotacao, error) {
	s.logger.Debug("GetLatestByTipo called", zap.String("tipoGado", tipoGado))
	return s.repo.GetLatestByTipo(ctx, tipoGado)
}

func (s *cotacaoService) GetByTipoAndData(ctx context.Context, tipoGado string, dataReferencia string) ([]models.Cotacao, error) {
	s.logger.Debug("GetByTipoAndData called", zap.String("tipoGado", tipoGado), zap.String("dataReferencia", dataReferencia))
	return s.repo.GetByTipoAndData(ctx, tipoGado, dataReferencia)
}

func (s *cotacaoService) Create(ctx context.Context, req *models.CreateCotacaoRequest) (*models.Cotacao, error) {
	s.logger.Debug("Create called", zap.String("tipoGado", req.TipoGado), zap.Float64("precoArroba", req.PrecoArroba))

	cotacao := &models.Cotacao{
		TipoGado:       req.TipoGado,
		PrecoArroba:    req.PrecoArroba,
		DataReferencia: req.DataReferencia,
		Fonte:          req.Fonte,
		Notas:          req.Notas,
	}

	return s.repo.Create(ctx, cotacao)
}

func (s *cotacaoService) Update(ctx context.Context, id int, req *models.UpdateCotacaoRequest) (*models.Cotacao, error) {
	s.logger.Debug("Update called", zap.Int("id", id))

	// Get existing cotacao
	cotacao, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, err
	}

	if cotacao == nil {
		return nil, fmt.Errorf("cotacao not found")
	}

	// Apply updates
	if req.PrecoArroba != nil {
		cotacao.PrecoArroba = *req.PrecoArroba
	}
	if req.Notas != nil {
		cotacao.Notas = req.Notas
	}

	return s.repo.Update(ctx, cotacao)
}

func (s *cotacaoService) Delete(ctx context.Context, id int) error {
	s.logger.Debug("Delete called", zap.Int("id", id))
	return s.repo.Delete(ctx, id)
}

func (s *cotacaoService) Count(ctx context.Context) (int, error) {
	s.logger.Debug("Count called")
	return s.repo.Count(ctx)
}
