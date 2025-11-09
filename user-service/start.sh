#!/bin/bash
# start.sh - Script de inicio para el contenedor

set -e

echo "Starting User Service..."

# Paso 1: Esperar a que PostgreSQL esté escuchando (pg_isready solo verifica que escuche)
echo "Step 1: Waiting for PostgreSQL to be listening (max 60 seconds)..."
MAX_ATTEMPTS=30
ATTEMPT=0
DB_LISTENING=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if pg_isready -h medisupply-user-db -p 5432 -U user 2>/dev/null; then
        echo "✅ PostgreSQL is listening!"
        DB_LISTENING=true
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "PostgreSQL not listening, waiting... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ "$DB_LISTENING" = "false" ]; then
    echo "⚠️  PostgreSQL not listening after 60 seconds, continuing anyway..."
    echo "ℹ️  Service will retry database connections automatically (pool_pre_ping=True)"
fi

# Paso 2: Verificar que podemos hacer una conexión SQL real
# Esto asegura que la BD esté completamente inicializada y acepte conexiones
echo "Step 2: Verifying SQL connection (max 60 seconds)..."
MAX_ATTEMPTS=30
ATTEMPT=0
SQL_READY=false

# Leer credenciales desde variables de entorno
DB_HOST="${DB_HOST:-medisupply-user-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-user}"
DB_NAME="${DB_NAME:-users_db}"

# Intentar leer password desde DATABASE_URL si está disponible
DB_PASSWORD="${DB_PASSWORD:-}"
if [ -z "$DB_PASSWORD" ] && [ ! -z "$DATABASE_URL" ]; then
    # Extraer password de DATABASE_URL si está presente (formato: postgresql://user:password@host:port/db)
    DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p' || echo "")
fi

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    # Intentar conectar y ejecutar una query simple
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ SQL connection verified!"
        SQL_READY=true
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "SQL connection not ready, waiting... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ "$SQL_READY" = "false" ]; then
    echo "⚠️  SQL connection not ready after 60 seconds, continuing anyway..."
    echo "ℹ️  Service will retry database connections automatically (pool_pre_ping=True)"
    echo "ℹ️  Tables will be created automatically on first request"
else
    echo "✅ Database is fully ready!"
fi

# Ejecutar la aplicación (la aplicación es resiliente con pool_pre_ping=True)
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
