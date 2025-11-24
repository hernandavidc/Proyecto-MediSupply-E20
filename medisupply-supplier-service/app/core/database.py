from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine with connection pooling and automatic reconnection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para los modelos
Base = declarative_base()


# Dependencia común para obtener la sesión en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear tablas declaradas en los modelos usando la metadata de SQLAlchemy.

    Esta función es una utilidad compatible con otros servicios del monorepo
    que esperan `create_tables()` en `app.core.database`.
    """
    from app.core.database import engine, Base as _Base
    # Importar modelos para que las tablas se registren en la metadata
    # (si los modelos están definidos en módulos importados por los paquetes)
    try:
        _Base.metadata.create_all(bind=engine)
    except Exception:
        # Re-raise to let el llamador manejar los retries/logging
        raise

    # --- Compatibility: ensure `user_id` column exists on `vendedores` table ---
    # Some deployments create the DB before code changes; add column if missing.
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if 'vendedores' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('vendedores')]
            if 'user_id' not in cols:
                with engine.begin() as conn:
                    # Add nullable integer column and an index for lookups
                    conn.execute(text('ALTER TABLE vendedores ADD COLUMN user_id INTEGER'))
                    try:
                        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_vendedores_user_id ON vendedores (user_id)'))
                    except Exception:
                        # index creation non-fatal
                        pass
        # --- Compatibility: ensure `user_id` column exists on `clientes` table ---
        if 'clientes' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('clientes')]
            if 'user_id' not in cols:
                with engine.begin() as conn:
                    conn.execute(text('ALTER TABLE clientes ADD COLUMN user_id INTEGER'))
                    try:
                        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_clientes_user_id ON clientes (user_id)'))
                    except Exception:
                        pass
    except Exception:
        # Non-fatal: don't block table creation on schema adjustments
        pass
