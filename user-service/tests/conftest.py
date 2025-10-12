import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.auth import get_password_hash


# Configuración de base de datos para testing (SQLite en memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la función get_db para usar la base de datos de testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Fixture que proporciona una sesión de base de datos limpia para cada test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Fixture que proporciona un TestClient con la base de datos de testing"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Fixture con datos de usuario de prueba"""
    return {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "password": "password123"
    }


@pytest.fixture
def sample_user_create_data():
    """Fixture con datos para crear usuario"""
    return {
        "name": "María García",
        "email": "maria.garcia@example.com",
        "password": "securepassword456"
    }


@pytest.fixture
def created_user(db_session):
    """Fixture que crea un usuario en la base de datos para testing"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "is_active": True
    }
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def inactive_user(db_session):
    """Fixture que crea un usuario inactivo para testing"""
    user_data = {
        "name": "Inactive User",
        "email": "inactive@example.com",
        "hashed_password": get_password_hash("inactivepassword"),
        "is_active": False
    }
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user
