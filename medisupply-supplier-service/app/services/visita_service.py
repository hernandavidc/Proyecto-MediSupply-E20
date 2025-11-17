from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.visita import Visita


def get_visitas_for_vendedor(db: Session, vendedor_id: int, fecha: Optional[date] = None) -> List[Visita]:
    """Devuelve las visitas de un vendedor. Si fecha es None devuelve todas."""
    if fecha is None:
        visitas = db.query(Visita).filter(Visita.vendedor_id == vendedor_id).order_by(Visita.scheduled_at).all()
    else:
        visitas = db.query(Visita).filter(
            Visita.vendedor_id == vendedor_id,
            func.date(Visita.scheduled_at) == fecha,
        ).all()
    return visitas


def create_visita(db: Session, vendedor_id: int, visita_payload: dict) -> Visita:
    """Crea y persiste una visita en la base de datos.

    Lanza HTTPException en caso de errores de datos o integridad.
    """
    # Validación mínima de coordenadas
    try:
        lat_val = float(visita_payload.get('lat'))
        lon_val = float(visita_payload.get('lon'))
    except Exception:
        raise HTTPException(status_code=400, detail='Coordenadas inválidas')

    if not (-90 <= lat_val <= 90 and -180 <= lon_val <= 180):
        raise HTTPException(status_code=400, detail='Coordenadas fuera de rango')

    visita = Visita(vendedor_id=vendedor_id, **visita_payload)
    db.add(visita)
    try:
        db.commit()
        db.refresh(visita)
    except IntegrityError as e:
        db.rollback()
        err_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'foreign key' in err_msg.lower() or 'foreignkey' in err_msg.lower():
            raise HTTPException(status_code=400, detail='Error de integridad: vendedor o cliente no existe')
        raise HTTPException(status_code=400, detail=f'Error al registrar la visita: {err_msg}')

    return visita
