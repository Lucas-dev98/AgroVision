package unit

import (
	"context"
	"testing"
	"time"

	"github.com/agrovision/pesagem-service/internal/models"
	"github.com/agrovision/pesagem-service/internal/service"
	"go.uber.org/zap"
)

// Mock repository for testing
type mockPesagemRepository struct {
	pesagens map[int]*models.Pesagem
	nextID   int
}

func newMockRepository() *mockPesagemRepository {
	return &mockPesagemRepository{
		pesagens: make(map[int]*models.Pesagem),
		nextID:   1,
	}
}

func (m *mockPesagemRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Pesagem, error) {
	var result []models.Pesagem
	for _, p := range m.pesagens {
		result = append(result, *p)
	}
	return result, nil
}

func (m *mockPesagemRepository) GetByID(ctx context.Context, id int) (*models.Pesagem, error) {
	return m.pesagens[id], nil
}

func (m *mockPesagemRepository) GetByAnimalID(ctx context.Context, animalID int) ([]models.Pesagem, error) {
	var result []models.Pesagem
	for _, p := range m.pesagens {
		if p.AnimalID == animalID {
			result = append(result, *p)
		}
	}
	return result, nil
}

func (m *mockPesagemRepository) GetLatestByAnimalID(ctx context.Context, animalID int) (*models.Pesagem, error) {
	for _, p := range m.pesagens {
		if p.AnimalID == animalID {
			return p, nil
		}
	}
	return nil, nil
}

func (m *mockPesagemRepository) Create(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error) {
	pesagem.ID = m.nextID
	pesagem.CreatedAt = time.Now()
	pesagem.UpdatedAt = time.Now()
	m.pesagens[m.nextID] = pesagem
	m.nextID++
	return pesagem, nil
}

func (m *mockPesagemRepository) Update(ctx context.Context, pesagem *models.Pesagem) (*models.Pesagem, error) {
	pesagem.UpdatedAt = time.Now()
	m.pesagens[pesagem.ID] = pesagem
	return pesagem, nil
}

func (m *mockPesagemRepository) Delete(ctx context.Context, id int) error {
	delete(m.pesagens, id)
	return nil
}

func (m *mockPesagemRepository) Count(ctx context.Context) (int, error) {
	return len(m.pesagens), nil
}

func TestCreatePesagem(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	pesagemService := service.NewPesagemService(mockRepo, logger)

	req := &models.CreatePesagemRequest{
		AnimalID:    1,
		PesoKg:      450.5,
		DataPesagem: time.Now(),
		Observacoes: nil,
	}

	pesagem, err := pesagemService.Create(context.Background(), req)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if pesagem == nil {
		t.Fatalf("Expected pesagem, got nil")
	}
	if pesagem.AnimalID != 1 {
		t.Fatalf("Expected animal_id 1, got %d", pesagem.AnimalID)
	}
	if pesagem.PesoKg != 450.5 {
		t.Fatalf("Expected peso 450.5, got %f", pesagem.PesoKg)
	}
}

func TestGetPesagem(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	pesagemService := service.NewPesagemService(mockRepo, logger)

	// Create a pesagem first
	req := &models.CreatePesagemRequest{
		AnimalID:    1,
		PesoKg:      450.5,
		DataPesagem: time.Now(),
	}
	created, _ := pesagemService.Create(context.Background(), req)

	// Get it back
	pesagem, err := pesagemService.GetByID(context.Background(), created.ID)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if pesagem == nil {
		t.Fatalf("Expected pesagem, got nil")
	}
	if pesagem.PesoKg != 450.5 {
		t.Fatalf("Expected peso 450.5, got %f", pesagem.PesoKg)
	}
}

func TestGetByAnimalID(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	pesagemService := service.NewPesagemService(mockRepo, logger)

	// Create 2 pesagens for animal 1
	req1 := &models.CreatePesagemRequest{
		AnimalID:    1,
		PesoKg:      450.5,
		DataPesagem: time.Now(),
	}
	req2 := &models.CreatePesagemRequest{
		AnimalID:    1,
		PesoKg:      480.0,
		DataPesagem: time.Now().Add(24 * time.Hour),
	}
	pesagemService.Create(context.Background(), req1)
	pesagemService.Create(context.Background(), req2)

	// Get all for animal 1
	pesagens, err := pesagemService.GetByAnimalID(context.Background(), 1)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if len(pesagens) != 2 {
		t.Fatalf("Expected 2 pesagens, got %d", len(pesagens))
	}
}

func TestDeletePesagem(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	pesagemService := service.NewPesagemService(mockRepo, logger)

	// Create a pesagem
	req := &models.CreatePesagemRequest{
		AnimalID:    1,
		PesoKg:      450.5,
		DataPesagem: time.Now(),
	}
	created, _ := pesagemService.Create(context.Background(), req)

	// Delete it
	err := pesagemService.Delete(context.Background(), created.ID)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	// Verify it's gone
	count, _ := mockRepo.Count(context.Background())
	if count != 0 {
		t.Fatalf("Expected 0 pesagens, got %d", count)
	}
}
