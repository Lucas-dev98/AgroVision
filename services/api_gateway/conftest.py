"""Configuração de testes para API Gateway"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from app import app


@pytest.fixture(scope="session")
def test_client():
    """Cliente de teste"""
    return TestClient(app)


@pytest.fixture
def client():
    """Cliente para cada teste"""
    return TestClient(app)
