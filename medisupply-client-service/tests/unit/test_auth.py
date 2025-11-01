import pytest
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.core.auth import verify_token, get_token_payload
from app.core.config import settings


def test_verify_valid_token():
    """Test que un token válido es verificado correctamente"""
    # Crear un token válido
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": "test@example.com", "exp": expire}
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Verificar el token
    email = verify_token(token)
    assert email == "test@example.com"


def test_verify_invalid_token():
    """Test que un token inválido retorna None"""
    invalid_token = "invalid.token.here"
    email = verify_token(invalid_token)
    assert email is None


def test_verify_token_with_wrong_secret():
    """Test que un token con diferente secret no es válido"""
    wrong_secret = "wrong_secret_key"
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": "test@example.com", "exp": expire}
    token = jwt.encode(token_data, wrong_secret, algorithm=settings.ALGORITHM)
    
    email = verify_token(token)
    assert email is None


def test_verify_expired_token():
    """Test que un token expirado retorna None"""
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
    token_data = {
        "sub": "test@example.com",
        "exp": expired_time
    }
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    email = verify_token(token)
    assert email is None


def test_verify_token_without_sub_claim():
    """Test que un token sin claim 'sub' retorna None"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"exp": expire}  # Sin 'sub'
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    email = verify_token(token)
    assert email is None


def test_get_token_payload_valid():
    """Test obtener payload de token válido"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    token_data = {"sub": "test@example.com", "exp": expire}
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    payload = get_token_payload(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"


def test_get_token_payload_invalid():
    """Test obtener payload de token inválido retorna None"""
    invalid_token = "invalid.token.here"
    payload = get_token_payload(invalid_token)
    assert payload is None

