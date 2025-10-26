# MediSupply Supplier Service

Microservicio que implementa la gestión de proveedores y catálogos de productos para MediSupply.

## 📋 Estructura

```
app/
├── main.py              # Aplicación FastAPI principal
├── core/                # Configuración, base de datos, dependencias
├── models/              # Modelos SQLAlchemy (Proveedor, Producto, etc.)
├── schemas/             # Schemas Pydantic para validación
├── services/            # Lógica de negocio
└── api/v1/             # Rutas de la API
```

## 🌐 Endpoints Principales

### Catálogos
- `GET /api/v1/paises` - Listar países
- `GET /api/v1/certificaciones` - Listar certificaciones sanitarias
- `GET /api/v1/categorias-suministros` - Listar categorías

### Proveedores
- `GET /api/v1/proveedores` - Listar proveedores
- `POST /api/v1/proveedores` - Crear proveedor
- `GET /api/v1/proveedores/{id}` - Obtener proveedor
- `PUT /api/v1/proveedores/{id}` - Actualizar proveedor
- `DELETE /api/v1/proveedores/{id}` - Eliminar proveedor

### Productos
- `GET /api/v1/productos` - Listar productos
- `POST /api/v1/productos` - Crear producto
- `POST /api/v1/productos/bulk-upload` - Carga masiva de productos (CSV)

### Otros
- `GET /` - Información del servicio
- `GET /healthz` - Health check

## 🗄️ Configuración de Base de Datos

**IMPORTANTE**: El servicio soporta dos modos según el entorno:

### Desarrollo Local (SQLite)
```bash
DATABASE_URL=sqlite:///./supplier.db
```
- Usado para desarrollo y testing local
- Facilita ejecutar tests sin dependencias externas

### Producción (PostgreSQL)
```bash
DATABASE_URL=postgresql://user:password@postgres-service:5432/suppliers_db
```
- **Requerido en Kubernetes/GKE**
- Configurado en `k8s/services/supplier-service/supplier-service-secret.yaml`

Ver `DATABASE_CONFIG.md` para más detalles.

## 🚀 Uso Local

### Prerrequisitos
- Python 3.13+
- PostgreSQL (opcional, para producción)

### Configuración

1. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
export DATABASE_URL="sqlite:///./supplier.db"
export SECRET_KEY="test_secret_key"
```

4. **Ejecutar el servicio:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El servicio estará disponible en `http://localhost:8000`

### Con Docker

```bash
docker build -t medisupply-supplier-service .
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./supplier.db" \
  -e SECRET_KEY="your-secret-key" \
  medisupply-supplier-service
```

## 🧪 Testing

```bash
# Todos los tests
pytest tests/ -v

# Tests unitarios
pytest tests/unit/ -v

# Tests de integración
pytest tests/integration/ -v

# Tests end-to-end
pytest tests/e2e/ -v

# Con cobertura
pytest tests/ -v --cov=app --cov-report=html
```

Ver `TESTING_README.md` para más detalles sobre los tests.

## 📦 Carga Masiva de Productos

El servicio incluye funcionalidad de carga masiva de productos vía CSV:

```bash
curl -X POST "http://localhost:8000/api/v1/productos/bulk-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ejemplo_productos.csv" \
  -F "reject_on_errors=true"
```

Ver `BULK_UPLOAD_README.md` para más detalles sobre el formato CSV y ejemplos.

## 🚢 Deploy en Kubernetes

El servicio incluye un `initContainer` que:
1. Espera a que PostgreSQL esté listo
2. Inicializa la base de datos con datos de catálogos

Ver `k8s/services/supplier-service/` para los manifestos de Kubernetes.

## 📚 Documentación Adicional

- `DATABASE_CONFIG.md` - Configuración detallada de base de datos
- `TESTING_README.md` - Estrategia de testing
- `BULK_UPLOAD_README.md` - Documentación de carga masiva
- `INIT_DATABASE_README.md` - Inicialización de base de datos

## 🔧 Variables de Entorno

| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `DATABASE_URL` | URL de conexión a base de datos | `sqlite:///./supplier.db` |
| `SECRET_KEY` | Clave secreta para JWT | `replace_with_secure_secret` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración de tokens | `30` |
| `DEBUG` | Modo debug | `false` |
| `HOST` | Host del servicio | `0.0.0.0` |
| `PORT` | Puerto del servicio | `8000` |

