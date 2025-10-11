import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.models.user import User
from app.core.auth import get_password_hash


class TestUserService:
    """Tests para UserService"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_db = Mock(spec=Session)
        self.user_service = UserService(self.mock_db)
    
    def test_init(self):
        """Test que UserService se inicializa correctamente"""
        assert self.user_service.db == self.mock_db
    
    @patch('app.services.user_service.get_password_hash')
    def test_create_user_success(self, mock_hash):
        """Test crear usuario exitosamente"""
        # Configurar mocks
        mock_hash.return_value = "hashed_password"
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Crear usuario mock que será devuelto después del commit
        created_user_mock = Mock()
        created_user_mock.id = 1
        created_user_mock.name = "Juan Pérez"
        created_user_mock.email = "juan@example.com"
        created_user_mock.is_active = True
        created_user_mock.created_at = "2023-01-01T00:00:00"
        
        self.mock_db.refresh.side_effect = lambda user: setattr(user, 'id', 1) or setattr(user, 'created_at', "2023-01-01T00:00:00")
        
        # Datos de entrada
        user_data = UserCreate(
            name="Juan Pérez",
            email="juan@example.com",
            password="password123"
        )
        
        # Ejecutar
        with patch.object(self.user_service, 'db') as mock_db:
            mock_db.query.return_value.filter.return_value.first.return_value = None
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.refresh = Mock(side_effect=lambda user: [
                setattr(user, 'id', 1),
                setattr(user, 'is_active', True),
                setattr(user, 'created_at', "2023-01-01T00:00:00")
            ])
            
            result = self.user_service.create_user(user_data)
        
        # Verificar
        mock_hash.assert_called_once_with("password123")
        assert isinstance(result, UserResponse)
        assert result.name == "Juan Pérez"
        assert result.email == "juan@example.com"
    
    def test_create_user_email_already_exists(self):
        """Test crear usuario con email ya existente"""
        # Configurar mock para email existente
        existing_user_mock = Mock()
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_user_mock
        
        user_data = UserCreate(
            name="Juan Pérez",
            email="juan@example.com",
            password="password123"
        )
        
        # Verificar que se lanza excepción
        with pytest.raises(HTTPException) as exc_info:
            self.user_service.create_user(user_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "El email ya está registrado" in str(exc_info.value.detail)
    
    @patch('app.services.user_service.verify_password')
    def test_authenticate_user_success(self, mock_verify):
        """Test autenticación exitosa"""
        mock_verify.return_value = True
        
        # Mock del usuario encontrado
        user_mock = Mock()
        user_mock.email = "test@example.com"
        user_mock.hashed_password = "hashed_password"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = user_mock
        
        result = self.user_service.authenticate_user("test@example.com", "password123")
        
        assert result == user_mock
        mock_verify.assert_called_once_with("password123", "hashed_password")
    
    def test_authenticate_user_user_not_found(self):
        """Test autenticación con usuario no encontrado"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_service.authenticate_user("test@example.com", "password123")
        
        assert result is None
    
    @patch('app.services.user_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify):
        """Test autenticación con contraseña incorrecta"""
        mock_verify.return_value = False
        
        user_mock = Mock()
        user_mock.email = "test@example.com"
        user_mock.hashed_password = "hashed_password"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = user_mock
        
        result = self.user_service.authenticate_user("test@example.com", "wrong_password")
        
        assert result is None
        mock_verify.assert_called_once_with("wrong_password", "hashed_password")
    
    @patch('app.services.user_service.create_access_token')
    def test_login_user_success(self, mock_create_token):
        """Test login exitoso"""
        mock_create_token.return_value = "access_token_123"
        
        # Mock del usuario autenticado
        user_mock = Mock()
        user_mock.email = "test@example.com"
        user_mock.is_active = True
        
        with patch.object(self.user_service, 'authenticate_user') as mock_auth:
            mock_auth.return_value = user_mock
            
            user_login = UserLogin(email="test@example.com", password="password123")
            result = self.user_service.login_user(user_login)
        
        assert result == {
            "access_token": "access_token_123",
            "token_type": "bearer"
        }
        mock_create_token.assert_called_once_with(data={"sub": "test@example.com"})
    
    def test_login_user_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        with patch.object(self.user_service, 'authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            user_login = UserLogin(email="test@example.com", password="wrong_password")
            
            with pytest.raises(HTTPException) as exc_info:
                self.user_service.login_user(user_login)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Email o contraseña incorrectos" in str(exc_info.value.detail)
    
    @patch('app.services.user_service.create_access_token')
    def test_login_user_inactive(self, mock_create_token):
        """Test login con usuario inactivo"""
        user_mock = Mock()
        user_mock.email = "test@example.com"
        user_mock.is_active = False
        
        with patch.object(self.user_service, 'authenticate_user') as mock_auth:
            mock_auth.return_value = user_mock
            
            user_login = UserLogin(email="test@example.com", password="password123")
            
            with pytest.raises(HTTPException) as exc_info:
                self.user_service.login_user(user_login)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Usuario inactivo" in str(exc_info.value.detail)
    
    def test_get_user_by_email_found(self):
        """Test obtener usuario por email - encontrado"""
        user_mock = Mock()
        user_mock.email = "test@example.com"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = user_mock
        
        result = self.user_service.get_user_by_email("test@example.com")
        
        assert result == user_mock
    
    def test_get_user_by_email_not_found(self):
        """Test obtener usuario por email - no encontrado"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.user_service.get_user_by_email("test@example.com")
        
        assert result is None
    
    def test_get_user_success(self):
        """Test obtener usuario por ID exitosamente"""
        user_mock = Mock()
        user_mock.id = 1
        user_mock.name = "Test User"
        user_mock.email = "test@example.com"
        user_mock.is_active = True
        user_mock.created_at = "2023-01-01T00:00:00"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = user_mock
        
        result = self.user_service.get_user(1)
        
        assert isinstance(result, UserResponse)
        assert result.id == 1
        assert result.name == "Test User"
        assert result.email == "test@example.com"
        assert result.is_active == True
        assert result.created_at == datetime(2023, 1, 1, 0, 0)
    
    def test_get_user_not_found(self):
        """Test obtener usuario por ID - no encontrado"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            self.user_service.get_user(999)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Usuario no encontrado" in str(exc_info.value.detail)


class TestUserServiceIntegration:
    """Tests de integración para UserService con base de datos real"""
    
    def test_create_and_get_user_flow(self, db_session):
        """Test del flujo completo: crear y obtener usuario"""
        user_service = UserService(db_session)
        
        # Crear usuario
        user_data = UserCreate(
            name="Integration Test User",
            email="integration@example.com",
            password="testpassword123"
        )
        
        created_user = user_service.create_user(user_data)
        
        # Verificar usuario creado
        assert created_user.name == "Integration Test User"
        assert created_user.email == "integration@example.com"
        assert created_user.is_active is True
        assert created_user.id is not None
        
        # Obtener usuario creado
        retrieved_user = user_service.get_user(created_user.id)
        
        assert retrieved_user.id == created_user.id
        assert retrieved_user.name == created_user.name
        assert retrieved_user.email == created_user.email
    
    def test_authenticate_and_login_flow(self, db_session):
        """Test del flujo completo: autenticación y login"""
        user_service = UserService(db_session)
        
        # Crear usuario
        user_data = UserCreate(
            name="Auth Test User",
            email="auth@example.com",
            password="authpassword123"
        )
        
        user_service.create_user(user_data)
        
        # Autenticar usuario
        authenticated_user = user_service.authenticate_user(
            "auth@example.com", 
            "authpassword123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.email == "auth@example.com"
        
        # Login del usuario
        login_data = UserLogin(
            email="auth@example.com",
            password="authpassword123"
        )
        
        login_result = user_service.login_user(login_data)
        
        assert "access_token" in login_result
        assert "token_type" in login_result
        assert login_result["token_type"] == "bearer"
    
    def test_duplicate_email_prevention(self, db_session):
        """Test que no se pueden crear usuarios con email duplicado"""
        user_service = UserService(db_session)
        
        # Crear primer usuario
        user_data1 = UserCreate(
            name="First User",
            email="duplicate@example.com",
            password="password1"
        )
        
        user_service.create_user(user_data1)
        
        # Intentar crear segundo usuario con mismo email
        user_data2 = UserCreate(
            name="Second User",
            email="duplicate@example.com",
            password="password2"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(user_data2)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
