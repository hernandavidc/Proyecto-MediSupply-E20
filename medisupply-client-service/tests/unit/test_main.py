import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestMainEndpoints:
    """Test main application endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        with TestClient(app) as client:
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "service" in data
            assert "Client Service" in data["service"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "service" in data
            assert "timestamp" in data
    
    def test_docs_endpoint_accessible(self):
        """Test that OpenAPI docs are accessible"""
        with TestClient(app) as client:
            response = client.get("/docs")
            
            assert response.status_code == 200
    
    def test_openapi_json_accessible(self):
        """Test that OpenAPI JSON schema is accessible"""
        with TestClient(app) as client:
            response = client.get("/openapi.json")
            
            assert response.status_code == 200
            data = response.json()
            assert "openapi" in data
            assert "info" in data
            assert "paths" in data

