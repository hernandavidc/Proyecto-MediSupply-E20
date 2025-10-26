import pytest
from pydantic import ValidationError
from app.schemas.proveedor_schema import ProveedorCreate

def test_valid_proveedor():
    data = {
        "razon_social": "ACME",
        "paises_operacion": [1, 2, 2],
        "certificaciones_sanitarias": [1, 1],
        "categorias_suministradas": [3],
        "capacidad_cadena_frio": ["-20C"]
    }
    p = ProveedorCreate(**data)
    assert p.razon_social == "ACME"
    assert p.paises_operacion == [1, 2]
    assert p.certificaciones_sanitarias == [1]
    assert p.categorias_suministradas == [3]

def test_blank_razon_social():
    with pytest.raises(ValidationError):
        ProveedorCreate(**{"razon_social": "   ", "paises_operacion": [1], "certificaciones_sanitarias": [1], "categorias_suministradas": [1]})
