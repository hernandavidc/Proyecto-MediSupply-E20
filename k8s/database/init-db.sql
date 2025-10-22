-- Script de inicialización para PostgreSQL
-- Crea las bases de datos necesarias para los microservicios

-- Crear base de datos para suppliers si no existe
SELECT 'CREATE DATABASE suppliers_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'suppliers_db')\gexec

-- Conectar a la base de datos de suppliers
\c suppliers_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear base de datos para users si no existe (ya debería existir)
SELECT 'CREATE DATABASE users_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'users_db')\gexec

-- Conectar a la base de datos de users
\c users_db;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Mostrar bases de datos creadas
\l
