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

-- Mostrar bases de datos creadas
\l
