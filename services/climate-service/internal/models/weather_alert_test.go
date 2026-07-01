package models

import "testing"

func TestCreateWeatherAlertRequestValidate(t *testing.T) {
	tests := []struct {
		name    string
		req     CreateWeatherAlertRequest
		wantErr bool
	}{
		{
			name: "valid request",
			req: CreateWeatherAlertRequest{
				PropertyID:        "prop-1",
				AlertType:         "rain",
				Severity:          "high",
				Description:       "Heavy rain expected",
				RecommendedAction: "Delay spraying",
			},
			wantErr: false,
		},
		{
			name: "missing property_id",
			req: CreateWeatherAlertRequest{
				AlertType:         "rain",
				Severity:          "high",
				Description:       "Heavy rain expected",
				RecommendedAction: "Delay spraying",
			},
			wantErr: true,
		},
		{
			name: "invalid severity",
			req: CreateWeatherAlertRequest{
				PropertyID:        "prop-1",
				AlertType:         "rain",
				Severity:          "critical",
				Description:       "Heavy rain expected",
				RecommendedAction: "Delay spraying",
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
