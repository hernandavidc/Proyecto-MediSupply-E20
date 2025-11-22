from pydantic import BaseModel


class OrdenProductoBase(BaseModel):
    id_orden: int
    id_producto: int
    cantidad: int


class OrdenProductoCreate(OrdenProductoBase):
    pass


class OrdenProductoUpdate(BaseModel):
    cantidad: int


class OrdenProductoResponse(OrdenProductoBase):
    class Config:
        from_attributes = True
