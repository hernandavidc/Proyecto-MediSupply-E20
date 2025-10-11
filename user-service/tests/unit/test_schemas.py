import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user_schema import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token, 
    TokenData,
    HealthCheck
)


class TestUserSchemas:
    """Tests para los schemas de usuario"""
    
    def test_user_create_valid_data(self):
        """Test UserCreate con datos válidos"""
        user_data = {
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        
        assert user.name == "Juan Pérez"
        assert user.email == "juan@example.com"
        assert user.password == "password123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate con email inválido"""
        user_data = {
            "name": "Juan Pérez",
            "email": "invalid-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_user_create_missing_fields(self):
        """Test UserCreate con campos faltantes"""
        user_data = {
            "name": "Juan Pérez",
            # "email": "juan@example.com",  # Email faltante
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "field required" in str(exc_info.value)
    
    def test_user_login_valid_data(self):
        """Test UserLogin con datos válidos"""
        login_data = {
            "email": "user@example.com",
            "password": "password123"
        }
        
        user_login = UserLogin(**login_data)
        
        assert user_login.email == "user@example.com"
        assert user_login.password == "password123"
    
    def test_user_login_invalid_email(self):
        """Test UserLogin con email inválido"""
        login_data = {
            "email": "not-an-email",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(**login_data)
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_user_response_valid_data(self):
        """Test UserResponse con datos válidos"""
        response_data = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "is_active": True,
            "created_at": datetime.now()
        }
        
        user_response = UserResponse(**response_data)
        
        assert user_response.id == 1
        assert user_response.name == "Test User"
        assert user_response.email == "test@example.com"
        assert user_response.is_active is True
        assert isinstance(user_response.created_at, datetime)
    
    def test_token_schema(self):
        """Test Token schema"""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
        token = Token(**token_data)
        
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
    
    def test_token_data_schema(self):
        """Test TokenData schema"""
        # Con email
        token_data = TokenData(email="test@example.com")
        assert token_data.email == "test@example.com"
        
        # Sin email (None por defecto)
        token_data_empty = TokenData()
        assert token_data_empty.email is None
    
    def test_health_check_schema(self):
        """Test HealthCheck schema"""
        health_data = {
            "status": "healthy",
            "message": "Service is running",
            "timestamp": datetime.now()
        }
        
        health_check = HealthCheck(**health_data)
        
        assert health_check.status == "healthy"
        assert health_check.message == "Service is running"
        assert isinstance(health_check.timestamp, datetime)
    
    def test_user_create_with_special_characters(self):
        """Test UserCreate con caracteres especiales"""
        user_data = {
            "name": "María José Pérez-García",
            "email": "maria.jose@compañía.com",
            "password": "contraseña123!@#"
        }
        
        user = UserCreate(**user_data)
        
        assert user.name == "María José Pérez-García"
        assert user.email == "maria.jose@compañía.com"
        assert user.password == "contraseña123!@#"
    
    def test_user_create_name_edge_cases(self):
        """Test UserCreate con casos límite de nombre"""
        # Nombre muy corto
        user_data_short = {
            "name": "A",
            "email": "a@example.com",
            "password": "password123"
        }
        
        user_short = UserCreate(**user_data_short)
        assert user_short.name == "A"
        
        # Nombre muy largo
        long_name = "A" * 200
        user_data_long = {
            "name": long_name,
            "email": "long@example.com",
            "password": "password123"
        }
        
        user_long = UserCreate(**user_data_long)
        assert user_long.name == long_name
    
    def test_user_response_serialization(self):
        """Test serialización de UserResponse"""
        response_data = {
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "is_active": True,
            "created_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user_response = UserResponse(**response_data)
        
        # Test dict serialization
        user_dict = user_response.model_dump()
        
        assert user_dict["id"] == 1
        assert user_dict["name"] == "Test User"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["is_active"] is True
        assert user_dict["created_at"] == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_user_create_password_edge_cases(self):
        """Test UserCreate con casos límite de contraseña"""
        # Contraseña muy corta
        user_data_short = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "1"
        }
        
        user_short = UserCreate(**user_data_short)
        assert user_short.password == "1"
        
        # Contraseña muy larga
        long_password = "a" * 1000
        user_data_long = {
            "name": "Test User",
            "email": "test@example.com",
            "password": long_password
        }
        
        user_long = UserCreate(**user_data_long)
        assert user_long.password == long_password
