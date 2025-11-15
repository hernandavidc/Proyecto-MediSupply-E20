from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.visita_schema import RutaResponse, RutaItem, VisitaResponse, VisitaBase
from app.services.route_service import compute_route
from app.models.visita import Visita
from app.models.vendedor import Vendedor
from sqlalchemy.exc import IntegrityError
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/rutas-visitas", tags=["Visitas"])


@router.get("/{vendedor_id}", response_model=RutaResponse)
def get_ruta_visitas(
    vendedor_id: int,
    fecha: date | None = Query(default=None, description="Fecha a consultar (YYYY-MM-DD). Si se omite, devuelve todas las visitas del vendedor."),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Devuelve la ruta optimizada de visitas para el vendedor indicado en la fecha seleccionada.

    Respuesta incluye orden sugerido, distancia entre puntos y tiempos estimados.
    """
    # Requerir autenticación
    if not current_user:
        raise HTTPException(status_code=401, detail='Autenticación requerida')

    # Validar existencia del vendedor solicitado (se obtiene por path param)
    vendedor_obj = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not vendedor_obj:
        raise HTTPException(status_code=400, detail='El vendedor especificado no existe')

    from sqlalchemy import func

    # Si no se especifica fecha, devolvemos todas las visitas para el vendedor
    if fecha is None:
        visitas = db.query(Visita).filter(Visita.vendedor_id == vendedor_id).order_by(Visita.scheduled_at).all()
        date_str = "all"
    else:
        # Buscar visitas programadas para la fecha solicitada usando DATE() en BD
        visitas = db.query(Visita).filter(
            Visita.vendedor_id == vendedor_id,
            func.date(Visita.scheduled_at) == fecha,
        ).all()
        date_str = str(fecha)

    if not visitas:
        # Responder explícitamente que no hay visitas para la fecha pedida (solo para este vendedor)
        return RutaResponse(date=date_str, total_distance_km=0.0, total_travel_time_minutes=0, items=[], message="No hay visitas programadas para esta fecha")

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

    return RutaResponse(date=date_str, total_distance_km=route['total_distance_km'], total_travel_time_minutes=route['total_travel_time_minutes'], items=items)


# Endpoint para registrar una visita (HU: Registrar visita)
# Ahora la ruta exige el id del vendedor en la URL: /registro/{vendedor_id}
@router.post('/registro/{vendedor_id}', status_code=status.HTTP_201_CREATED)
def registrar_visita(
    vendedor_id: int,
    payload: VisitaBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Registrar una visita para el vendedor autenticado.

    El cuerpo debe ser JSON con campos: cliente_id, direccion, lat, lon, scheduled_at (ISO datetime),
    duration_minutes, notas, evidencias (lista de URLs o paths a evidencias ya almacenadas).
    """
    # Verificar autenticación
    if not current_user:
        raise HTTPException(status_code=401, detail='Autenticación requerida')

    # Extraer email/is_admin
    def _user_email_and_admin(user):
        is_admin = False
        email = None
        if isinstance(user, dict):
            email = user.get('email')
            is_admin = bool(user.get('is_admin') or user.get('is_staff') or (user.get('role') == 'admin'))
        else:
            email = getattr(user, 'email', None)
            is_admin = bool(getattr(user, 'is_admin', False) or getattr(user, 'role', None) == 'admin')
        return email, is_admin

    user_email, user_is_admin = _user_email_and_admin(current_user)

    # Validar existencia del vendedor
    vendedor_obj = db.query(Vendedor).filter(Vendedor.id == vendedor_id).first()
    if not vendedor_obj:
        raise HTTPException(status_code=400, detail='El vendedor especificado no existe')

    # No se impone verificación de ownership: cualquier usuario autenticado
    # puede registrar visitas para un vendedor existente.

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
    try:
        db.commit()
        db.refresh(visita)
    except IntegrityError as e:
        db.rollback()
        # Detectar violación de FK y responder con mensaje amigable
        err_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'ForeignKeyViolation' in err_msg or 'foreign key' in err_msg.lower():
            raise HTTPException(status_code=400, detail='Error de integridad: vendedor o cliente no existe')
        raise HTTPException(status_code=400, detail='Error al registrar la visita: {}'.format(err_msg))

    return {"id": visita.id, "message": "Visita registrada"}
