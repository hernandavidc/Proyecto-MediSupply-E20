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
        from app.models.client import Cliente

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
            # seed minimal vendedores if not present (needed for client assignment)
            if db.query(Vendedor).count() == 0:
                db.add_all([
                    Vendedor(id=1, nombre='Vendedor Uno', email='v1@example.com', pais=1),
                    Vendedor(id=2, nombre='Vendedor Dos', email='v2@example.com', pais=1),
                ])

            # seed dummy clientes associated with vendedores (read-only via API)
            # Distribute clients across all existing vendedores so any vendedor created
            # (e.g. via API) can have seeded clients when the DB is initialized.
            if db.query(Cliente).count() == 0:
                # ensure we have at least the minimal vendedores in DB
                db.commit()  # commit potential new vendedores so they are queryable
                vendors = db.query(Vendedor).all()
                vendor_ids = [v.id for v in vendors] if vendors else [1, 2]
                clientes = []
                total_clients = 20
                for i in range(1, total_clients + 1):
                    # round-robin assign across available vendor ids
                    vid = vendor_ids[(i - 1) % len(vendor_ids)]
                    clientes.append(Cliente(
                        id=i,
                        vendedor_id=vid,
                        institucion_nombre=f'Institucion {i}',
                        direccion=f'Calle {i} # {i} - Centro',
                        contacto_principal=f'Contacto {i} (+57)30000000{i:02d}'
                    ))
                db.add_all(clientes)

            # seed proveedores if not present (needed for products)
            if db.query(Proveedor).count() == 0:
                db.add_all([
                    Proveedor(
                        id=1,
                        razon_social="Farmacéutica Internacional S.A.S",
                        paises_operacion=[1, 2, 3],  # Colombia, Perú, Ecuador
                        certificaciones_sanitarias=[1, 2, 3],  # FDA, EMA, INVIMA
                        categorias_suministradas=[1, 2],  # Medicamentos especiales y controlados
                        capacidad_cadena_frio=["REFRIGERADO", "CONGELADO_NORMAL"],
                        estado="APROBADO"
                    ),
                    Proveedor(
                        id=2,
                        razon_social="MedSupply Global Ltda",
                        paises_operacion=[1, 4],  # Colombia, México
                        certificaciones_sanitarias=[2, 4, 5],  # EMA, DIGEMID, COFEPRIS
                        categorias_suministradas=[3, 4],  # Insumos quirúrgicos y reactivos
                        capacidad_cadena_frio=None,
                        estado="APROBADO"
                    ),
                    Proveedor(
                        id=3,
                        razon_social="BioMedical Solutions Inc",
                        paises_operacion=[1],  # Colombia
                        certificaciones_sanitarias=[1, 3],  # FDA, INVIMA
                        categorias_suministradas=[5, 6],  # Pruebas diagnósticas y equipos
                        capacidad_cadena_frio=["REFRIGERADO"],
                        estado="APROBADO"
                    ),
                ])
                print("✅ Proveedores inicializados")

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
