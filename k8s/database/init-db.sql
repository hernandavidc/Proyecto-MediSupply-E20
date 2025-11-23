-- Script de inicialización para PostgreSQL
-- Crea las bases de datos necesarias para los microservicios

-- Crear base de datos para suppliers si no existe
SELECT 'CREATE DATABASE suppliers_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'suppliers_db')\gexec

-- Conectar a la base de datos de suppliers
\c suppliers_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear base de datos para users si no existe
SELECT 'CREATE DATABASE users_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'users_db')\gexec

-- Conectar a la base de datos de users
\c users_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear base de datos para clients si no existe
SELECT 'CREATE DATABASE clients_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'clients_db')\gexec

-- Conectar a la base de datos de clients
\c clients_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla de clientes
CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(50) UNIQUE NOT NULL,
    direccion VARCHAR(500) NOT NULL,
    nombre_contacto VARCHAR(255) NOT NULL,
    telefono_contacto VARCHAR(20) NOT NULL,
    email_contacto VARCHAR(255) NOT NULL,
    is_validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Crear índices para optimizar búsquedas
CREATE INDEX IF NOT EXISTS idx_clients_nombre ON clients(nombre);
CREATE INDEX IF NOT EXISTS idx_clients_nit ON clients(nit);

-- Crear base de datos para orders si no existe
SELECT 'CREATE DATABASE orders_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'orders_db')\gexec

-- Conectar a la base de datos de orders
\c orders_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tipo enum para estado de orden
DO $$ BEGIN
    CREATE TYPE estado_orden AS ENUM ('ABIERTO', 'ENTREGADO', 'EN_ALISTAMIENTO', 'EN_REPARTO', 'DEVUELTO', 'POR_ALISTAR');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tipo enum para tipo de vehículo
DO $$ BEGIN
    CREATE TYPE tipo_vehiculo AS ENUM ('CAMION', 'VAN', 'TRACTOMULA');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tipo enum para tipo de novedad
DO $$ BEGIN
    CREATE TYPE tipo_novedad AS ENUM ('DEVOLUCION', 'CANTIDAD_DIFERENTE', 'MAL_ESTADO', 'PRODUCTO_NO_COINCIDE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Crear tabla de bodegas
CREATE TABLE IF NOT EXISTS bodegas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(500) NOT NULL,
    id_pais INTEGER NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    latitud NUMERIC(10, 8),
    longitud NUMERIC(11, 8)
);

-- Crear índice para id_pais en bodegas
CREATE INDEX IF NOT EXISTS idx_bodegas_id_pais ON bodegas(id_pais);

-- Crear tabla de vehículos
CREATE TABLE IF NOT EXISTS vehiculos (
    id SERIAL PRIMARY KEY,
    id_conductor INTEGER NOT NULL,
    placa VARCHAR(20) NOT NULL UNIQUE,
    tipo tipo_vehiculo NOT NULL,
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION,
    timestamp TIMESTAMP
);

-- Crear índices para vehiculos
CREATE INDEX IF NOT EXISTS idx_vehiculos_id_conductor ON vehiculos(id_conductor);
CREATE INDEX IF NOT EXISTS idx_vehiculos_placa ON vehiculos(placa);

-- Crear tabla de órdenes
CREATE TABLE IF NOT EXISTS ordenes (
    id SERIAL PRIMARY KEY,
    fecha_entrega_estimada TIMESTAMP NOT NULL,
    id_vehiculo INTEGER REFERENCES vehiculos(id),
    id_cliente INTEGER NOT NULL,
    id_vendedor INTEGER NOT NULL,
    estado estado_orden NOT NULL DEFAULT 'ABIERTO',
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para ordenes
CREATE INDEX IF NOT EXISTS idx_ordenes_id_cliente ON ordenes(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ordenes_id_vendedor ON ordenes(id_vendedor);

-- Crear tabla de productos en bodega
CREATE TABLE IF NOT EXISTS bodega_producto (
    id_bodega INTEGER REFERENCES bodegas(id),
    id_producto INTEGER NOT NULL,
    lote VARCHAR(50) NOT NULL,
    cantidad INTEGER NOT NULL,
    dias_alistamiento INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id_bodega, id_producto, lote)
);

-- Crear tabla de productos en orden
CREATE TABLE IF NOT EXISTS orden_producto (
    id_orden INTEGER REFERENCES ordenes(id) ON DELETE CASCADE,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    PRIMARY KEY (id_orden, id_producto)
);

-- Crear tabla de novedades de orden
CREATE TABLE IF NOT EXISTS novedad_orden (
    id SERIAL PRIMARY KEY,
    id_pedido INTEGER REFERENCES ordenes(id) ON DELETE CASCADE,
    tipo tipo_novedad NOT NULL,
    descripcion VARCHAR(1000),
    fotos TEXT
);

-- Crear índice para id_pedido en novedad_orden
CREATE INDEX IF NOT EXISTS idx_novedad_orden_id_pedido ON novedad_orden(id_pedido);

-- Agregar comentario para el campo fotos
COMMENT ON COLUMN novedad_orden.fotos IS 'JSON array de URLs de fotos adjuntas a la novedad';

-- Mostrar bases de datos creadas
\l
