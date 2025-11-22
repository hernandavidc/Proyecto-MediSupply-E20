from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create engine with connection pooling and automatic reconnection
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True for SQL debugging
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
    """Crear todas las tablas"""
    # Importar todos los modelos para que SQLAlchemy los reconozca
    from app.models.user import User
    from app.models.role import Role

    Base.metadata.create_all(bind=engine)

    # Ensure role_id column exists on users table (useful when schema evolved over time)
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('users')]
            if 'role_id' not in cols:
                with engine.begin() as conn:
                    conn.execute(text('ALTER TABLE users ADD COLUMN role_id INTEGER'))
                    # Try to add FK constraint; ignore on failure
                    try:
                        conn.execute(text('ALTER TABLE users ADD CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id)'))
                    except Exception:
                        pass
    except Exception:
        pass

    # Seed default roles if missing
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        existing = session.query(Role).count()
        if existing == 0:
            default_roles = ['Admin', 'Cliente', 'Vendedor', 'Conductor']
            for r in default_roles:
                role = Role(name=r)
                session.add(role)
            session.commit()
        session.close()
    except Exception:
        # Non-fatal: if seeding fails (e.g., permissions) we won't block table creation
        pass
