import pytest
from pydantic import ValidationError
from app.schemas.client_schema import ClientCreate


def test_valid_client_schema():
    """Test that valid client data passes validation"""
    client_data = {
        "nombre": "Test Company",
        "nit": "1234567890",
        "direccion": "123 Test Street",
        "nombre_contacto": "John Doe",
        "telefono_contacto": "+1234567890",
        "email_contacto": "test@example.com"
    }
    
    client = ClientCreate(**client_data)
    assert client.nombre == "Test Company"
    assert client.nit == "1234567890"


def test_invalid_email():
    """Test that invalid email raises validation error"""
    client_data = {
        "nombre": "Test Company",
        "nit": "1234567890",
        "direccion": "123 Test Street",
        "nombre_contacto": "John Doe",
        "telefono_contacto": "+1234567890",
        "email_contacto": "invalid-email"
    }
    
    with pytest.raises(ValidationError):
        ClientCreate(**client_data)


def test_short_nit():
    """Test that short NIT raises validation error"""
    client_data = {
        "nombre": "Test Company",
        "nit": "123",  # Too short
        "direccion": "123 Test Street",
        "nombre_contacto": "John Doe",
        "telefono_contacto": "+1234567890",
        "email_contacto": "test@example.com"
    }
    
    with pytest.raises(ValidationError):
        ClientCreate(**client_data)


def test_nit_cleaning():
    """Test that NIT is cleaned properly"""
    client_data = {
        "nombre": "Test Company",
        "nit": "123-456-7890",  # With hyphens
        "direccion": "123 Test Street",
        "nombre_contacto": "John Doe",
        "telefono_contacto": "+1234567890",
        "email_contacto": "test@example.com"
    }
    
    client = ClientCreate(**client_data)
    assert client.nit == "1234567890"  # Hyphens removed

