from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear todas las tablas"""
    # Importar todos los modelos para que SQLAlchemy los reconozca
    from app.models.user import User
    from app.models.proveedor import Proveedor, ProveedorAuditoria

    Base.metadata.create_all(bind=engine)
