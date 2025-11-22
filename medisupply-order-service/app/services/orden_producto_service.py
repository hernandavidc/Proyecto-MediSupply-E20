from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.orden_producto import OrdenProducto
from app.schemas.orden_producto_schema import OrdenProductoCreate, OrdenProductoUpdate


class OrdenProductoService:
    def __init__(self, db: Session):
        self.db = db

    def crear_orden_producto(self, data: OrdenProductoCreate) -> OrdenProducto:
        orden_producto = OrdenProducto(**data.model_dump())
        self.db.add(orden_producto)
        self.db.commit()
        self.db.refresh(orden_producto)
        return orden_producto

    def listar_orden_productos(self, skip: int = 0, limit: int = 100) -> List[OrdenProducto]:
        return self.db.query(OrdenProducto).offset(skip).limit(limit).all()

    def listar_por_orden(self, orden_id: int) -> List[OrdenProducto]:
        return self.db.query(OrdenProducto).filter(OrdenProducto.id_orden == orden_id).all()

    def obtener_orden_producto(self, orden_id: int, producto_id: int) -> Optional[OrdenProducto]:
        return self.db.query(OrdenProducto).filter(
            OrdenProducto.id_orden == orden_id,
            OrdenProducto.id_producto == producto_id
        ).first()

    def actualizar_orden_producto(self, orden_id: int, producto_id: int, data: OrdenProductoUpdate) -> Optional[OrdenProducto]:
        orden_producto = self.obtener_orden_producto(orden_id, producto_id)
        if not orden_producto:
            return None
        
        orden_producto.cantidad = data.cantidad
        self.db.commit()
        self.db.refresh(orden_producto)
        return orden_producto

    def eliminar_orden_producto(self, orden_id: int, producto_id: int) -> bool:
        orden_producto = self.obtener_orden_producto(orden_id, producto_id)
        if not orden_producto:
            return False
        
        self.db.delete(orden_producto)
        self.db.commit()
        return True
