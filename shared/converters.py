"""
Utilitários de conversão e cálculos
"""
from decimal import Decimal
from typing import Optional


def kg_to_arrobas(kg: float, arroba_in_kg: float = 15.0) -> float:
    """
    Converte quilos para arrobas
    
    Args:
        kg: Peso em quilos
        arroba_in_kg: Valor de 1 arroba em kg (padrão 15 kg)
    
    Returns:
        Peso em arrobas
    
    Exemplo:
        >>> kg_to_arrobas(450)
        30.0
    """
    if kg < 0:
        raise ValueError("Peso não pode ser negativo")
    
    return round(kg / arroba_in_kg, 2)


def arrobas_to_kg(arrobas: float, arroba_in_kg: float = 15.0) -> float:
    """
    Converte arrobas para quilos
    
    Args:
        arrobas: Peso em arrobas
        arroba_in_kg: Valor de 1 arroba em kg (padrão 15 kg)
    
    Returns:
        Peso em quilos
    
    Exemplo:
        >>> arrobas_to_kg(30)
        450.0
    """
    if arrobas < 0:
        raise ValueError("Peso não pode ser negativo")
    
    return round(arrobas * arroba_in_kg, 2)


def calculate_animal_value(
    weight_arrobas: float,
    price_per_arroba: float
) -> float:
    """
    Calcula valor do animal baseado em peso e cotação
    
    Args:
        weight_arrobas: Peso em arrobas
        price_per_arroba: Preço por arroba em R$
    
    Returns:
        Valor total em R$
    
    Exemplo:
        >>> calculate_animal_value(30, 367.05)
        11011.5
    """
    if weight_arrobas < 0 or price_per_arroba < 0:
        raise ValueError("Valores não podem ser negativos")
    
    return round(weight_arrobas * price_per_arroba, 2)


def calculate_weight_gain(
    initial_weight_kg: float,
    final_weight_kg: float
) -> float:
    """
    Calcula ganho de peso entre duas pesagens
    
    Args:
        initial_weight_kg: Peso inicial em kg
        final_weight_kg: Peso final em kg
    
    Returns:
        Ganho de peso em kg
    
    Exemplo:
        >>> calculate_weight_gain(400, 450)
        50.0
    """
    return round(final_weight_kg - initial_weight_kg, 2)


def calculate_daily_weight_gain(
    weight_gain_kg: float,
    days: int
) -> float:
    """
    Calcula ganho diário de peso
    
    Args:
        weight_gain_kg: Ganho total em kg
        days: Número de dias
    
    Returns:
        Ganho diário médio em kg
    
    Exemplo:
        >>> calculate_daily_weight_gain(50, 100)
        0.5
    """
    if days <= 0:
        raise ValueError("Número de dias deve ser maior que 0")
    
    return round(weight_gain_kg / days, 2)
