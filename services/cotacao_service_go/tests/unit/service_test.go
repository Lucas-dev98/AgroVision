package unit

import (
	"context"
	"testing"
	"time"

	"github.com/agrovision/cotacao-service/internal/models"
	"github.com/agrovision/cotacao-service/internal/repository"
	"github.com/agrovision/cotacao-service/internal/service"
	"go.uber.org/zap"
)

// Mock repository for testing
type mockCotacaoRepository struct {
	cotacoes map[int]*models.Cotacao
	nextID   int
}

func newMockRepository() *mockCotacaoRepository {
	return &mockCotacaoRepository{
		cotacoes: make(map[int]*models.Cotacao),
		nextID:   1,
	}
}

func (m *mockCotacaoRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Cotacao, error) {
	var result []models.Cotacao
	for _, c := range m.cotacoes {
		result = append(result, *c)
	}
	return result, nil
}

func (m *mockCotacaoRepository) GetByID(ctx context.Context, id int) (*models.Cotacao, error) {
	return m.cotacoes[id], nil
}

func (m *mockCotacaoRepository) GetLatestByTipo(ctx context.Context, tipoGado string) (*models.Cotacao, error) {
	for _, c := range m.cotacoes {
		if c.TipoGado == tipoGado {
			return c, nil
		}
	}
	return nil, nil
}

func (m *mockCotacaoRepository) GetByTipoAndData(ctx context.Context, tipoGado string, dataReferencia string) ([]models.Cotacao, error) {
	var result []models.Cotacao
	for _, c := range m.cotacoes {
		if c.TipoGado == tipoGado {
			result = append(result, *c)
		}
	}
	return result, nil
}

func (m *mockCotacaoRepository) Create(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error) {
	cotacao.ID = m.nextID
	cotacao.CreatedAt = time.Now()
	cotacao.UpdatedAt = time.Now()
	m.cotacoes[m.nextID] = cotacao
	m.nextID++
	return cotacao, nil
}

func (m *mockCotacaoRepository) Update(ctx context.Context, cotacao *models.Cotacao) (*models.Cotacao, error) {
	cotacao.UpdatedAt = time.Now()
	m.cotacoes[cotacao.ID] = cotacao
	return cotacao, nil
}

func (m *mockCotacaoRepository) Delete(ctx context.Context, id int) error {
	delete(m.cotacoes, id)
	return nil
}

func (m *mockCotacaoRepository) Count(ctx context.Context) (int, error) {
	return len(m.cotacoes), nil
}

func TestCreateCotacao(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	cotacaoService := service.NewCotacaoService(mockRepo, logger)

	req := &models.CreateCotacaoRequest{
		TipoGado:       "Boi",
		PrecoArroba:    250.50,
		DataReferencia: time.Now(),
		Fonte:          "CEPEA",
	}

	cotacao, err := cotacaoService.Create(context.Background(), req)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if cotacao == nil {
		t.Fatalf("Expected cotacao, got nil")
	}
	if cotacao.TipoGado != "Boi" {
		t.Fatalf("Expected tipo Boi, got %s", cotacao.TipoGado)
	}
	if cotacao.PrecoArroba != 250.50 {
		t.Fatalf("Expected preco 250.50, got %f", cotacao.PrecoArroba)
	}
}

func TestGetCotacao(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	cotacaoService := service.NewCotacaoService(mockRepo, logger)

	// Create a cotacao first
	req := &models.CreateCotacaoRequest{
		TipoGado:       "Vaca",
		PrecoArroba:    220.00,
		DataReferencia: time.Now(),
		Fonte:          "CEPEA",
	}
	created, _ := cotacaoService.Create(context.Background(), req)

	// Get it back
	cotacao, err := cotacaoService.GetByID(context.Background(), created.ID)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if cotacao == nil {
		t.Fatalf("Expected cotacao, got nil")
	}
	if cotacao.PrecoArroba != 220.00 {
		t.Fatalf("Expected preco 220.00, got %f", cotacao.PrecoArroba)
	}
}

func TestDeleteCotacao(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	cotacaoService := service.NewCotacaoService(mockRepo, logger)

	// Create a cotacao
	req := &models.CreateCotacaoRequest{
		TipoGado:       "Bezerro",
		PrecoArroba:    180.00,
		DataReferencia: time.Now(),
		Fonte:          "CEPEA",
	}
	created, _ := cotacaoService.Create(context.Background(), req)

	// Delete it
	err := cotacaoService.Delete(context.Background(), created.ID)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	// Verify it's gone
	count, _ := mockRepo.Count(context.Background())
	if count != 0 {
		t.Fatalf("Expected 0 cotacoes, got %d", count)
	}
}
