import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.services.proveedor_service import ProveedorService
from app.models.proveedor import ProveedorAuditoria

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

def test_create_proveedor_and_audit(db_session):
    service = ProveedorService(db_session)
    data = {"razon_social": "Proveedor X", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]}
    proveedor = service.crear_proveedor(data, usuario_id=42)
    assert proveedor.id is not None
    audits = db_session.query(ProveedorAuditoria).filter(ProveedorAuditoria.proveedor_id == proveedor.id).all()
    assert len(audits) >= 1
    assert audits[0].operacion == 'CREATE'

def test_delete_blocked_when_product_exists(db_session):
    service = ProveedorService(db_session)
    data = {"razon_social": "Proveedor Y", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]}
    proveedor = service.crear_proveedor(data)
    # crear un producto real que referencie al proveedor para simular productos activos
    from app.services.product_service import ProductService
    prod_service = ProductService(db_session)
    prod_service.crear_producto({"sku": "PX1", "nombre_producto": "Producto X", "proveedor_id": proveedor.id, "valor_unitario_usd": 1.0, "certificaciones": []})
    with pytest.raises(ValueError):
        service.eliminar_proveedor(proveedor)

def test_update_proveedor(db_session):
    service = ProveedorService(db_session)
    data = {"razon_social": "Proveedor Z", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]}
    proveedor = service.crear_proveedor(data)
    updated = service.actualizar_proveedor(proveedor, {"razon_social": "Proveedor Z Updated", "paises_operacion": [1, 2]}, usuario_id=7)
    assert updated.razon_social == "Proveedor Z Updated"
    audits = db_session.query(ProveedorAuditoria).filter(ProveedorAuditoria.proveedor_id == proveedor.id, ProveedorAuditoria.operacion == 'UPDATE').all()
    assert len(audits) >= 1
