from pydantic import BaseModel
from typing import Optional


class ClienteResponse(BaseModel):
    id: int
    vendedor_id: int
    institucion_nombre: str
    direccion: Optional[str] = None
    contacto_principal: Optional[str] = None

    # Pydantic v2: use 'from_attributes' to allow creating model from ORM objects
    model_config = {
        "from_attributes": True
    }
