import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database for each test
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database dependency override
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_client_data():
    """
    Sample client data for testing
    """
    return {
        "nombre": "Test Company S.A.",
        "nit": "1234567890",
        "direccion": "123 Test Street, Test City",
        "nombre_contacto": "John Doe",
        "telefono_contacto": "+1234567890",
        "email_contacto": "john.doe@testcompany.com"
    }


@pytest.fixture
def test_token():
    """
    Helper fixture to create a valid JWT token for testing
    """
    def _create_token(email: str = "test@example.com", expires_in_minutes: int = 30) -> str:
        """
        Create a test JWT token
        
        Args:
            email: Email to include in token (sub claim)
            expires_in_minutes: Token expiration time in minutes
            
        Returns:
            str: Valid JWT token
        """
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        token_data = {
            "sub": email,
            "exp": expire
        }
        return jwt.encode(
            token_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    return _create_token


@pytest.fixture
def auth_headers(test_token):
    """
    Fixture that provides authentication headers with a valid token
    """
    token = test_token("test@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_user_service(httpx_mock):
    """
    Mock user-service HTTP calls using pytest-httpx
    """
    from app.core.config import settings
    
    # Mock roles endpoint
    httpx_mock.add_response(
        url=f"{settings.USER_SERVICE_URL}/api/v1/roles",
        method="GET",
        json=[
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Cliente"},
            {"id": 3, "name": "Vendedor"}
        ],
        status_code=200
    )
    
    # Mock user registration endpoint (any email)
    httpx_mock.add_response(
        url__regex=f"{settings.USER_SERVICE_URL}/api/v1/users/register",
        method="POST",
        json={
            "id": 1,
            "email": "test@example.com",
            "role_id": 2,
            "is_active": True
        },
        status_code=201
    )
    
    return httpx_mock

