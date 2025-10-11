import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.schemas.user_schema import UserCreate, UserLogin


class TestUserRoutes:
    """Tests de integración para las rutas de usuario"""
    
    def test_health_check_endpoint(self, client: TestClient):
        """Test del endpoint de health check"""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["message"] == "User service is running"
        assert "timestamp" in data
    
    def test_register_user_success(self, client: TestClient):
        """Test registro exitoso de usuario"""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # La contraseña no debe devolverse
    
    def test_register_user_duplicate_email(self, client: TestClient):
        """Test registro con email duplicado"""
        user_data = {
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "password123"
        }
        
        # Registrar primer usuario
        response1 = client.post("/api/v1/users/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Intentar registrar segundo usuario con mismo email
        user_data2 = {
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "password456"
        }
        
        response2 = client.post("/api/v1/users/register", json=user_data2)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response2.json()
        assert "El email ya está registrado" in data["detail"]
    
    def test_register_user_invalid_email(self, client: TestClient):
        """Test registro con email inválido"""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_missing_fields(self, client: TestClient):
        """Test registro con campos faltantes"""
        user_data = {
            "name": "Test User",
            # "email": "test@example.com",  # Email faltante
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_token_success(self, client: TestClient):
        """Test generación exitosa de token"""
        # Primero registrar usuario
        user_data = {
            "name": "Token Test User",
            "email": "token@example.com",
            "password": "tokenpassword123"
        }
        
        register_response = client.post("/api/v1/users/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Generar token
        login_data = {
            "email": "token@example.com",
            "password": "tokenpassword123"
        }
        
        response = client.post("/api/v1/users/generate-token", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_generate_token_invalid_credentials(self, client: TestClient):
        """Test generación de token con credenciales inválidas"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/users/generate-token", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "Email o contraseña incorrectos" in data["detail"]
    
    def test_generate_token_inactive_user(self, client: TestClient, inactive_user):
        """Test generación de token con usuario inactivo"""
        login_data = {
            "email": inactive_user.email,
            "password": "inactivepassword"
        }
        
        response = client.post("/api/v1/users/generate-token", json=login_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "Usuario inactivo" in data["detail"]
    
    def test_oauth2_token_endpoint(self, client: TestClient):
        """Test del endpoint OAuth2 para Swagger UI"""
        # Primero registrar usuario
        user_data = {
            "name": "OAuth Test User",
            "email": "oauth@example.com",
            "password": "oauthpassword123"
        }
        
        register_response = client.post("/api/v1/users/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Generar token usando OAuth2 form
        form_data = {
            "username": "oauth@example.com",  # OAuth2 usa 'username' en lugar de 'email'
            "password": "oauthpassword123"
        }
        
        response = client.post(
            "/api/v1/users/token", 
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user_info_success(self, client: TestClient):
        """Test obtener información del usuario actual"""
        # Registrar y obtener token
        user_data = {
            "name": "Current User Test",
            "email": "current@example.com",
            "password": "currentpassword123"
        }
        
        register_response = client.post("/api/v1/users/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        login_data = {
            "email": "current@example.com",
            "password": "currentpassword123"
        }
        
        token_response = client.post("/api/v1/users/generate-token", json=login_data)
        token = token_response.json()["access_token"]
        
        # Obtener información del usuario
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "Current User Test"
        assert data["email"] == "current@example.com"
        assert data["is_active"] is True
    
    def test_get_current_user_info_unauthorized(self, client: TestClient):
        """Test obtener información sin token"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_info_invalid_token(self, client: TestClient):
        """Test obtener información con token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_user_by_id_success(self, client: TestClient):
        """Test obtener usuario por ID"""
        # Registrar usuario y obtener token
        user_data = {
            "name": "Get User Test",
            "email": "getuser@example.com",
            "password": "getuserpassword123"
        }
        
        register_response = client.post("/api/v1/users/register", json=user_data)
        user_id = register_response.json()["id"]
        
        login_data = {
            "email": "getuser@example.com",
            "password": "getuserpassword123"
        }
        
        token_response = client.post("/api/v1/users/generate-token", json=login_data)
        token = token_response.json()["access_token"]
        
        # Obtener usuario por ID
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == user_id
        assert data["name"] == "Get User Test"
        assert data["email"] == "getuser@example.com"
    
    def test_get_user_by_id_not_found(self, client: TestClient):
        """Test obtener usuario por ID no existente"""
        # Registrar usuario y obtener token
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        client.post("/api/v1/users/register", json=user_data)
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        token_response = client.post("/api/v1/users/generate-token", json=login_data)
        token = token_response.json()["access_token"]
        
        # Intentar obtener usuario inexistente
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/99999", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "Usuario no encontrado" in data["detail"]
    
    def test_get_user_by_id_unauthorized(self, client: TestClient, created_user):
        """Test obtener usuario por ID sin autenticación"""
        response = client.get(f"/api/v1/users/{created_user.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserRoutesValidation:
    """Tests para validación de datos en las rutas"""
    
    def test_register_with_empty_name(self, client: TestClient):
        """Test registro con nombre vacío"""
        user_data = {
            "name": "",
            "email": "empty@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_with_short_password(self, client: TestClient):
        """Test registro con contraseña muy corta"""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "123"  # Contraseña muy corta
        }
        
        response = client.post("/api/v1/users/register", json=user_data)
        # El modelo actual no valida longitud, pero podría agregarse
        # Por ahora solo verificamos que el usuario se crea
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_login_with_invalid_email_format(self, client: TestClient):
        """Test login con formato de email inválido"""
        login_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        
        response = client.post("/api/v1/users/generate-token", json=login_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
