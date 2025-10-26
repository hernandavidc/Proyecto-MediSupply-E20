import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.product_service import ProductService
from app.services.proveedor_service import ProveedorService

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

def test_create_producto_success(db_session):
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "Prov1", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    data = {"sku": "ABC123", "nombre_producto": "Producto 1", "proveedor_id": prov.id, "valor_unitario_usd": 10.50, "certificaciones": [1]}
    prod = prod_service.crear_producto(data, usuario_id=5)
    assert prod.id is not None

def test_create_producto_block_cert_mismatch(db_session):
    # proveedor sin certificaciones
    prov_service = ProveedorService(db_session)
    prov = prov_service.crear_proveedor({"razon_social": "Prov2", "paises_operacion": [1], "certificaciones_sanitarias": [], "categorias_suministradas": [1]})
    prod_service = ProductService(db_session)
    data = {"sku": "DEF456", "nombre_producto": "Producto 2", "proveedor_id": prov.id, "valor_unitario_usd": 5.00, "certificaciones": [1]}
    with pytest.raises(ValueError):
        prod_service.crear_producto(data)
