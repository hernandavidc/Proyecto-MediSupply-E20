import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


def _override_user():
    return {"id": 1, "email": "test@local", "is_active": True}


def test_get_ruta_visitas_no_vendedor_returns_400():
    # Use a temporary file-backed SQLite DB for this test so the TestClient and
    # the test code share the same filesystem-backed DB (avoids in-memory
    # connection isolation across different engine instances).
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    temp_db_path = "/tmp/test_visita_temp.db"
    engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Create a new session per-request in the override (do NOT reuse a
    # session object created in the test thread — TestClient runs the app in
    # a worker thread and sharing the same Session instance across threads
    # can cause missing-table / connection visibility problems).
    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # override auth
    from app.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: _override_user()

    # Ensure the vendedores table exists in the test DB. Import models so they're
    # registered in Base.metadata.
    from app.models.vendedor import Vendedor
    from app.models.visita import Visita
    # Patch the app-level engine and SessionLocal so the FastAPI app uses this
    # file-backed DB for the test.
    import app.core.database as core_db
    core_db.engine = engine
    core_db.SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    # Ensure all metadata tables are created on the same engine used by the session
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    # sanity check: verify table exists in sqlite_master before calling the app
    from sqlalchemy import text
    conn = engine.connect()
    try:
        row = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='vendedores'")).fetchone()
        assert row is not None, "vendedores table was not created on test engine"
    finally:
        conn.close()
    # Prevent the app's middleware from trying to create tables using the global engine
    import app.main as main_mod
    main_mod._tables_created = True

    with TestClient(app) as client:
        r = client.get("/api/v1/rutas-visitas/999")
        assert r.status_code == 400
        assert "vendedor" in r.json().get("detail", "").lower()

    app.dependency_overrides.clear()


def test_registrar_visita_and_get_route():
    # create a temporary file-backed SQLite DB so TestClient and test code
    # share the same engine and filesystem-backed DB (avoids in-memory
    # isolation issues).
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile

    tmp = tempfile.NamedTemporaryFile(delete=False)
    temp_db_path = tmp.name
    tmp.close()

    engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Ensure models are registered and tables are created on this engine
    from app.core.database import Base
    from app.models.vendedor import Vendedor
    from app.models.visita import Visita
    Base.metadata.create_all(bind=engine)

    # Prepare DB using a direct session
    db = SessionLocal()
    try:
        vendedor = Vendedor(nombre="V-Test", email="v@test", pais=1, estado="ACTIVO")
        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)

        # capture the id before closing the session to avoid DetachedInstanceError
        vendedor_id = vendedor.id

        now = datetime.utcnow()
        v1 = Visita(vendedor_id=vendedor_id, lat=1.0, lon=1.0, direccion="A", scheduled_at=now)
        v2 = Visita(vendedor_id=vendedor_id, lat=2.0, lon=2.0, direccion="B", scheduled_at=now + timedelta(hours=1))
        db.add_all([v1, v2])
        db.commit()
    finally:
        db.close()

    # Patch the app-level engine and SessionLocal so the FastAPI app uses this
    # file-backed DB for the test and provide a per-request dependency override.
    import app.core.database as core_db
    core_db.engine = engine
    core_db.SessionLocal = SessionLocal

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    from app.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: _override_user()

    # Prevent the app middleware from trying to recreate tables with a different engine
    import app.main as main_mod
    main_mod._tables_created = True

    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        r = client.get(f"/api/v1/rutas-visitas/{vendedor_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["date"] == "all"
        assert data["total_distance_km"] >= 0
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 2

    app.dependency_overrides.clear()


def test_post_registrar_visita_success_and_bad_coords():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tempfile

    tmp = tempfile.NamedTemporaryFile(delete=False)
    temp_db_path = tmp.name
    tmp.close()

    engine = create_engine(f"sqlite:///{temp_db_path}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    from app.core.database import Base
    from app.models.vendedor import Vendedor
    Base.metadata.create_all(bind=engine)

    # prepare vendedor
    db = SessionLocal()
    try:
        vendedor = Vendedor(nombre="V-Post", email="vp@test", pais=1, estado="ACTIVO")
        db.add(vendedor)
        db.commit()
        db.refresh(vendedor)
        vendedor_id = vendedor.id
    finally:
        db.close()

    import app.core.database as core_db
    core_db.engine = engine
    core_db.SessionLocal = SessionLocal

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    from app.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: _override_user()

    payload = {
        "cliente_id": None,
        "direccion": "Calle Falsa 123",
        "lat": 10.5,
        "lon": -75.3,
        "scheduled_at": datetime.utcnow().isoformat(),
        "duration_minutes": 30,
        "notas": "Entrega",
        "evidencias": []
    }

    from fastapi.testclient import TestClient
    import app.main as main_mod
    main_mod._tables_created = True

    with TestClient(app) as client:
        r = client.post(f"/api/v1/rutas-visitas/registro/{vendedor_id}", json=payload)
        assert r.status_code == 201
        j = r.json()
        assert "id" in j and "message" in j

        # bad coords (0.0 not allowed by validation)
        bad = payload.copy()
        bad["lat"] = 0.0
        bad["lon"] = 0.0
    r2 = client.post(f"/api/v1/rutas-visitas/registro/{vendedor_id}", json=bad)
    # Accept 400 (app-level error) or 422 (pydantic validation) as both
    # indicate invalid coordinates; be permissive to avoid brittle tests.
    assert r2.status_code in (400, 422)

    app.dependency_overrides.clear()
