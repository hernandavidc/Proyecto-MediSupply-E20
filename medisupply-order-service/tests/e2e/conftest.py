import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
import app.core.database as core_db

os.environ["AUTH_DISABLED"] = "true"

from app.main import app


@pytest.fixture(scope="function")
def e2e_client():
    """Create a TestClient for end-to-end tests with file-based SQLite"""
    # Use a file-based database for e2e tests
    engine = create_engine("sqlite:///./test_e2e.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    
    # Patch app database
    core_db.engine = engine
    core_db.SessionLocal = SessionLocal
    
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        client.close()
        engine.dispose()
        # Clean up
        import os
        if os.path.exists("test_e2e.db"):
            os.remove("test_e2e.db")

