from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.visita_schema import RutaResponse, RutaItem, VisitaResponse, VisitaBase
from app.services.route_service import compute_route
from app.models.visita import Visita
from app.models.vendedor import Vendedor
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/rutas-visitas", tags=["Visitas"])


@router.get("/", response_model=RutaResponse)
def get_ruta_visitas(
    fecha: date = Query(default=date.today(), description="Fecha a consultar (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Devuelve la ruta optimizada de visitas para el vendedor autenticado en la fecha seleccionada.

    Respuesta incluye orden sugerido, distancia entre puntos y tiempos estimados.
    """
    vendedor_id = None
    # current_user puede ser dict o ORM; normalmente la verificación remota devuelve dict
    if isinstance(current_user, dict):
        vendedor_id = current_user.get('id')
    else:
        # si viene un objeto con id
        vendedor_id = getattr(current_user, 'id', None)

    if vendedor_id is None:
        # intentar mapear el usuario autenticado a un vendedor por email si viene en el token
        user_email = None
        if isinstance(current_user, dict):
            user_email = current_user.get('email')
        else:
            user_email = getattr(current_user, 'email', None)
        if user_email:
            vendedor_obj = db.query(Vendedor).filter(Vendedor.email == user_email).first()
            if vendedor_obj:
                vendedor_id = vendedor_obj.id

    if vendedor_id is None:
        raise HTTPException(status_code=400, detail='No se pudo identificar al vendedor autenticado')

    # Buscar visitas programadas para el día
    start_dt = datetime.combine(fecha, datetime.min.time())
    end_dt = datetime.combine(fecha, datetime.max.time())

    visitas = db.query(Visita).filter(Visita.vendedor_id == vendedor_id, Visita.scheduled_at >= start_dt, Visita.scheduled_at <= end_dt).all()

    if not visitas:
        # Responder explícitamente que no hay visitas para la fecha pedida (solo para este vendedor)
        return RutaResponse(date=str(fecha), total_distance_km=0.0, total_travel_time_minutes=0, items=[], message="No hay visitas programadas para esta fecha")

    # Transformar visitas a dicts para el servicio
    points = []
    for v in visitas:
        points.append({
            'id': v.id,
            'cliente_id': v.cliente_id,
            'lat': v.lat,
            'lon': v.lon,
            'scheduled_at': v.scheduled_at,
            'duration_minutes': v.duration_minutes,
            'direccion': v.direccion,
            'notas': v.notas,
            'evidencias': v.evidencias,
        })

    route = compute_route(points)

    # Mapear items para la respuesta usando VisitaResponse
    items = []
    for it in route['items']:
        visita_dict = it['visita']
        visita_resp = VisitaResponse(
            id=visita_dict['id'],
            cliente_id=visita_dict.get('cliente_id'),
            direccion=visita_dict.get('direccion'),
            lat=visita_dict['lat'],
            lon=visita_dict['lon'],
            scheduled_at=visita_dict.get('scheduled_at'),
            duration_minutes=visita_dict.get('duration_minutes'),
            notas=visita_dict.get('notas'),
            evidencias=visita_dict.get('evidencias'),
        )
        item = RutaItem(
            visita=visita_resp,
            sequence=it['sequence'],
            distance_from_prev_km=it['distance_from_prev_km'],
            travel_time_minutes=it['travel_time_minutes'],
            estimated_arrival=it['estimated_arrival'],
        )
        items.append(item)

    return RutaResponse(date=str(fecha), total_distance_km=route['total_distance_km'], total_travel_time_minutes=route['total_travel_time_minutes'], items=items)


# Endpoint para registrar una visita (HU: Registrar visita)
@router.post('/registro', status_code=status.HTTP_201_CREATED)
def registrar_visita(
    payload: VisitaBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registrar una visita para el vendedor autenticado.

    El cuerpo debe ser JSON con campos: cliente_id, direccion, lat, lon, scheduled_at (ISO datetime),
    duration_minutes, notas, evidencias (lista de URLs o paths a evidencias ya almacenadas).
    """
    vendedor_id = None
    if isinstance(current_user, dict):
        vendedor_id = current_user.get('id')
    else:
        vendedor_id = getattr(current_user, 'id', None)

    if vendedor_id is None:
        raise HTTPException(status_code=400, detail='No se pudo identificar al vendedor autenticado')

    # Validación sencilla de coordenadas
    try:
        lat_val = float(payload.lat)
        lon_val = float(payload.lon)
    except Exception:
        raise HTTPException(status_code=400, detail='Coordenadas inválidas')

    # Rango básico de coordenadas
    if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
        raise HTTPException(status_code=400, detail='Coordenadas fuera de rango')

    visita_data = payload.model_dump() if hasattr(payload, 'model_dump') else payload.dict()
    visita = Visita(vendedor_id=vendedor_id, **visita_data)
    db.add(visita)
    db.commit()
    db.refresh(visita)

    return {"id": visita.id, "message": "Visita registrada"}
