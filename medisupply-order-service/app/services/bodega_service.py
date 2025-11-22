from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.bodega import Bodega
from app.models.bodega_producto import BodegaProducto
from app.schemas.bodega_schema import BodegaCreate, BodegaUpdate


class BodegaService:
    def __init__(self, db: Session):
        self.db = db

    def crear_bodega(self, data: BodegaCreate) -> Bodega:
        bodega = Bodega(**data.model_dump())
        self.db.add(bodega)
        self.db.commit()
        self.db.refresh(bodega)
        return bodega

    def listar_bodegas(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        id_pais: Optional[int] = None,
        id_producto: Optional[int] = None
    ) -> List[Bodega]:
        query = self.db.query(Bodega)
        
        # Apply filter by id_pais
        if id_pais:
            query = query.filter(Bodega.id_pais == id_pais)
        
        # Apply filter by id_producto using relationship with bodega_producto
        if id_producto:
            query = query.join(BodegaProducto).filter(BodegaProducto.id_producto == id_producto).distinct()
        
        return query.offset(skip).limit(limit).all()

    def obtener_bodega(self, bodega_id: int) -> Optional[Bodega]:
        return self.db.query(Bodega).filter(Bodega.id == bodega_id).first()

    def actualizar_bodega(self, bodega_id: int, data: BodegaUpdate) -> Optional[Bodega]:
        bodega = self.obtener_bodega(bodega_id)
        if not bodega:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(bodega, key, value)
        
        self.db.commit()
        self.db.refresh(bodega)
        return bodega

    def eliminar_bodega(self, bodega_id: int) -> bool:
        bodega = self.obtener_bodega(bodega_id)
        if not bodega:
            return False
        
        self.db.delete(bodega)
        self.db.commit()
        return True
