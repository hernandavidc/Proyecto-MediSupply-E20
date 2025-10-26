"""
Enums para el sistema MediSupply
Contiene todas las listas predefinidas para proveedores según HU-001
"""

from enum import Enum


class PaisOperacion(str, Enum):
    """Países de operación permitidos"""

    COLOMBIA = "Colombia"
    PERU = "Perú"
    ECUADOR = "Ecuador"
    MEXICO = "México"


class CertificacionSanitaria(str, Enum):
    """Certificaciones sanitarias válidas"""

    FDA = "FDA"
    EMA = "EMA"
    INVIMA = "INVIMA"
    DIGEMID = "DIGEMID"
    COFEPRIS = "COFEPRIS"


class CategoriaSuministro(str, Enum):
    """Categorías de suministros que puede proveer"""

    MEDICAMENTOS_ESPECIALES = "Medicamentos especiales/controlados"
    INSUMOS_QUIRURGICOS = "Insumos quirúrgicos y hospitalarios"
    REACTIVOS_DIAGNOSTICOS = "Reactivos y pruebas diagnósticas"
    EQUIPOS_BIOMEDICOS = "Equipos y dispositivos biomédicos"
    OTROS_PPE = "Otros (PPE, materiales varios)"


class CapacidadCadenaFrio(str, Enum):
    """Capacidades de cadena de frío disponibles"""

    REFRIGERADO = "2–8°C"
    CONGELADO_NORMAL = "-20°C"
    ULTRA_CONGELADO = "-80°C"
    AMBIENTE = "Ambiente"


class EstadoProveedor(str, Enum):
    """Estados posibles del proveedor"""

    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"
    PENDIENTE_APROBACION = "pendiente_aprobacion"
