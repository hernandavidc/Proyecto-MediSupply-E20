import pytest
from app.services.vendedor_service import VendedorService
from app.services.plan_service import PlanService


def test_eliminar_vendedor_success(db_session):
    vend_svc = VendedorService(db_session)
    v = vend_svc.crear_vendedor({"nombre": "VDel", "email": "vdel@x.com", "pais": 1, "estado": "ACTIVO"})
    # no plans: deletion allowed
    vend_svc.eliminar_vendedor(v)
    assert vend_svc.obtener_vendedor(v.id) is None


def test_eliminar_vendedor_blocked_when_has_plan(db_session):
    vend_svc = VendedorService(db_session)
    plan_svc = PlanService(db_session)
    v = vend_svc.crear_vendedor({"nombre": "VPlan", "email": "vplan@x.com", "pais": 1, "estado": "ACTIVO"})
    # create minimal product and plan to block deletion
    from app.services.proveedor_service import ProveedorService
    from app.services.product_service import ProductService
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "P1", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod = ProductService(db_session).crear_producto({"sku": "SPB", "nombre_producto": "PB", "proveedor_id": prov.id, "valor_unitario_usd": 1.0, "certificaciones": [1]}, usuario_id=1)
    plan = plan_svc.crear_plan({"vendedor_id": v.id, "periodo": "Q1", "anio": 2025, "pais": 1, "productos_objetivo": [prod.id]}, usuario_id=1)
    with pytest.raises(ValueError):
        vend_svc.eliminar_vendedor(v)
