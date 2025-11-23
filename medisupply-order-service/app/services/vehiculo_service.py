from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo_schema import VehiculoCreate, VehiculoUpdate
from app.core.redis import get_redis, cache_key, serialize_for_cache, deserialize_from_cache
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()

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
        # Intentar obtener del caché
        if self.redis:
            try:
                key = cache_key("vehiculo", id=vehiculo_id)
                cached = self.redis.get(key)
                if cached:
                    data = deserialize_from_cache(cached)
                    # Reconstruir objeto Vehiculo desde cache
                    vehiculo = Vehiculo(**data)
                    vehiculo.id = data['id']
                    return vehiculo
            except Exception as e:
                logger.warning(f"Error leyendo caché: {e}")
        
        # Obtener de base de datos
        vehiculo = self.db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        
        # Guardar en caché si existe
        if vehiculo and self.redis:
            try:
                key = cache_key("vehiculo", id=vehiculo_id)
                self.redis.setex(
                    key,
                    settings.CACHE_TTL,
                    serialize_for_cache(vehiculo)
                )
            except Exception as e:
                logger.warning(f"Error guardando en caché: {e}")
        
        return vehiculo

    def actualizar_vehiculo(self, vehiculo_id: int, data: VehiculoUpdate) -> Optional[Vehiculo]:
        vehiculo = self.db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        if not vehiculo:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(vehiculo, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(vehiculo)
            
            # Invalidar caché después de actualizar
            if self.redis:
                try:
                    key = cache_key("vehiculo", id=vehiculo_id)
                    self.redis.delete(key)
                except Exception as e:
                    logger.warning(f"Error invalidando caché: {e}")
            
            return vehiculo
        except IntegrityError:
            self.db.rollback()
            raise ValueError("La placa ya existe")

    def eliminar_vehiculo(self, vehiculo_id: int) -> bool:
        vehiculo = self.db.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        if not vehiculo:
            return False
        
        self.db.delete(vehiculo)
        self.db.commit()
        
        # Invalidar caché después de eliminar
        if self.redis:
            try:
                key = cache_key("vehiculo", id=vehiculo_id)
                self.redis.delete(key)
            except Exception as e:
                logger.warning(f"Error invalidando caché: {e}")
        
        return True
