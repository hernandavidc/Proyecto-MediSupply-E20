# Ejemplo de Uso - Envío de Fotos en Novedades con Postman

## Configuración Rápida en Postman

### 1. Crear Novedad SIN Fotos

**Método**: `POST`  
**URL**: `http://localhost:8000/api/v1/novedades`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Body** (seleccionar `form-data`):
| Key | Value | Type |
|-----|-------|------|
| id_pedido | 1 | Text |
| tipo | MAL_ESTADO | Text |
| descripcion | Producto llegó dañado | Text |

### 2. Crear Novedad CON Fotos

**Método**: `POST`  
**URL**: `http://localhost:8000/api/v1/novedades`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Body** (seleccionar `form-data`):
| Key | Value | Type |
|-----|-------|------|
| id_pedido | 1 | Text |
| tipo | MAL_ESTADO | Text |
| descripcion | Producto llegó dañado - ver fotos | Text |
| fotos | [Seleccionar archivo imagen1.jpg] | File |
| fotos | [Seleccionar archivo imagen2.jpg] | File |

**IMPORTANTE**: Puedes agregar múltiples fotos usando el mismo nombre de campo "fotos" varias veces.

### 3. Respuesta Esperada

```json
{
    "id": 1,
    "id_pedido": 1,
    "tipo": "MAL_ESTADO",
    "descripcion": "Producto llegó dañado - ver fotos",
    "fotos": [
        "/uploads/novedades/550e8400-e29b-41d4-a716-446655440001.jpg",
        "/uploads/novedades/550e8400-e29b-41d4-a716-446655440002.jpg"
    ]
}
```

### 4. Ver las Fotos

Las fotos se pueden acceder directamente desde el navegador o cualquier cliente HTTP:

**URL de foto**: `http://localhost:8000/uploads/novedades/550e8400-e29b-41d4-a716-446655440001.jpg`

**Nota**: Las fotos son públicamente accesibles sin autenticación.

## Tipos de Novedad Disponibles

- `DEVOLUCION`
- `CANTIDAD_DIFERENTE`
- `MAL_ESTADO`
- `PRODUCTO_NO_COINCIDE`

## Validaciones

- Solo se aceptan archivos de imagen (`image/*`)
- Archivos que no sean imágenes son ignorados automáticamente
- El campo `fotos` es opcional
- Puedes enviar múltiples fotos en una sola petición

## Obtener Novedades con Fotos

### GET Single Novedad
```
GET http://localhost:8000/api/v1/novedades/{novedad_id}
```

### GET Novedades por Orden
```
GET http://localhost:8000/api/v1/novedades/orden/{orden_id}
```

### GET Todas las Novedades
```
GET http://localhost:8000/api/v1/novedades
```

Todas estas peticiones devuelven las novedades con el array de fotos incluido.

## Testing Local sin Autenticación

Si quieres probar sin autenticación (solo en desarrollo):

```bash
export AUTH_DISABLED=true
# Luego iniciar el servidor
```

Luego puedes hacer peticiones sin el header `Authorization`.

