import pytest
from app.api.v1 import producto_routes
from app.schemas.product_schema import ProductoCreate


@pytest.mark.asyncio
async def test_create_producto_route_success(db_session):
    # prepare provider
    from app.services.proveedor_service import ProveedorService
    prov = ProveedorService(db_session).crear_proveedor({"razon_social": "PRoute", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    payload = ProductoCreate(sku='SRT', nombre_producto='PR', proveedor_id=prov.id, valor_unitario_usd=3.5)
    prod = await producto_routes.create_producto(payload, db=db_session)
    assert prod.id is not None
