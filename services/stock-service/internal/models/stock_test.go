package models

import "testing"

func TestCreateStockRequestValidate(t *testing.T) {
	tests := []struct {
		name    string
		req     CreateStockRequest
		wantErr bool
	}{
		{
			name: "valid request",
			req: CreateStockRequest{
				PropertyID:      "prop-1",
				ItemName:        "Fertilizante NPK",
				Category:        "fertilizer",
				Quantity:        50,
				Unit:            "kg",
				MinimumQuantity: 10,
			},
			wantErr: false,
		},
		{
			name: "missing property_id",
			req: CreateStockRequest{
				ItemName:        "Fertilizante NPK",
				Quantity:        50,
				Unit:            "kg",
				MinimumQuantity: 10,
			},
			wantErr: true,
		},
		{
			name: "negative quantity",
			req: CreateStockRequest{
				PropertyID:      "prop-1",
				ItemName:        "Fertilizante NPK",
				Quantity:        -1,
				Unit:            "kg",
				MinimumQuantity: 10,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.req.Validate()
			if (err != nil) != tt.wantErr {
				t.Fatalf("Validate() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
