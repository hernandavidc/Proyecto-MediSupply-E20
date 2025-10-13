import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token
)


class TestPasswordHashing:
    """Tests para funciones de hash de contraseñas"""
    
    def test_get_password_hash_returns_different_hash_for_same_password(self):
        """Test que el hash es diferente cada vez (por el salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_verify_password_with_correct_password(self):
        """Test que verify_password funciona con contraseña correcta"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_incorrect_password(self):
        """Test que verify_password falla con contraseña incorrecta"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_get_password_hash_with_empty_string(self):
        """Test que se puede hacer hash de string vacío"""
        password = ""
        hashed = get_password_hash(password)
        
        assert len(hashed) > 0
        assert verify_password(password, hashed) is True
    
    def test_get_password_hash_with_long_password(self):
        """Test que contraseñas muy largas son truncadas correctamente"""
        # Crear contraseña de más de 72 bytes
        password = "a" * 100
        hashed = get_password_hash(password)
        
        assert len(hashed) > 0
        # Verificar que la contraseña truncada funciona
        truncated_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        assert verify_password(truncated_password, hashed) is True
    
    def test_get_password_hash_with_unicode_characters(self):
        """Test que funciona con caracteres unicode"""
        password = "contraseña123ñáéíóú"
        hashed = get_password_hash(password)
        
        assert len(hashed) > 0
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests para funciones de tokens JWT"""
    
    @patch('app.core.auth.settings')
    def test_create_access_token_with_default_expiration(self, mock_settings):
        """Test crear token JWT con expiración por defecto"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar token para verificar contenido
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload
    
    @patch('app.core.auth.settings')
    def test_create_access_token_with_custom_expiration(self, mock_settings):
        """Test crear token JWT con expiración personalizada"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        
        # Verificar que la expiración es aproximadamente 60 minutos desde ahora
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires_delta
        
        # Permitir una diferencia de 5 segundos
        assert abs((exp_datetime - expected_exp).total_seconds()) < 5
    
    @patch('app.core.auth.settings')
    def test_verify_token_with_valid_token(self, mock_settings):
        """Test verificar token JWT válido"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        result = verify_token(token)
        assert result == "test@example.com"
    
    @patch('app.core.auth.settings')
    def test_verify_token_with_invalid_signature(self, mock_settings):
        """Test verificar token JWT con firma inválida"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        # Crear token con una clave diferente
        wrong_key_token = jwt.encode(
            {"sub": "test@example.com"}, 
            "wrong_secret_key", 
            algorithm="HS256"
        )
        
        result = verify_token(wrong_key_token)
        assert result is None
    
    @patch('app.core.auth.settings')
    def test_verify_token_with_expired_token(self, mock_settings):
        """Test verificar token JWT expirado"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        # Crear token expirado
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        data = {"sub": "test@example.com", "exp": expired_time}
        expired_token = jwt.encode(data, "test_secret_key", algorithm="HS256")
        
        result = verify_token(expired_token)
        assert result is None
    
    @patch('app.core.auth.settings')
    def test_verify_token_without_sub_claim(self, mock_settings):
        """Test verificar token JWT sin claim 'sub'"""
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        # Crear token sin 'sub'
        data = {"user_id": 123}
        token = jwt.encode(data, "test_secret_key", algorithm="HS256")
        
        result = verify_token(token)
        assert result is None
    
    def test_verify_token_with_malformed_token(self):
        """Test verificar token JWT malformado"""
        malformed_token = "this.is.not.a.valid.jwt.token"
        
        result = verify_token(malformed_token)
        assert result is None
    
    def test_verify_token_with_empty_token(self):
        """Test verificar token JWT vacío"""
        result = verify_token("")
        assert result is None
