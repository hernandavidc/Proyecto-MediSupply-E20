#!/bin/bash
# Script para ejecutar tests end-to-end
echo "🌐 Ejecutando tests end-to-end..."
python -m pytest tests/e2e/ -v -m "e2e" --tb=short
