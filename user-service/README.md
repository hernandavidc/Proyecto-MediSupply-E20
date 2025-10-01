# User Service - MediSupply

¡Hola! Este es el **microservicio de usuarios** para el sistema MediSupply. Es como un portero muy inteligente que cuida quién puede entrar y salir de nuestra aplicación médica.

## ¿Qué hace este microservicio?


- **Registre nuevas personas** 
- **Les dé llaves especiales** (tokens JWT) para entrar
- **Verifique que las llaves sean reales** cada vez que alguien quiere entrar
- **Te diga si está funcionando bien** (health check)

## Características Principales

- **Registro de usuarios** 
- **Generación de tokens JWT** 
- **Autenticación segura** 
- **Base de datos PostgreSQL** -
- **Compatible con Docker**
- **Compatible con Postman y Swagger** 

## Endpoints (Las puertas de entrada) - ¡MUY IMPORTANTE!

### **PARA POSTMAN (USA ESTOS):**

#### **Registrar Usuario**
```
POST http://localhost:8001/api/v1/users/register
Content-Type: application/json

{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "password": "miPassword123"
}
```

#### **Generar Token JWT** (¡EL MÁS IMPORTANTE!)
```
POST http://localhost:8001/api/v1/users/generate-token
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "password": "miPassword123"
}
```
**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### **Ver Mi Información** (requiere token)
```
GET http://localhost:8001/api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### **Ver Usuario por ID** (requiere token)
```
GET http://localhost:8001/api/v1/users/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **PARA SWAGGER UI (OAuth2):**
- `POST /api/v1/users/token` - **Generar token** (formulario OAuth2)

### **HEALTH CHECKS:**
```
POST http://localhost:8001/api/v1/users/generate-token
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "password": "miPassword123"
}
```
**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 👤 **Ver Mi Información** (requiere token)
```
GET http://localhost:8001/api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 👥 **Ver Usuario por ID** (requiere token)
```
GET http://localhost:8001/api/v1/users/123
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

###  **PARA SWAGGER UI (OAuth2):**
- `POST /api/v1/users/token` - **Generar token** (formulario OAuth2)

###  **HEALTH CHECKS:**
- `GET http://localhost:8001/health` - **¿Está funcionando el servicio?**
- `GET http://localhost:8001/api/v1/users/` - **¿Funciona la parte de usuarios?**

##  Guía Completa para Probar (Paso a Paso)

###  **Paso 1: Iniciar el servicio**
```bash
cd C:\Users\me.ruiz42\Documents\proyecto-maestria
docker-compose up --build -d
```

###  **Paso 2: Verificar que funciona**
```bash
# Abrir en navegador o Postman:
GET http://localhost:8001/health
```
**Debe responder:** `{"status": "healthy", "service": "user-service"}`

###  **Paso 3: Registrar un usuario**
**En Postman:**
- Método: `POST`
- URL: `http://localhost:8001/api/v1/users/register`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "María García",
  "email": "maria@test.com",
  "password": "password123"
}
```
**Respuesta esperada:** `201 Created` con datos del usuario

### **Paso 4: Generar token**
**En Postman:**
- Método: `POST`
- URL: `http://localhost:8001/api/v1/users/generate-token`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "email": "maria@test.com",
  "password": "password123"
}
```
**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJpYUB0ZXN0LmNvbSIsImV4cCI6MTY5ODQyMzQ1Nn0.xyz...",
  "token_type": "bearer"
}
```

### **Paso 5: Usar el token para ver tu información**
**En Postman:**
- Método: `GET`
- URL: `http://localhost:8001/api/v1/users/me`
- Headers: 
  - `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (el token del paso anterior)

## Comandos Útiles para Debuggear

### **Ver logs en tiempo real:**
```bash
docker-compose logs -f medisupply-user-service
```

### **Conectarse a la base de datos:**
```bash
docker exec -it medisupply-user-db psql -U user -d users_db
```

###  **Ver todos los usuarios en la DB:**
```sql
-- Dentro de psql:
\l              -- Ver bases de datos
\c users_db     -- Conectar a la base
\dt             -- Ver tablas
SELECT * FROM users;  -- Ver todos los usuarios
```

###  **Reiniciar todo:**
```bash
docker-compose down
docker-compose up --build -d
```

###  **Ver estado de contenedores:**
```bash
docker-compose ps
```

##  Estructura del Proyecto (Detallada)

```
user-service/                   #  Proyecto principal
├──  README.md                     #  Documentación principal del proyecto
├──  docker-compose.yml           #  Orquestación de todos los servicios
├──  DOCKER.md                     #  Documentación específica de Docker
├──  dev.sh                        #  Script de desarrollo rápido
├──  .gitignore                    #  Archivos ignorados por Git
│
└──  user-service/                 #  Microservicio de usuarios
    ├──  app/                      #  Aplicación principal FastAPI
    │   ├──  api/                  #  Endpoints y rutas
    │   │   ├──  v1/               #  Versión 1 de la API
    │   │   │   ├── user_routes.py   #  TODOS los endpoints de usuarios
    │   │   │   └── __init__.py      #  Inicialización del módulo
    │   │   └── __init__.py          #  Inicialización del módulo
    │   ├──  core/                 #  Núcleo del sistema
    │   │   ├── auth.py              #  Autenticación JWT y passwords
    │   │   ├── config.py            #  Configuraciones del sistema
    │   │   ├── database.py          #  Conexión a PostgreSQL
    │   │   ├── dependencies.py      #  Dependencias de FastAPI
    │   │   └── __init__.py          #  Inicialización del módulo
    │   ├──  models/               #  Modelos de base de datos
    │   │   ├── user.py              # Modelo User (SQLAlchemy)
    │   │   └── __init__.py          #  Inicialización del módulo
    │   ├──  schemas/              #  Validaciones y esquemas
    │   │   ├── user_schema.py       #  Schemas de usuarios (Pydantic)
    │   │   └── __init__.py          #  Inicialización del módulo
    │   ├──  services/             #  Lógica de negocio
    │   │   ├── user_service.py      #  Servicio principal de usuarios
    │   │   └── __init__.py          #  Inicialización del módulo
    │   ├── main.py                  #  Punto de entrada FastAPI
    │   └── __init__.py              #  Inicialización del módulo
    │
    ├──  Dockerfile                #  Instrucciones para crear imagen Docker
    ├──  requirements.txt          #  Dependencias de Python
    ├──  run.py                    #  Script para ejecutar localmente
    ├──  start.sh                  #  Script de inicio para Docker
    ├──  wait-for-db.sh            #  Script para esperar la base de datos
    │
    ├──  .env.example              #  Ejemplo de variables de entorno
    ├──  .env.docker               #  Variables específicas para Docker
    ├──  .dockerignore             #  Archivos ignorados por Docker
    │
    ├──  init-db/                  #  Scripts de inicialización de DB (vacío)
    ├──  core/                     #  Carpeta adicional (vacía)
    │
    └──  README.md                 #  Este archivo - Documentación completa
```

##  Archivos Importantes del Proyecto

###  **En la raíz del proyecto:**
- **`docker-compose.yml`** -  Configura todos los servicios (user-service + PostgreSQL)
- **`DOCKER.md`** -  Documentación específica de Docker
- **`dev.sh`** -  Script para desarrollo rápido

### **Archivos específicos de Docker:**
- **`Dockerfile`** - Instrucciones para crear la imagen del microservicio
- **`start.sh`** - Script que ejecuta Docker al iniciar el contenedor
- **`wait-for-db.sh`** - Espera que PostgreSQL esté listo antes de iniciar
- **`.dockerignore`** - Archivos que Docker debe ignorar
- **`.env.docker`** - Variables de entorno específicas para Docker

### **Archivos de configuración:**
- **`.env.example`** - Plantilla de variables de entorno
- **`requirements.txt`** - Todas las librerías de Python necesarias
- **`run.py`** - Para ejecutar el servicio localmente (sin Docker)

### **Carpetas especiales:**
- **`init-db/`** - Scripts SQL que se ejecutan al crear la base de datos (actualmente vacía)
- **`core/`** - Carpeta adicional para futuras extensiones (actualmente vacía)

## ¿Cómo funciona cada archivo? (Súper Detallado)

### `user_routes.py` - El Centro de Control
```python
# ENDPOINTS PARA POSTMAN (JSON):
@router.post("/register")           # Registrar usuario
@router.post("/generate-token")     # Generar JWT token (¡EL IMPORTANTE!)

# ENDPOINTS PARA SWAGGER (OAuth2):
@router.post("/token")              # Token con formulario OAuth2

# ENDPOINTS PROTEGIDOS (necesitan token):
@router.get("/me")                  # Mi información
@router.get("/{user_id}")          # Usuario por ID

# HEALTH CHECKS:
@router.get("/")                    # Estado del servicio
```

### `user_service.py` - El Cerebro
```python
# Funciones principales:
create_user()       # Crear nuevo usuario (hashea password)
authenticate_user() # Verificar email + password
login_user()        # Generar JWT token si auth es correcta
get_user_by_email() # Buscar usuario por email
get_user()          # Buscar usuario por ID
```

### `auth.py` - El Guardián de Seguridad
```python
# Funciones de seguridad:
get_password_hash()   # Convierte "password123" → hash seguro
verify_password()     # Verifica si password coincide con hash
create_access_token() # Crea JWT token que expira en 30 min
verify_token()        # Verifica si token es válido
```

### `config.py` - Las Configuraciones
```python
# Variables importantes:
DATABASE_URL                 # postgresql://user:password@host:port/db
SECRET_KEY                   # Llave para firmar JWT tokens
ACCESS_TOKEN_EXPIRE_MINUTES  # Cuánto duran los tokens (30 min)
DEBUG                        # Si mostrar errores detallados
```

### `Dockerfile` - La Receta de la Caja Mágica
```dockerfile
# Es como una receta de cocina que le dice a Docker:
# 1. Usar Python 3.11 como base
# 2. Crear un usuario especial (no root) 
# 3. Copiar todos los archivos
# 4. Instalar las dependencias de requirements.txt
# 5. Configurar permisos de seguridad
# 6. Ejecutar start.sh al iniciar
```

### `start.sh` - El Iniciador Inteligente
```bash
# Script que se ejecuta cuando el contenedor inicia:
# 1. Espera a que PostgreSQL esté listo (wait-for-db.sh)
# 2. Crea las tablas en la base de datos si no existen
# 3. Inicia la aplicación FastAPI con Uvicorn
```

### `wait-for-db.sh` - El Paciente Ayudante
```bash
# Script que espera pacientemente:
# 1. Revisa cada segundo si PostgreSQL responde
# 2. Solo continúa cuando la base de datos está lista
# 3. Evita errores de "conexión rechazada"
```

### `.env.docker` - Configuración para Contenedores
```bash
# Variables especiales para Docker:
DATABASE_URL=postgresql://user:password@medisupply-user-db:5432/users_db
SECRET_KEY=clave-super-secreta-para-jwt
DEBUG=true
```

## Seguridad Implementada

- **Passwords hasheadas con bcrypt** - Nunca guardamos passwords en texto plano
- **JWT Tokens con expiración** - Los tokens se vencen en 30 minutos
- **Validación de emails** - Solo acepta emails válidos
- **Endpoints protegidos** - Algunos requieren token válido
- **CORS configurado** - Controla qué dominios pueden acceder
- **Variables de entorno** - Secretos no están en el código

## Docker Setup Completo

### **docker-compose.yml** incluye:
- **medisupply-user-service** (puerto 8001)
- **medisupply-user-db** (PostgreSQL, puerto 5433)
- **Red interna** (medisupply-network)
- **Volumen persistente** para la base de datos
- **Health checks** automáticos

### **Variables de entorno en Docker:**
```yaml
DATABASE_URL=postgresql://user:password@medisupply-user-db:5432/users_db
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
```

## Troubleshooting (Solución de Problemas)

### **Error 400 Bad Request**
**Problema:** Formato incorrecto de JSON
**Solución:** Verificar que Content-Type sea `application/json`

### **Error 401 Unauthorized** 
**Problema:** Token inválido o expirado
**Solución:** Generar nuevo token con `/generate-token`

### **Error 500 Internal Server Error**
**Problema:** Error en la base de datos o código
**Solución:** Ver logs: `docker-compose logs -f medisupply-user-service`

### **Servicio no responde**
**Problema:** Docker no está corriendo
**Solución:** 
```bash
docker-compose ps                    # Ver estado
docker-compose up --build -d        # Reiniciar
```

### **No puede conectar a la base de datos**
**Problema:** PostgreSQL no está listo
**Solución:** Esperar unos segundos, el script `start.sh` maneja esto

## URLs Importantes

- **Aplicación:** http://localhost:8001
- **Documentación Swagger:** http://localhost:8001/docs
- **Documentación ReDoc:** http://localhost:8001/redoc
- **Health Check:** http://localhost:8001/health
- **Base de datos:** localhost:5433 (usuario: `user`, password: `password`, db: `users_db`)

## Tecnologías Usadas

- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web súper rápido
- **PostgreSQL 15** - Base de datos robusta
- **JWT** - Tokens seguros
- **bcrypt** - Hash de passwords
- **Docker & Docker Compose** - Containerización
- **SQLAlchemy** - ORM para base de datos
- **Pydantic** - Validación de datos

