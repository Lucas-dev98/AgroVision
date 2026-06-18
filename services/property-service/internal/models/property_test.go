package models

import "testing"

func TestCreatePropertyRequestValidate(t *testing.T) {
	tests := []struct {
		name    string
		req     CreatePropertyRequest
		wantErr bool
	}{
		{
			name: "valid payload",
			req: CreatePropertyRequest{
				UserID:      "u-1",
				Name:        "Fazenda Norte",
				TotalArea:   10,
				PlantedArea: 8,
			},
			wantErr: false,
		},
		{
			name: "missing user id",
			req: CreatePropertyRequest{
				Name:        "Fazenda Norte",
				TotalArea:   10,
				PlantedArea: 8,
			},
			wantErr: true,
		},
		{
			name: "planted greater than total",
			req: CreatePropertyRequest{
				UserID:      "u-1",
				Name:        "Fazenda Norte",
				TotalArea:   10,
				PlantedArea: 11,
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
