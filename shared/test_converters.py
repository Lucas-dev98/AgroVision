"""
TESTES UNITÁRIOS - Converters (Conversões de Unidade)
TDD Phase 1: RED - Escrevemos os testes
Fase 2: GREEN - Code passa nos testes
Fase 3: REFACTOR - Melhorar código
"""
import pytest
from shared.converters import (
    kg_to_arrobas,
    arrobas_to_kg,
    calculate_animal_value,
    calculate_weight_gain,
    calculate_daily_weight_gain
)


class TestKgToArrobas:
    """Conversão de quilos para arrobas"""

    def test_kg_to_arrobas_450kg(self):
        """
        GIVEN: 450 kg
        WHEN: Converter para arrobas
        THEN: Deve retornar 30 arrobas (450 / 15)
        """
        result = kg_to_arrobas(450)
        assert result == 30.0

    def test_kg_to_arrobas_zero(self):
        """
        GIVEN: 0 kg
        WHEN: Converter
        THEN: Deve retornar 0 arrobas
        """
        result = kg_to_arrobas(0)
        assert result == 0.0

    def test_kg_to_arrobas_decimal(self):
        """
        GIVEN: 480 kg
        WHEN: Converter
        THEN: Deve retornar 32.0 arrobas (480 / 15)
        """
        result = kg_to_arrobas(480)
        assert result == 32.0

    def test_kg_to_arrobas_custom_arroba_size(self):
        """
        GIVEN: 420 kg com arroba customizada (14 kg)
        WHEN: Converter
        THEN: Deve retornar 30 arrobas (420 / 14)
        """
        result = kg_to_arrobas(420, arroba_in_kg=14.0)
        assert result == 30.0

    def test_kg_to_arrobas_negative_should_raise_error(self):
        """
        GIVEN: -100 kg (valor negativo)
        WHEN: Converter
        THEN: Deve lançar ValueError
        """
        with pytest.raises(ValueError):
            kg_to_arrobas(-100)


class TestArrobasToKg:
    """Conversão de arrobas para quilos"""

    def test_arrobas_to_kg_30(self):
        """
        GIVEN: 30 arrobas
        WHEN: Converter para kg
        THEN: Deve retornar 450 kg (30 × 15)
        """
        result = arrobas_to_kg(30)
        assert result == 450.0

    def test_arrobas_to_kg_zero(self):
        """
        GIVEN: 0 arrobas
        WHEN: Converter
        THEN: Deve retornar 0 kg
        """
        result = arrobas_to_kg(0)
        assert result == 0.0

    def test_arrobas_to_kg_custom_size(self):
        """
        GIVEN: 30 arrobas com size customizado (14 kg)
        WHEN: Converter
        THEN: Deve retornar 420 kg (30 × 14)
        """
        result = arrobas_to_kg(30, arroba_in_kg=14.0)
        assert result == 420.0

    def test_arrobas_to_kg_negative_should_raise_error(self):
        """
        GIVEN: -50 arrobas
        WHEN: Converter
        THEN: Deve lançar ValueError
        """
        with pytest.raises(ValueError):
            arrobas_to_kg(-50)


class TestBidrectionalConversion:
    """Testes de conversão bidirecional"""

    def test_kg_to_arrobas_and_back(self):
        """
        GIVEN: Alguns quilos
        WHEN: Converter para arrobas e voltar para kg
        THEN: Deve voltar ao valor original
        """
        original_kg = 450.0
        
        arrobas = kg_to_arrobas(original_kg)
        back_to_kg = arrobas_to_kg(arrobas)
        
        assert back_to_kg == original_kg

    def test_arrobas_to_kg_and_back(self):
        """
        GIVEN: Algumas arrobas
        WHEN: Converter para kg e voltar para arrobas
        THEN: Deve voltar ao valor original
        """
        original_arrobas = 30.0
        
        kg = arrobas_to_kg(original_arrobas)
        back_to_arrobas = kg_to_arrobas(kg)
        
        assert back_to_arrobas == original_arrobas


class TestCalculateAnimalValue:
    """Cálculo de valor do animal"""

    def test_calculate_value_basic(self):
        """
        GIVEN: 30 arrobas a R$ 367,05 por arroba
        WHEN: Calcular valor
        THEN: Deve retornar R$ 11.011,50 (30 × 367.05)
        """
        result = calculate_animal_value(30, 367.05)
        assert result == 11011.5

    def test_calculate_value_zero_weight(self):
        """
        GIVEN: 0 arrobas
        WHEN: Calcular valor
        THEN: Deve retornar 0
        """
        result = calculate_animal_value(0, 367.05)
        assert result == 0.0

    def test_calculate_value_zero_price(self):
        """
        GIVEN: 30 arrobas a R$ 0
        WHEN: Calcular
        THEN: Deve retornar 0
        """
        result = calculate_animal_value(30, 0)
        assert result == 0.0

    def test_calculate_value_with_different_price(self):
        """
        GIVEN: 25 arrobas a R$ 350,00
        WHEN: Calcular
        THEN: Deve retornar R$ 8.750,00 (25 × 350)
        """
        result = calculate_animal_value(25, 350.0)
        assert result == 8750.0

    def test_calculate_value_negative_values_should_raise(self):
        """
        GIVEN: Valores negativos
        WHEN: Calcular valor
        THEN: Deve lançar ValueError
        """
        with pytest.raises(ValueError):
            calculate_animal_value(-30, 367.05)
        
        with pytest.raises(ValueError):
            calculate_animal_value(30, -367.05)


class TestCalculateWeightGain:
    """Cálculo de ganho de peso"""

    def test_weight_gain_positive(self):
        """
        GIVEN: Peso inicial 400 kg, final 450 kg
        WHEN: Calcular ganho
        THEN: Deve retornar 50 kg
        """
        result = calculate_weight_gain(400, 450)
        assert result == 50.0

    def test_weight_gain_negative(self):
        """
        GIVEN: Peso inicial 450 kg, final 400 kg
        WHEN: Calcular ganho
        THEN: Deve retornar -50 kg (perda de peso)
        """
        result = calculate_weight_gain(450, 400)
        assert result == -50.0

    def test_weight_gain_zero(self):
        """
        GIVEN: Pesos iguais
        WHEN: Calcular ganho
        THEN: Deve retornar 0
        """
        result = calculate_weight_gain(450, 450)
        assert result == 0.0


class TestCalculateDailyWeightGain:
    """Cálculo de ganho diário de peso"""

    def test_daily_weight_gain_basic(self):
        """
        GIVEN: Ganho de 50 kg em 100 dias
        WHEN: Calcular ganho diário
        THEN: Deve retornar 0.5 kg/dia (50 / 100)
        """
        result = calculate_daily_weight_gain(50, 100)
        assert result == 0.5

    def test_daily_weight_gain_one_day(self):
        """
        GIVEN: Ganho de 2 kg em 1 dia
        WHEN: Calcular
        THEN: Deve retornar 2.0 kg/dia
        """
        result = calculate_daily_weight_gain(2, 1)
        assert result == 2.0

    def test_daily_weight_gain_zero_days_should_raise(self):
        """
        GIVEN: 0 dias
        WHEN: Calcular ganho diário
        THEN: Deve lançar ValueError
        """
        with pytest.raises(ValueError):
            calculate_daily_weight_gain(50, 0)

    def test_daily_weight_gain_negative_days_should_raise(self):
        """
        GIVEN: -10 dias
        WHEN: Calcular
        THEN: Deve lançar ValueError
        """
        with pytest.raises(ValueError):
            calculate_daily_weight_gain(50, -10)

    def test_daily_weight_gain_fractional(self):
        """
        GIVEN: Ganho de 75 kg em 150 dias
        WHEN: Calcular
        THEN: Deve retornar 0.5 kg/dia
        """
        result = calculate_daily_weight_gain(75, 150)
        assert result == 0.5
