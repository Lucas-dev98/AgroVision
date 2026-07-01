package models

import (
	"testing"
	"time"
)

func TestCreateNutritionRequestValidate(t *testing.T) {
	valid := CreateNutritionRequest{
		PropertyID: "prop-1",
		FeedType:   "silagem",
		QuantityKg: 12.5,
		MealTime:   time.Now(),
	}

	if err := valid.Validate(); err != nil {
		t.Fatalf("expected valid request, got error: %v", err)
	}

	invalidProperty := valid
	invalidProperty.PropertyID = ""
	if err := invalidProperty.Validate(); err == nil {
		t.Fatalf("expected property validation error")
	}

	invalidFeed := valid
	invalidFeed.FeedType = ""
	if err := invalidFeed.Validate(); err == nil {
		t.Fatalf("expected feed validation error")
	}

	invalidQuantity := valid
	invalidQuantity.QuantityKg = 0
	if err := invalidQuantity.Validate(); err == nil {
		t.Fatalf("expected quantity validation error")
	}
}
