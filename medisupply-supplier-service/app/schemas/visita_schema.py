from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class VisitaBase(BaseModel):
    cliente_id: Optional[int]
    direccion: Optional[str]
    lat: float
    lon: float
    scheduled_at: Optional[datetime]
    duration_minutes: Optional[int]
    notas: Optional[str] = None
    evidencias: Optional[List[str]] = None

    @validator('lat')
    def lat_must_be_valid(cls, v):
        try:
            fv = float(v)
        except Exception:
            raise ValueError('lat must be a number')
        if not (-90.0 <= fv <= 90.0):
            raise ValueError('lat out of range (-90..90)')
        if fv == 0.0:
            raise ValueError('lat cannot be 0.0')
        return fv

    @validator('lon')
    def lon_must_be_valid(cls, v):
        try:
            fv = float(v)
        except Exception:
            raise ValueError('lon must be a number')
        if not (-180.0 <= fv <= 180.0):
            raise ValueError('lon out of range (-180..180)')
        if fv == 0.0:
            raise ValueError('lon cannot be 0.0')
        return fv


class VisitaResponse(VisitaBase):
    id: int

    class Config:
        orm_mode = True


class RutaItem(BaseModel):
    visita: VisitaResponse
    sequence: int
    distance_from_prev_km: float
    travel_time_minutes: int
    estimated_arrival: Optional[datetime]


class RutaResponse(BaseModel):
    date: str
    total_distance_km: float
    total_travel_time_minutes: int
    items: List[RutaItem]
    message: Optional[str] = None
