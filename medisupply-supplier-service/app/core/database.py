from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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
    # Importar modelos para registrar metadatos
    try:
        from app.models.proveedor import Proveedor, ProveedorAuditoria
        from app.models.catalogs import Pais, Certificacion, CategoriaSuministro
        # incluir modelos de productos y otros dominios para que se creen las tablas
        from app.models.product import Producto, ProductoAuditoria
        from app.models.plan_venta import PlanVenta, PlanVentaAuditoria
        from app.models.vendedor import Vendedor, VendedorAuditoria

        Base.metadata.create_all(bind=engine)
        # Seed minimal catalog data si aún no existe
        db = SessionLocal()
        try:
            if db.query(Pais).count() == 0:
                db.add_all([
                    Pais(id=1, nombre='Colombia'),
                    Pais(id=2, nombre='Perú'),
                    Pais(id=3, nombre='Ecuador'),
                    Pais(id=4, nombre='México'),
                ])
            if db.query(Certificacion).count() == 0:
                db.add_all([
                    Certificacion(id=1, codigo='FDA', nombre='FDA (Food and Drug Administration)'),
                    Certificacion(id=2, codigo='EMA', nombre='EMA (European Medicines Agency)'),
                    Certificacion(id=3, codigo='INVIMA', nombre='INVIMA (Instituto Nacional de Vigilancia de Medicamentos y Alimentos)'),
                    Certificacion(id=4, codigo='DIGEMID', nombre='DIGEMID'),
                    Certificacion(id=5, codigo='COFEPRIS', nombre='COFEPRIS'),
                ])
            if db.query(CategoriaSuministro).count() == 0:
                db.add_all([
                    CategoriaSuministro(id=1, nombre='Medicamentos especiales'),
                    CategoriaSuministro(id=2, nombre='Medicamentos controlados'),
                    CategoriaSuministro(id=3, nombre='Insumos quirurgicos y hospitalarios'),
                    CategoriaSuministro(id=4, nombre='Insumos reactivos'),
                    CategoriaSuministro(id=5, nombre='Pruebas diagnosticas'),
                    CategoriaSuministro(id=6, nombre='Equipos y dispositivos biomédicos'),
                    CategoriaSuministro(id=7, nombre='Otros (PPE, Materiales varios)'),
                ])
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass
    except Exception:
        # Si los modelos no están disponibles al import, simplemente retornar
        return


# Importar modelos a nivel de módulo para asegurar que Base.metadata
# contenga todas las tablas cuando se ejecute Base.metadata.create_all()
try:
    # modelos principales
    import app.models.proveedor  # noqa: F401
    import app.models.catalogs   # noqa: F401
    import app.models.product    # noqa: F401
    import app.models.plan_venta # noqa: F401
    import app.models.vendedor   # noqa: F401
except Exception:
    # evitar fallos en entornos donde algunos modelos aún no estén disponibles
    pass
