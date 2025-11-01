import pytest
from fastapi import status
from jose import jwt
from app.core.config import settings


def get_test_token(email: str = "test@example.com") -> str:
    """Helper para crear tokens de prueba"""
    from datetime import datetime, timedelta, timezone
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": email, "exp": expire}
    return jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def test_register_client(client, sample_client_data, auth_headers):
    """Test client registration endpoint with valid token"""
    response = client.post(
        "/api/v1/clientes",
        json=sample_client_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nombre"] == sample_client_data["nombre"]
    assert data["nit"] == sample_client_data["nit"]
    assert "id" in data
    assert "created_at" in data


def test_register_client_without_token(client, sample_client_data):
    """Test that registering client without token returns 401"""
    response = client.post("/api/v1/clientes", json=sample_client_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_client_with_invalid_token(client, sample_client_data):
    """Test that registering client with invalid token returns 401"""
    response = client.post(
        "/api/v1/clientes",
        json=sample_client_data,
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_duplicate_client(client, sample_client_data, auth_headers):
    """Test that registering duplicate NIT fails"""
    # Register first client
    client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    
    # Try to register again with same NIT
    response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_409_CONFLICT


def test_validate_nit(client):
    """Test NIT validation endpoint"""
    response = client.get("/api/v1/clientes/validate-nit/1234567890")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "is_valid" in data
    assert "nit" in data
    assert data["nit"] == "1234567890"


def test_get_client_by_id(client, sample_client_data, auth_headers):
    """Test getting client by ID"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Get client (public endpoint, no auth required)
    response = client.get(f"/api/v1/clientes/{client_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == client_id
    assert data["nombre"] == sample_client_data["nombre"]


def test_get_nonexistent_client(client):
    """Test getting non-existent client returns 404"""
    response = client.get("/api/v1/clientes/nonexistent-id")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_clients(client, sample_client_data, auth_headers):
    """Test listing clients with pagination"""
    # Create a client
    client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    
    # Get list (public endpoint, no auth required)
    response = client.get("/api/v1/clientes")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "clients" in data
    assert "total" in data
    assert "page" in data
    assert len(data["clients"]) > 0


def test_update_client(client, sample_client_data, auth_headers):
    """Test updating client information"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Update client (requires auth)
    update_data = {"nombre_contacto": "Jane Smith"}
    response = client.put(f"/api/v1/clientes/{client_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre_contacto"] == "Jane Smith"


def test_update_client_without_token(client, sample_client_data, auth_headers):
    """Test that updating client without token returns 401"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Try to update without token
    update_data = {"nombre_contacto": "Jane Smith"}
    response = client.put(f"/api/v1/clientes/{client_id}", json=update_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_client(client, sample_client_data, auth_headers):
    """Test deleting client"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Delete client (requires auth)
    response = client.delete(f"/api/v1/clientes/{client_id}", headers=auth_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify client is deleted
    get_response = client.get(f"/api/v1/clientes/{client_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_client_without_token(client, sample_client_data, auth_headers):
    """Test that deleting client without token returns 401"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Try to delete without token
    response = client.delete(f"/api/v1/clientes/{client_id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"


def test_validate_client_endpoint(client, sample_client_data, auth_headers):
    """Test validate client endpoint requires authentication"""
    # Create client
    create_response = client.post("/api/v1/clientes", json=sample_client_data, headers=auth_headers)
    client_id = create_response.json()["id"]
    
    # Try to validate without token
    response = client.post(f"/api/v1/clientes/{client_id}/validate")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Validate with token
    response = client.post(f"/api/v1/clientes/{client_id}/validate", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_validated"] is True

