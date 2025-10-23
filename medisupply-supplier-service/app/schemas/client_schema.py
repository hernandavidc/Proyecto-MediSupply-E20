from pydantic import BaseModel
from typing import Optional


class ClienteResponse(BaseModel):
    id: int
    vendedor_id: int
    institucion_nombre: str
    direccion: Optional[str] = None
    contacto_principal: Optional[str] = None

    model_config = {
        "orm_mode": True
    }
