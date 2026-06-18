package models

import (
	"testing"
	"time"
)

func TestCreateExpenseRequestValidate(t *testing.T) {
	now := time.Now()
	tests := []struct {
		name    string
		req     CreateExpenseRequest
		wantErr bool
	}{
		{
			name: "valid payload",
			req: CreateExpenseRequest{
				PropertyID: "property-1",
				Category:   "fuel",
				Amount:     150.75,
				Date:       now,
			},
			wantErr: false,
		},
		{
			name: "missing property",
			req: CreateExpenseRequest{
				Category: "fuel",
				Amount:   150.75,
				Date:     now,
			},
			wantErr: true,
		},
		{
			name: "invalid amount",
			req: CreateExpenseRequest{
				PropertyID: "property-1",
				Category:   "fuel",
				Amount:     0,
				Date:       now,
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
