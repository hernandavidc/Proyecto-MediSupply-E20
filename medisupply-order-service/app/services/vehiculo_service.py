from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo_schema import VehiculoCreate, VehiculoUpdate


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db

    def crear_vehiculo(self, data: VehiculoCreate) -> Vehiculo:
        vehiculo = Vehiculo(**data.model_dump())
        try:
            self.db.add(vehiculo)
            self.db.commit()
            self.db.refresh(vehiculo)
            return vehiculo
        except IntegrityError:
            self.db.rollback()
            raise ValueError("La placa ya existe")

    def listar_vehiculos(self, skip: int = 0, limit: int = 100) -> List[Vehiculo]:
        return self.db.query(Vehiculo).offset(skip).limit(limit).all()

    def obtener_vehiculo(self, vehiculo_id: int) -> Optional[Vehiculo]:
        return self.db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()

    def actualizar_vehiculo(self, vehiculo_id: int, data: VehiculoUpdate) -> Optional[Vehiculo]:
        vehiculo = self.obtener_vehiculo(vehiculo_id)
        if not vehiculo:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehiculo, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(vehiculo)
            return vehiculo
        except IntegrityError:
            self.db.rollback()
            raise ValueError("La placa ya existe")

    def eliminar_vehiculo(self, vehiculo_id: int) -> bool:
        vehiculo = self.obtener_vehiculo(vehiculo_id)
        if not vehiculo:
            return False
        
        self.db.delete(vehiculo)
        self.db.commit()
        return True
