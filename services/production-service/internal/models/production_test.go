package models

import (
	"testing"
	"time"
)

func TestCreateProductionRequestValidate(t *testing.T) {
	now := time.Now()
	tests := []struct {
		name    string
		req     CreateProductionRequest
		wantErr bool
	}{
		{
			name: "valid payload",
			req: CreateProductionRequest{
				PlotID:      "plot-1",
				HarvestDate: now,
				QuantityKg:  120.5,
			},
			wantErr: false,
		},
		{
			name: "missing plot id",
			req: CreateProductionRequest{
				HarvestDate: now,
				QuantityKg:  120.5,
			},
			wantErr: true,
		},
		{
			name: "invalid quantity",
			req: CreateProductionRequest{
				PlotID:      "plot-1",
				HarvestDate: now,
				QuantityKg:  0,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.req.Validate()
			if tt.wantErr && err == nil {
				t.Fatalf("expected error, got nil")
			}
			if !tt.wantErr && err != nil {
				t.Fatalf("expected nil error, got %v", err)
			}
		})
	}
}
