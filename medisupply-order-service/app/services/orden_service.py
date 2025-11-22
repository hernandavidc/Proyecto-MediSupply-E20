from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.orden import Orden, EstadoOrden
from app.models.orden_producto import OrdenProducto
from app.schemas.orden_schema import OrdenCreate, OrdenUpdate


class OrdenService:
    def __init__(self, db: Session):
        self.db = db

    def crear_orden(self, data: OrdenCreate) -> Orden:
        # Extract productos from data
        productos_data = data.productos
        orden_data = data.model_dump(exclude={'productos'})
        
        # Create orden
        orden = Orden(**orden_data)
        self.db.add(orden)
        self.db.flush()  # Get the orden ID without committing
        
        # Create orden_productos
        for producto_data in productos_data:
            orden_producto = OrdenProducto(
                id_orden=orden.id,
                id_producto=producto_data.id_producto,
                cantidad=producto_data.cantidad
            )
            self.db.add(orden_producto)
        
        self.db.commit()
        self.db.refresh(orden)
        return orden

    def listar_ordenes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        estado: Optional[str] = None,
        id_cliente: Optional[int] = None
    ) -> List[Orden]:
        query = self.db.query(Orden)
        
        # Apply filters if provided
        if estado:
            query = query.filter(Orden.estado == estado)
        if id_cliente:
            query = query.filter(Orden.id_cliente == id_cliente)
        
        return query.offset(skip).limit(limit).all()

    def obtener_orden(self, orden_id: int) -> Optional[Orden]:
        return self.db.query(Orden).filter(Orden.id == orden_id).first()

    def actualizar_orden(self, orden_id: int, data: OrdenUpdate) -> Optional[Orden]:
        orden = self.obtener_orden(orden_id)
        if not orden:
            return None
        
        # Validar que el estado de la orden sea ABIERTO
        if orden.estado != EstadoOrden.ABIERTO:
            raise ValueError("El estado de la orden no permite modificaciones")
        
        update_data = data.model_dump(exclude_unset=True, exclude={'productos'})
        
        # Update orden fields
        for key, value in update_data.items():
            setattr(orden, key, value)
        
        # Update productos if provided
        if data.productos is not None:
            # Delete existing productos
            self.db.query(OrdenProducto).filter(OrdenProducto.id_orden == orden_id).delete()
            
            # Add new productos
            for producto_data in data.productos:
                orden_producto = OrdenProducto(
                    id_orden=orden_id,
                    id_producto=producto_data.id_producto,
                    cantidad=producto_data.cantidad
                )
                self.db.add(orden_producto)
        
        self.db.commit()
        self.db.refresh(orden)
        return orden

    def eliminar_orden(self, orden_id: int) -> bool:
        orden = self.obtener_orden(orden_id)
        if not orden:
            return False
        
        # Delete orden_productos first (cascade should handle this, but being explicit)
        self.db.query(OrdenProducto).filter(OrdenProducto.id_orden == orden_id).delete()
        
        # Delete orden
        self.db.delete(orden)
        self.db.commit()
        return True

    def _orden_to_response(self, orden: Orden) -> dict:
        """Convert Orden model to response format including productos"""
        productos = self.db.query(OrdenProducto).filter(OrdenProducto.id_orden == orden.id).all()
        
        return {
            "id": orden.id,
            "fecha_entrega_estimada": orden.fecha_entrega_estimada,
            "id_vehiculo": orden.id_vehiculo,
            "id_cliente": orden.id_cliente,
            "id_vendedor": orden.id_vendedor,
            "estado": orden.estado,
            "fecha_creacion": orden.fecha_creacion,
            "productos": [
                {
                    "id_producto": p.id_producto,
                    "cantidad": p.cantidad
                }
                for p in productos
            ]
        }
