from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.core.database import engine, Base as _Base
    # Import models so they are registered in metadata
    from app.models import (
        Orden, Vehiculo, OrdenProducto, 
        Bodega, BodegaProducto, NovedadOrden
    )
    try:
        _Base.metadata.create_all(bind=engine)
    except Exception:
        raise
