from pydantic import BaseModel

class PedidoCreate(BaseModel):
    cliente: str
    producto: str
    cantidad: int
