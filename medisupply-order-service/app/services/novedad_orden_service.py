from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.novedad_orden import NovedadOrden
from app.schemas.novedad_orden_schema import NovedadOrdenCreate, NovedadOrdenUpdate


class NovedadOrdenService:
    def __init__(self, db: Session):
        self.db = db

    def crear_novedad(self, data: NovedadOrdenCreate) -> NovedadOrden:
        novedad = NovedadOrden(**data.model_dump())
        self.db.add(novedad)
        self.db.commit()
        self.db.refresh(novedad)
        return novedad

    def listar_novedades(self, skip: int = 0, limit: int = 100) -> List[NovedadOrden]:
        return self.db.query(NovedadOrden).offset(skip).limit(limit).all()

    def listar_por_orden(self, orden_id: int) -> List[NovedadOrden]:
        return self.db.query(NovedadOrden).filter(NovedadOrden.id_pedido == orden_id).all()

    def obtener_novedad(self, novedad_id: int) -> Optional[NovedadOrden]:
        return self.db.query(NovedadOrden).filter(NovedadOrden.id == novedad_id).first()

    def actualizar_novedad(self, novedad_id: int, data: NovedadOrdenUpdate) -> Optional[NovedadOrden]:
        novedad = self.obtener_novedad(novedad_id)
        if not novedad:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(novedad, key, value)
        
        self.db.commit()
        self.db.refresh(novedad)
        return novedad

    def eliminar_novedad(self, novedad_id: int) -> bool:
        novedad = self.obtener_novedad(novedad_id)
        if not novedad:
            return False
        
        self.db.delete(novedad)
        self.db.commit()
        return True
