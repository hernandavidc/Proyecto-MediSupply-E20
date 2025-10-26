#!/bin/bash
# Script para ejecutar tests de integración
echo "🔗 Ejecutando tests de integración..."
python -m pytest tests/integration/ -v -m "integration" --tb=short
