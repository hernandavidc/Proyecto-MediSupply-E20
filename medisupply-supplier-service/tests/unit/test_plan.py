import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.plan_service import PlanService
from app.services.proveedor_service import ProveedorService
from app.services.product_service import ProductService

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

def test_create_plan_success(db_session):
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "ProvPlan", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    prod = prod_service.crear_producto({"sku": "SKU1", "nombre_producto": "P1", "proveedor_id": prov.id, "valor_unitario_usd": 1.23, "certificaciones": [1]}, usuario_id=1)
    plan_service = PlanService(db_session)
    data = {"vendedor_id": 10, "periodo": "Q3", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id], "meta_monetaria_usd": 1000}
    plan = plan_service.crear_plan(data, usuario_id=2)
    assert plan.id is not None

def test_duplicate_plan_rejected(db_session):
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "ProvPlan2", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    prod = prod_service.crear_producto({"sku": "SKU2", "nombre_producto": "P2", "proveedor_id": prov.id, "valor_unitario_usd": 2.00, "certificaciones": [1]}, usuario_id=1)
    plan_service = PlanService(db_session)
    data = {"vendedor_id": 11, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}
    plan_service.crear_plan(data, usuario_id=3)
    with pytest.raises(ValueError):
        plan_service.crear_plan(data, usuario_id=3)

def test_delete_blocked_when_in_execution(db_session):
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "ProvPlan3", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    prod = prod_service.crear_producto({"sku": "SKU3", "nombre_producto": "P3", "proveedor_id": prov.id, "valor_unitario_usd": 3.00, "certificaciones": [1]}, usuario_id=1)
    plan_service = PlanService(db_session)
    data = {"vendedor_id": 12, "periodo": "Q2", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}
    plan = plan_service.crear_plan(data, usuario_id=4)
    # simular plan en ejecucion
    plan.estado = 'EN_EJECUCION'
    db_session.add(plan)
    db_session.commit()
    with pytest.raises(ValueError):
        plan_service.eliminar_plan(plan)
