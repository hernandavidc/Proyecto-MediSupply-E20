from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.bodega_producto import BodegaProducto
from app.models.bodega import Bodega
from app.schemas.bodega_producto_schema import BodegaProductoCreate, BodegaProductoUpdate
from datetime import datetime, timedelta
import math


class BodegaProductoService:
    def __init__(self, db: Session):
        self.db = db

    def _calcular_distancia_haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
        Retorna la distancia en kilómetros.
        """
        # Radio de la Tierra en kilómetros
        R = 6371.0
        
        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distancia = R * c
        return distancia

    def _calcular_pronostico_entrega(
        self, 
        lat_origen: float, 
        lon_origen: float, 
        lat_bodega: float, 
        lon_bodega: float,
        dias_alistamiento: int
    ) -> datetime:
        """
        Calcula el pronóstico de entrega considerando:
        - Distancia desde origen hasta bodega
        - Velocidad de transporte: 20 km/h
        - Días de alistamiento
        """
        # Calcular distancia en km
        distancia_km = self._calcular_distancia_haversine(lat_origen, lon_origen, lat_bodega, lon_bodega)
        
        # Calcular tiempo de viaje en horas (velocidad = 20 km/h)
        tiempo_viaje_horas = distancia_km / 20.0
        
        # Convertir días de alistamiento a horas
        tiempo_alistamiento_horas = dias_alistamiento * 24
        
        # Tiempo total en horas
        tiempo_total_horas = tiempo_viaje_horas + tiempo_alistamiento_horas
        
        # Calcular fecha de entrega desde ahora
        fecha_entrega = datetime.now() + timedelta(hours=tiempo_total_horas)
        
        return fecha_entrega

    def crear_bodega_producto(self, data: BodegaProductoCreate) -> BodegaProducto:
        bodega_producto = BodegaProducto(**data.model_dump())
        self.db.add(bodega_producto)
        self.db.commit()
        self.db.refresh(bodega_producto)
        return bodega_producto

    def listar_bodega_productos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        id_bodega: Optional[int] = None,
        id_producto: Optional[int] = None,
        lote: Optional[str] = None,
        latitud: Optional[float] = None,
        longitud: Optional[float] = None
    ) -> List[dict]:
        query = self.db.query(BodegaProducto).join(Bodega)
        
        # Apply filters if provided
        if id_bodega:
            query = query.filter(BodegaProducto.id_bodega == id_bodega)
        if id_producto:
            query = query.filter(BodegaProducto.id_producto == id_producto)
        if lote:
            query = query.filter(BodegaProducto.lote == lote)
        
        bodega_productos = query.offset(skip).limit(limit).all()
        
        # Convertir a diccionarios con pronostico_entrega calculado
        resultados = []
        for bp in bodega_productos:
            bodega = self.db.query(Bodega).filter(Bodega.id == bp.id_bodega).first()
            resultado = {
                "id_bodega": bp.id_bodega,
                "id_producto": bp.id_producto,
                "lote": bp.lote,
                "cantidad": bp.cantidad,
                "dias_alistamiento": bp.dias_alistamiento,
                "pronostico_entrega": None
            }
            
            # Calcular pronostico_entrega si se proporcionaron coordenadas y la bodega tiene ubicación
            if latitud is not None and longitud is not None and bodega and bodega.latitud and bodega.longitud:
                resultado["pronostico_entrega"] = self._calcular_pronostico_entrega(
                    latitud, longitud,
                    float(bodega.latitud), float(bodega.longitud),
                    bp.dias_alistamiento
                )
            
            resultados.append(resultado)
        
        return resultados

    def listar_por_bodega(self, bodega_id: int) -> List[BodegaProducto]:
        return self.db.query(BodegaProducto).filter(BodegaProducto.id_bodega == bodega_id).all()

    def obtener_bodega_producto(self, bodega_id: int, producto_id: int, lote: str) -> Optional[BodegaProducto]:
        return self.db.query(BodegaProducto).filter(
            BodegaProducto.id_bodega == bodega_id,
            BodegaProducto.id_producto == producto_id,
            BodegaProducto.lote == lote
        ).first()

    def actualizar_bodega_producto(self, bodega_id: int, producto_id: int, lote: str, data: BodegaProductoUpdate) -> Optional[BodegaProducto]:
        bodega_producto = self.obtener_bodega_producto(bodega_id, producto_id, lote)
        if not bodega_producto:
            return None
        
        # Update only provided fields
        if data.cantidad is not None:
            bodega_producto.cantidad = data.cantidad
        if data.dias_alistamiento is not None:
            bodega_producto.dias_alistamiento = data.dias_alistamiento
        
        self.db.commit()
        self.db.refresh(bodega_producto)
        return bodega_producto

    def eliminar_bodega_producto(self, bodega_id: int, producto_id: int, lote: str) -> bool:
        bodega_producto = self.obtener_bodega_producto(bodega_id, producto_id, lote)
        if not bodega_producto:
            return False
        
        self.db.delete(bodega_producto)
        self.db.commit()
        return True
