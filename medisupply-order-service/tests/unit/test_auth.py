import pytest
from app.core.auth import verify_token_with_user_service
from app.core.dependencies import get_current_user
from fastapi import HTTPException, Request
from unittest.mock import Mock, patch


def test_verify_token_with_user_service_valid():
    """Test token verification with valid token"""
    with patch('app.core.auth.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.return_value = mock_response
        
        result = verify_token_with_user_service("valid_token")
        assert result is not None
        assert result["email"] == "test@example.com"


def test_verify_token_with_user_service_invalid():
    """Test token verification with invalid token"""
    with patch('app.core.auth.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = verify_token_with_user_service("invalid_token")
        assert result is None


def test_verify_token_with_user_service_connection_error():
    """Test token verification when user service is unavailable"""
    with patch('app.core.auth.requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        
        result = verify_token_with_user_service("some_token")
        assert result is None


def test_get_current_user_with_auth_disabled():
    """Test get_current_user when AUTH_DISABLED=true"""
    import os
    os.environ["AUTH_DISABLED"] = "true"
    
    mock_request = Mock(spec=Request)
    user = get_current_user(mock_request, None)
    
    assert user is not None
    assert user["email"] == "test@local"


def test_get_current_user_without_credentials():
    """Test get_current_user without credentials raises exception"""
    import os
    os.environ["AUTH_DISABLED"] = "false"
    
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.user = None
    mock_request.headers.get.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(mock_request, None)
    
    assert exc_info.value.status_code == 401

