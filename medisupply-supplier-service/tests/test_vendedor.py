import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.vendedor_service import VendedorService
from app.services.plan_service import PlanService

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_vendedor_success(db_session):
    service = VendedorService(db_session)
    v = service.crear_vendedor({"nombre": "Vendedor 1", "email": "v1@company.com", "pais": 1, "estado": "ACTIVO"}, usuario_id=1)
    assert v.id is not None

def test_duplicate_email_rejected(db_session):
    service = VendedorService(db_session)
    service.crear_vendedor({"nombre": "V2", "email": "v2@company.com", "pais": 1, "estado": "ACTIVO"})
    with pytest.raises(ValueError):
        service.crear_vendedor({"nombre": "V2b", "email": "v2@company.com", "pais": 1, "estado": "ACTIVO"})

def test_delete_blocked_when_has_plans(db_session):
    vend_service = VendedorService(db_session)
    plan_service = PlanService(db_session)
    v = vend_service.crear_vendedor({"nombre": "V3", "email": "v3@company.com", "pais": 1, "estado": "ACTIVO"})
    # crear producto y plan para vincular
    # crear producto dummy
    # producto no necesita proveedor en esta prueba; usar plan de prueba con productos_objetivo empty avoided
    # crear un producto real via product service
    from app.services.proveedor_service import ProveedorService
    from app.services.product_service import ProductService
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "ProvV", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    prod = prod_service.crear_producto({"sku": "SKUV", "nombre_producto": "P-V", "proveedor_id": prov.id, "valor_unitario_usd": 1.0, "certificaciones": [1]}, usuario_id=1)
    plan = plan_service.crear_plan({"vendedor_id": v.id, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=2)
    with pytest.raises(ValueError):
        vend_service.eliminar_vendedor(v)
