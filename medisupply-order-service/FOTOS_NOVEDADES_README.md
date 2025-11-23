# Guía de Uso: Adjuntar Fotos a Novedades

## Descripción
El endpoint `POST /api/v1/novedades` ahora soporta el envío de fotos adjuntas junto con la creación de una novedad.

## Cambios Implementados

### 1. Modelo de Base de Datos
Se agregó un nuevo campo `fotos` a la tabla `novedad_orden`:
- **Campo**: `fotos` (TEXT, nullable)
- **Contenido**: JSON array con las URLs de las fotos almacenadas
- **Ejemplo**: `["/uploads/novedades/abc123.jpg", "/uploads/novedades/def456.png"]`

### 2. Almacenamiento de Archivos
Las fotos se guardan en el sistema de archivos:
- **Directorio**: `uploads/novedades/`
- **Nombres**: UUID único + extensión original
- **Acceso**: Via endpoint público `/uploads/novedades/{filename}`

### 3. Endpoint Modificado

#### POST /api/v1/novedades

**Content-Type**: `multipart/form-data`

**Parámetros**:
- `id_pedido` (int, required): ID del pedido asociado
- `tipo` (TipoNovedad, required): Tipo de novedad
  - `DEVOLUCION`
  - `CANTIDAD_DIFERENTE`
  - `MAL_ESTADO`
  - `PRODUCTO_NO_COINCIDE`
- `descripcion` (string, optional): Descripción de la novedad
- `fotos` (file[], optional): Array de archivos de imagen

**Validación de Fotos**:
- Solo se aceptan archivos con content-type de imagen (`image/*`)
- Múltiples fotos pueden ser enviadas en una sola petición
- Los archivos que no sean imágenes son ignorados silenciosamente

## Ejemplos de Uso

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/novedades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "id_pedido=123" \
  -F "tipo=MAL_ESTADO" \
  -F "descripcion=Producto llegó en mal estado" \
  -F "fotos=@/path/to/foto1.jpg" \
  -F "fotos=@/path/to/foto2.jpg"
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/novedades"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

data = {
    "id_pedido": 123,
    "tipo": "MAL_ESTADO",
    "descripcion": "Producto llegó en mal estado"
}

files = [
    ("fotos", ("foto1.jpg", open("foto1.jpg", "rb"), "image/jpeg")),
    ("fotos", ("foto2.jpg", open("foto2.jpg", "rb"), "image/jpeg"))
]

response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())
```

### JavaScript (FormData)

```javascript
const formData = new FormData();
formData.append('id_pedido', '123');
formData.append('tipo', 'MAL_ESTADO');
formData.append('descripcion', 'Producto llegó en mal estado');
formData.append('fotos', fileInput1.files[0]);
formData.append('fotos', fileInput2.files[0]);

fetch('http://localhost:8000/api/v1/novedades', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Postman

1. Seleccionar método `POST`
2. URL: `http://localhost:8000/api/v1/novedades`
3. En la pestaña **Headers**:
   - Agregar `Authorization: Bearer YOUR_TOKEN`
4. En la pestaña **Body**:
   - Seleccionar `form-data`
   - Agregar campos:
     - `id_pedido`: 123 (Text)
     - `tipo`: MAL_ESTADO (Text)
     - `descripcion`: Producto llegó en mal estado (Text)
     - `fotos`: seleccionar archivo (File) - puede agregar múltiples con el mismo nombre
     - `fotos`: seleccionar otro archivo (File)

## Respuesta Exitosa

```json
{
  "id": 1,
  "id_pedido": 123,
  "tipo": "MAL_ESTADO",
  "descripcion": "Producto llegó en mal estado",
  "fotos": [
    "/uploads/novedades/550e8400-e29b-41d4-a716-446655440001.jpg",
    "/uploads/novedades/550e8400-e29b-41d4-a716-446655440002.jpg"
  ]
}
```

## Acceso a las Fotos

Las fotos pueden ser accedidas directamente via HTTP:

```bash
curl http://localhost:8000/uploads/novedades/550e8400-e29b-41d4-a716-446655440001.jpg
```

O en HTML:
```html
<img src="http://localhost:8000/uploads/novedades/550e8400-e29b-41d4-a716-446655440001.jpg" alt="Foto de novedad">
```

## Endpoints GET Actualizados

Todos los endpoints GET también devuelven el array de fotos:

### GET /api/v1/novedades
Lista todas las novedades con sus fotos.

### GET /api/v1/novedades/{novedad_id}
Obtiene una novedad específica con sus fotos.

### GET /api/v1/novedades/orden/{orden_id}
Lista todas las novedades de un pedido específico con sus fotos.

## Migración de Base de Datos

Para aplicar los cambios a una base de datos existente, ejecutar:

```bash
psql -U your_user -d your_database -f migrations/add_fotos_to_novedad_orden.sql
```

O si usas SQLite (desarrollo local):
```sql
ALTER TABLE novedad_orden ADD COLUMN fotos TEXT;
```

## Consideraciones de Producción

### Almacenamiento
En producción, se recomienda:
1. Usar un servicio de almacenamiento en la nube (AWS S3, Google Cloud Storage, etc.)
2. Implementar límites de tamaño de archivo
3. Implementar compresión de imágenes
4. Agregar validación de dimensiones

### Seguridad
- Las fotos son públicamente accesibles sin autenticación
- Para mayor seguridad, considerar:
  - Generar URLs con tokens temporales
  - Servir las fotos detrás de autenticación
  - Escanear archivos en busca de malware

### Performance
- Considerar implementar un CDN para servir las fotos
- Implementar caché de archivos estáticos
- Optimizar tamaño de imágenes automáticamente

## Estructura de Directorios

```
medisupply-order-service/
├── uploads/
│   └── novedades/
│       ├── 550e8400-e29b-41d4-a716-446655440001.jpg
│       ├── 550e8400-e29b-41d4-a716-446655440002.jpg
│       └── ...
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── novedad_orden_routes.py
│   ├── models/
│   │   └── novedad_orden.py
│   ├── schemas/
│   │   └── novedad_orden_schema.py
│   └── services/
│       └── novedad_orden_service.py
└── migrations/
    └── add_fotos_to_novedad_orden.sql
```

## Testing

Para probar el endpoint localmente sin autenticación:

```bash
# Habilitar modo sin auth
export AUTH_DISABLED=true

# Crear novedad con fotos
curl -X POST "http://localhost:8000/api/v1/novedades" \
  -F "id_pedido=1" \
  -F "tipo=MAL_ESTADO" \
  -F "descripcion=Test con foto" \
  -F "fotos=@test_image.jpg"
```

## Troubleshooting

### Error: "fotos field is required"
Asegúrate de usar `Content-Type: multipart/form-data` y no `application/json`.

### Error: "File not found"
Verifica que el directorio `uploads/novedades/` existe y tiene permisos de escritura.

### Las fotos no se muestran
Verifica que el endpoint `/uploads/` esté en la lista de `exempt_prefixes` en el middleware de autenticación.

### Error: "Invalid content type"
Solo se aceptan archivos con content-type de imagen. Verifica que los archivos sean imágenes válidas.

