package models

import "testing"

func TestErrPropertyIDRequired(t *testing.T) {
	if ErrPropertyIDRequired == nil {
		t.Fatal("ErrPropertyIDRequired should not be nil")
	}
}
