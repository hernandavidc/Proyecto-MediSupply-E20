import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.dependencies import get_current_user_email, get_current_user_info
from app.core.auth import verify_token, get_token_payload
from app.core.config import settings


def create_test_token(email: str, expires_in_minutes: int = 30) -> str:
    """Helper to create test JWT tokens"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    token_data = {"sub": email, "exp": expire}
    return jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class TestVerifyToken:
    """Test verify_token function"""
    
    def test_verify_token_valid(self):
        """Test verifying a valid token"""
        token = create_test_token("test@example.com")
        
        result = verify_token(token)
        
        assert result is not None
        assert result["sub"] == "test@example.com"
    
    def test_verify_token_invalid(self):
        """Test verifying an invalid token"""
        result = verify_token("invalid.token.here")
        
        assert result is None
    
    def test_verify_token_expired(self):
        """Test verifying an expired token"""
        # Create token that expired 1 hour ago
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        token_data = {"sub": "test@example.com", "exp": expire}
        expired_token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        result = verify_token(expired_token)
        
        assert result is None
    
    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret"""
        # Create token with different secret
        token_data = {"sub": "test@example.com"}
        wrong_token = jwt.encode(token_data, "wrong_secret", algorithm=settings.ALGORITHM)
        
        result = verify_token(wrong_token)
        
        assert result is None
    
    def test_verify_token_missing_sub(self):
        """Test verifying token without sub claim"""
        token_data = {"email": "test@example.com"}  # Wrong claim
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        result = verify_token(token)
        
        # Token is technically valid but we check sub claim elsewhere
        assert result is not None


class TestGetCurrentUserEmail:
    """Test get_current_user_email dependency"""
    
    def test_get_current_user_email_valid_token(self):
        """Test getting current user email with valid token"""
        token = create_test_token("test@example.com")
        
        email = get_current_user_email(token)
        
        assert email == "test@example.com"
    
    def test_get_current_user_email_invalid_token(self):
        """Test getting current user email with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_email("invalid.token.here")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_email_expired_token(self):
        """Test getting current user email with expired token"""
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        token_data = {"sub": "test@example.com", "exp": expire}
        expired_token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_email(expired_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUserInfo:
    """Test get_current_user_info dependency"""
    
    def test_get_current_user_info_valid_token(self):
        """Test getting current user info with valid token"""
        token = create_test_token("test@example.com")
        
        info = get_current_user_info(token)
        
        assert info is not None
        assert info["sub"] == "test@example.com"
    
    def test_get_current_user_info_invalid_token(self):
        """Test getting current user info with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_info("invalid.token.here")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_info_expired_token(self):
        """Test getting current user info with expired token"""
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        token_data = {"sub": "test@example.com", "exp": expire}
        expired_token = jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_info(expired_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

