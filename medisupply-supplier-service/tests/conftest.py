import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base


@pytest.fixture
def db_session():
    """Shared db_session fixture that ensures engine disposal to avoid ResourceWarning.

    Creates a fresh in-memory SQLite DB for each test function and guarantees
    the SQLAlchemy engine is disposed after the test.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception:
            pass
        try:
            engine.dispose()
        except Exception:
            pass
