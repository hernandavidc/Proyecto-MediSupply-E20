from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.product import Producto, ProductoAuditoria
from app.models.proveedor import Proveedor
from datetime import date, datetime


def _serialize_dates(obj: Any):
    """Recursively convert date/datetime objects to ISO strings for JSON storage."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_dates(v) for v in obj]
    return obj

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def crear_producto(self, data: Dict[str, Any], usuario_id: Optional[int] = None, origen: str='MANUAL') -> Producto:
        # verificaciones de negocio: proveedor existe
        proveedor = self.db.query(Proveedor).filter(Proveedor.id == data.get('proveedor_id')).first()
        if not proveedor:
            raise ValueError('Proveedor no encontrado')
        # verificar certificaciones compatibles: si producto tiene certificaciones, proveedor debe tener al menos una coincidente
        prod_certs = set(data.get('certificaciones') or [])
        prov_certs = set(proveedor.certificaciones_sanitarias or [])
        if prod_certs and not (prod_certs & prov_certs):
            raise ValueError('Proveedor no tiene certificaciones compatibles')
        try:
            # Serialize any date/datetime inside JSON fields to avoid JSON encoding errors
            condiciones = data.get('condiciones')
            organizacion = data.get('organizacion')
            if condiciones is not None:
                condiciones = _serialize_dates(condiciones)
            if organizacion is not None:
                organizacion = _serialize_dates(organizacion)

            producto = Producto(
                sku=data.get('sku'),
                nombre_producto=data.get('nombre_producto'),
                proveedor_id=data.get('proveedor_id'),
                ficha_tecnica_url=data.get('ficha_tecnica_url'),
                condiciones=condiciones,
                organizacion=organizacion,
                tipo_medicamento=data.get('tipo_medicamento'),
                fecha_vencimiento=data.get('fecha_vencimiento'),
                valor_unitario_usd=data.get('valor_unitario_usd'),
                certificaciones=data.get('certificaciones'),
                tiempo_entrega_dias=data.get('tiempo_entrega_dias'),
                origen=origen,
            )
            self.db.add(producto)
            self.db.flush()
            audit = ProductoAuditoria(
                producto_id=producto.id,
                operacion='CREATE',
                usuario_id=usuario_id,
                datos_nuevos={'sku': producto.sku, 'nombre_producto': producto.nombre_producto},
                origen=origen
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(producto)
            return producto
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise

    def listar_productos(self, skip: int=0, limit: int=100):
        return self.db.query(Producto).offset(skip).limit(limit).all()

    def obtener_producto(self, producto_id: int):
        return self.db.query(Producto).filter(Producto.id == producto_id).first()
