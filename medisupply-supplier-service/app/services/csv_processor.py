import csv
import io
from typing import List, Dict, Any, Tuple, Optional
from pydantic import ValidationError
from app.schemas.product_schema import (
    ProductoCSV,
    ErrorValidacion,
    ResultadoCargaMasiva,
    ProductoResponse,
)
from app.services.product_service import ProductService
from sqlalchemy.orm import Session


class CSVProcessor:
    """Procesador de archivos CSV para carga masiva de productos"""

    # Columnas esperadas en el orden correcto
    COLUMNAS_ESPERADAS = [
        "sku",
        "nombre_producto",
        "proveedor_id",
        "ficha_tecnica_url",
        "ca_temp",
        "ca_humedad",
        "ca_luz",
        "ca_ventilacion",
        "ca_seguridad",
        "ca_envase",
        "org_tipo_medicamento",
        "org_fecha_vencimiento",
        "valor_unitario_usd",
        "certificaciones_sanitarias",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.product_service = ProductService(db)

    def procesar_archivo(
        self, file_content: bytes, rechazar_lote_ante_errores: bool = True
    ) -> ResultadoCargaMasiva:
        """
        Procesa un archivo CSV y carga los productos

        Args:
            file_content: Contenido del archivo CSV
            rechazar_lote_ante_errores: Si True, rechaza todo el lote si hay errores

        Returns:
            ResultadoCargaMasiva con estadísticas y errores
        """
        try:
            # Decodificar el archivo
            content_str = file_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(content_str), delimiter="|")

            # Validar columnas
            columnas_errores = self._validar_columnas(csv_reader.fieldnames)
            if columnas_errores:
                return ResultadoCargaMasiva(
                    total_lineas=0, exitosas=0, fallidas=0, errores=columnas_errores
                )

            # Procesar líneas
            return self._procesar_lineas(csv_reader, rechazar_lote_ante_errores)

        except UnicodeDecodeError:
            return ResultadoCargaMasiva(
                total_lineas=0,
                exitosas=0,
                fallidas=0,
                errores=[
                    ErrorValidacion(
                        linea=0,
                        campo="archivo",
                        error="El archivo no está codificado en UTF-8",
                    )
                ],
            )
        except Exception as e:
            return ResultadoCargaMasiva(
                total_lineas=0,
                exitosas=0,
                fallidas=0,
                errores=[
                    ErrorValidacion(
                        linea=0,
                        campo="archivo",
                        error=f"Error al procesar archivo: {str(e)}",
                    )
                ],
            )

    def _validar_columnas(
        self, columnas_archivo: Optional[List[str]]
    ) -> List[ErrorValidacion]:
        """Valida que el archivo tenga las columnas correctas"""
        errores = []

        if not columnas_archivo:
            errores.append(
                ErrorValidacion(
                    linea=0,
                    campo="columnas",
                    error="El archivo no tiene columnas definidas",
                )
            )
            return errores

        # Verificar que todas las columnas esperadas estén presentes
        columnas_faltantes = set(self.COLUMNAS_ESPERADAS) - set(columnas_archivo)
        if columnas_faltantes:
            errores.append(
                ErrorValidacion(
                    linea=0,
                    campo="columnas",
                    error=f'Faltan las siguientes columnas: {", ".join(columnas_faltantes)}',
                )
            )

        # Verificar columnas adicionales no esperadas
        columnas_extra = set(columnas_archivo) - set(self.COLUMNAS_ESPERADAS)
        if columnas_extra:
            errores.append(
                ErrorValidacion(
                    linea=0,
                    campo="columnas",
                    error=f'Columnas no esperadas encontradas: {", ".join(columnas_extra)}',
                )
            )

        return errores

    def _procesar_lineas(
        self, csv_reader, rechazar_lote_ante_errores: bool
    ) -> ResultadoCargaMasiva:
        """Procesa cada línea del CSV"""
        productos_creados = []
        errores = []
        total_lineas = 0
        exitosas = 0
        fallidas = 0

        for linea_num, fila in enumerate(
            csv_reader, start=2
        ):  # Empezar en 2 (después del header)
            total_lineas += 1

            resultado_linea = self._procesar_linea_individual(fila, linea_num)

            if resultado_linea["exitoso"]:
                productos_creados.append(resultado_linea["producto"])
                exitosas += 1
            else:
                errores.extend(resultado_linea["errores"])
                fallidas += 1

            # Si se debe rechazar el lote ante errores y hay errores, parar aquí
            if rechazar_lote_ante_errores and errores:
                break

        return ResultadoCargaMasiva(
            total_lineas=total_lineas,
            exitosas=exitosas,
            fallidas=fallidas,
            errores=errores,
            productos_creados=productos_creados,
        )

    def _procesar_linea_individual(
        self, fila: Dict[str, str], linea_num: int
    ) -> Dict[str, Any]:
        """Procesa una línea individual del CSV"""
        try:
            # Convertir fila a formato esperado por ProductoCSV
            producto_data = self._convertir_fila_a_producto(fila)

            # Validar con Pydantic
            producto_csv = ProductoCSV(**producto_data)

            # Convertir a formato de ProductoCreate
            producto_create_data = self._convertir_a_producto_create(producto_csv)

            # Crear producto usando el servicio existente
            producto_creado = self.product_service.crear_producto(
                producto_create_data, usuario_id=None, origen="CSV_MASIVO"
            )

            return {
                "exitoso": True,
                "producto": ProductoResponse.model_validate(producto_creado),
                "errores": [],
            }

        except ValidationError as e:
            errores = []
            for error in e.errors():
                errores.append(
                    ErrorValidacion(
                        linea=linea_num,
                        campo=error["loc"][0] if error["loc"] else "desconocido",
                        error=error["msg"],
                        valor=(
                            str(fila.get(error["loc"][0], "")) if error["loc"] else None
                        ),
                    )
                )
            return {"exitoso": False, "producto": None, "errores": errores}

        except ValueError as e:
            return {
                "exitoso": False,
                "producto": None,
                "errores": [
                    ErrorValidacion(linea=linea_num, campo="negocio", error=str(e))
                ],
            }

        except Exception as e:
            return {
                "exitoso": False,
                "producto": None,
                "errores": [
                    ErrorValidacion(
                        linea=linea_num,
                        campo="sistema",
                        error=f"Error inesperado: {str(e)}",
                    )
                ],
            }

    def _convertir_fila_a_producto(self, fila: Dict[str, str]) -> Dict[str, Any]:
        """Convierte una fila del CSV al formato esperado por ProductoCSV"""
        # Construir condiciones de almacenamiento
        condiciones = {}
        for campo in [
            "ca_temp",
            "ca_humedad",
            "ca_luz",
            "ca_ventilacion",
            "ca_seguridad",
            "ca_envase",
        ]:
            if fila.get(campo) and fila[campo].strip():
                condiciones[campo] = fila[campo].strip()

        # Construir organización
        organizacion = {}
        if fila.get("org_tipo_medicamento") and fila["org_tipo_medicamento"].strip():
            organizacion["org_tipo_medicamento"] = fila["org_tipo_medicamento"].strip()
        if fila.get("org_fecha_vencimiento") and fila["org_fecha_vencimiento"].strip():
            organizacion["org_fecha_vencimiento"] = fila[
                "org_fecha_vencimiento"
            ].strip()

        return {
            "sku": fila.get("sku", "").strip(),
            "nombre_producto": fila.get("nombre_producto", "").strip(),
            "proveedor_id": (
                int(fila.get("proveedor_id", 0)) if fila.get("proveedor_id") else 0
            ),
            "ficha_tecnica_url": fila.get("ficha_tecnica_url", "").strip() or None,
            "condicion_almacenamiento": condiciones if condiciones else None,
            "organizacion": organizacion if organizacion else None,
            "valor_unitario_usd": (
                float(fila.get("valor_unitario_usd", 0))
                if fila.get("valor_unitario_usd")
                else 0.0
            ),
            "certificaciones_sanitarias": fila.get(
                "certificaciones_sanitarias", ""
            ).strip()
            or None,
        }

    def _convertir_a_producto_create(self, producto_csv: ProductoCSV) -> Dict[str, Any]:
        """Convierte ProductoCSV a formato ProductoCreate"""
        # Convertir condiciones de almacenamiento al formato esperado
        condiciones = None
        if producto_csv.condicion_almacenamiento:
            condiciones = {
                "temperatura": producto_csv.condicion_almacenamiento.ca_temp,
                "humedad": producto_csv.condicion_almacenamiento.ca_humedad,
                "luz": producto_csv.condicion_almacenamiento.ca_luz,
                "ventilacion": producto_csv.condicion_almacenamiento.ca_ventilacion,
                "seguridad": producto_csv.condicion_almacenamiento.ca_seguridad,
                "envase": producto_csv.condicion_almacenamiento.ca_envase,
            }

        # Convertir organización al formato esperado
        organizacion = None
        if producto_csv.organizacion:
            organizacion = {
                "tipo_medicamento": producto_csv.organizacion.org_tipo_medicamento,
                "fecha_vencimiento": producto_csv.organizacion.org_fecha_vencimiento,
            }

        return {
            "sku": producto_csv.sku,
            "nombre_producto": producto_csv.nombre_producto,
            "proveedor_id": producto_csv.proveedor_id,
            "ficha_tecnica_url": producto_csv.ficha_tecnica_url,
            "condiciones": condiciones,
            "organizacion": organizacion,
            "tipo_medicamento": (
                producto_csv.organizacion.org_tipo_medicamento
                if producto_csv.organizacion
                else None
            ),
            "fecha_vencimiento": (
                producto_csv.organizacion.org_fecha_vencimiento
                if producto_csv.organizacion
                else None
            ),
            "valor_unitario_usd": producto_csv.valor_unitario_usd,
            "certificaciones": producto_csv.certificaciones_sanitarias,
        }
