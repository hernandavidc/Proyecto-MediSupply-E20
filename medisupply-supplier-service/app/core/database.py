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
