import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

os.environ["AUTH_DISABLED"] = "true"


@pytest.fixture(scope="function")
def integration_db():
    """Create a test database for integration tests"""
    engine = create_engine("sqlite:///./test_integration.db")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        # Clean up test database
        import os
        if os.path.exists("test_integration.db"):
            os.remove("test_integration.db")

