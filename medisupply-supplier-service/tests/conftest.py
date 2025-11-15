import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
import app.core.database as core_db
# Disable auth for tests so middleware always allows requests during CI/test runs
os.environ.setdefault("AUTH_DISABLED", "true")

from app.main import app


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


@pytest.fixture
def client():
    """Create a TestClient backed by an in-memory SQLite DB (StaticPool).

    Using StaticPool + check_same_thread=False lets the TestClient (app
    running in worker threads) and the test code share the same connection
    so tables and data are visible across threads.
    """
    # create an in-memory engine that can be shared across threads
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # create tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)

    # patch app-level engine and SessionLocal so the FastAPI app uses this test DB
    core_db.engine = engine
    core_db.SessionLocal = SessionLocal

    # per-request dependency override
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # yield client
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        try:
            client.close()
        except Exception:
            pass
        try:
            engine.dispose()
        except Exception:
            pass
