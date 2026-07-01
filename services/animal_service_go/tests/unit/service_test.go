package unit

import (
	"context"
	"testing"

	"github.com/agrovision/animal-service/internal/models"
	"github.com/agrovision/animal-service/internal/service"
	"go.uber.org/zap"
)

// Mock repository for testing
type mockAnimalRepository struct {
	animals map[int]*models.Animal
	nextID  int
}

func newMockRepository() *mockAnimalRepository {
	return &mockAnimalRepository{
		animals: make(map[int]*models.Animal),
		nextID:  1,
	}
}

func (m *mockAnimalRepository) GetAll(ctx context.Context, limit, offset int) ([]models.Animal, error) {
	var result []models.Animal
	for _, a := range m.animals {
		result = append(result, *a)
	}
	return result, nil
}

func (m *mockAnimalRepository) GetByID(ctx context.Context, id int) (*models.Animal, error) {
	return m.animals[id], nil
}

func (m *mockAnimalRepository) GetByEarTag(ctx context.Context, earTag string) (*models.Animal, error) {
	return nil, nil
}

func (m *mockAnimalRepository) Create(ctx context.Context, animal *models.Animal) (*models.Animal, error) {
	animal.ID = m.nextID
	m.animals[m.nextID] = animal
	m.nextID++
	return animal, nil
}

func (m *mockAnimalRepository) Update(ctx context.Context, animal *models.Animal) (*models.Animal, error) {
	m.animals[animal.ID] = animal
	return animal, nil
}

func (m *mockAnimalRepository) Delete(ctx context.Context, id int) error {
	delete(m.animals, id)
	return nil
}

func (m *mockAnimalRepository) Count(ctx context.Context) (int, error) {
	return len(m.animals), nil
}

func TestCreateAnimal(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	animalService := service.NewAnimalService(mockRepo, logger)

	req := &models.CreateAnimalRequest{
		Name:   "Boi Preto",
		Breed:  "Nelore",
		Gender: "M",
	}

	animal, err := animalService.Create(context.Background(), req)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if animal == nil {
		t.Fatalf("Expected animal, got nil")
	}
	if animal.Name != "Boi Preto" {
		t.Fatalf("Expected name 'Boi Preto', got %s", animal.Name)
	}
	if animal.Status != "ATIVO" {
		t.Fatalf("Expected status 'ATIVO', got %s", animal.Status)
	}
}

func TestGetAnimal(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	animalService := service.NewAnimalService(mockRepo, logger)

	// Create an animal first
	req := &models.CreateAnimalRequest{
		Name:   "Vaca Branca",
		Breed:  "Angus",
		Gender: "F",
	}
	created, _ := animalService.Create(context.Background(), req)

	// Get it back
	animal, err := animalService.GetByID(context.Background(), created.ID)

	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	if animal == nil {
		t.Fatalf("Expected animal, got nil")
	}
	if animal.Name != "Vaca Branca" {
		t.Fatalf("Expected name 'Vaca Branca', got %s", animal.Name)
	}
}

func TestDeleteAnimal(t *testing.T) {
	logger, _ := zap.NewProduction()
	mockRepo := newMockRepository()
	animalService := service.NewAnimalService(mockRepo, logger)

	// Create an animal
	req := &models.CreateAnimalRequest{
		Name:   "Boi Preto",
		Breed:  "Nelore",
		Gender: "M",
	}
	created, _ := animalService.Create(context.Background(), req)

	// Delete it
	err := animalService.Delete(context.Background(), created.ID)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}

	// Verify it's gone
	count, _ := mockRepo.Count(context.Background())
	if count != 0 {
		t.Fatalf("Expected 0 animals, got %d", count)
	}
}
