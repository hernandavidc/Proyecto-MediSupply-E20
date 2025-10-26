import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.plan_service import PlanService
from app.services.product_service import ProductService
from app.services.vendedor_service import VendedorService
from app.services.proveedor_service import ProveedorService


def test_crear_plan_success(db_session):
    vend_svc = VendedorService(db_session)
    v = vend_svc.crear_vendedor({"nombre": "Vplan", "email": "vp@x.com", "pais": 1, "estado": "ACTIVO"})
    prov_svc = ProveedorService(db_session)
    prov = prov_svc.crear_proveedor({"razon_social": "ProvP", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_svc = ProductService(db_session)
    prod = prod_svc.crear_producto({"sku": "SP", "nombre_producto": "ProdP", "proveedor_id": prov.id, "valor_unitario_usd": 2.0, "certificaciones": [1]}, usuario_id=1)

    plan_svc = PlanService(db_session)
    plan = plan_svc.crear_plan({"vendedor_id": v.id, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=3)
    assert plan.id is not None


def test_crear_plan_missing_products_raises(db_session):
    plan_svc = PlanService(db_session)
    with pytest.raises(ValueError):
        plan_svc.crear_plan({"vendedor_id": 1, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": []})


def test_crear_plan_duplicate_raises(db_session):
    vend_svc = VendedorService(db_session)
    v = vend_svc.crear_vendedor({"nombre": "VDup", "email": "vdup@x.com", "pais": 1, "estado": "ACTIVO"})
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "Pdup", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod = ProductService(db_session).crear_producto({"sku": "SDUP", "nombre_producto": "PD", "proveedor_id": prov.id, "valor_unitario_usd": 2.0, "certificaciones": [1]}, usuario_id=1)
    plan_svc = PlanService(db_session)
    plan_svc.crear_plan({"vendedor_id": v.id, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=3)
    # duplicate same vendedor/periodo/anio/pais should raise
    with pytest.raises(ValueError):
        plan_svc.crear_plan({"vendedor_id": v.id, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=4)

def test_eliminar_plan_blocked_when_en_ejecucion(db_session):
    vend_svc = VendedorService(db_session)
    v = vend_svc.crear_vendedor({"nombre": "VExec", "email": "vexec@x.com", "pais": 1, "estado": "ACTIVO"})
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "Pexec", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod = ProductService(db_session).crear_producto({"sku": "SEJ", "nombre_producto": "PEJ", "proveedor_id": prov.id, "valor_unitario_usd": 2.0, "certificaciones": [1]}, usuario_id=1)
    plan_svc = PlanService(db_session)
    plan = plan_svc.crear_plan({"vendedor_id": v.id, "periodo": "Q2", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=3)
    # set estado to EN_EJECUCION and expect deletion blocked
    plan.estado = 'EN_EJECUCION'
    db_session.commit()
    with pytest.raises(ValueError):
        plan_svc.eliminar_plan(plan)
