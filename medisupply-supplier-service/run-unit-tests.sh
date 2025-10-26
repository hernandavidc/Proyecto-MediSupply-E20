#!/bin/bash
# Script para ejecutar tests unitarios
echo "🧪 Ejecutando tests unitarios..."
python -m pytest tests/unit/ -v -m "unit" --tb=short
