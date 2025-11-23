-- Migración: Agregar campo fotos a la tabla novedad_orden
-- Fecha: 2025-11-23
-- Descripción: Agrega soporte para almacenar fotos adjuntas a las novedades

-- Agregar columna fotos si no existe
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'novedad_orden' 
        AND column_name = 'fotos'
    ) THEN
        ALTER TABLE novedad_orden 
        ADD COLUMN fotos TEXT NULL;
        
        COMMENT ON COLUMN novedad_orden.fotos IS 'JSON array de URLs de fotos adjuntas a la novedad';
        
        RAISE NOTICE 'Columna fotos agregada exitosamente a novedad_orden';
    ELSE
        RAISE NOTICE 'La columna fotos ya existe en novedad_orden';
    END IF;
END $$;

