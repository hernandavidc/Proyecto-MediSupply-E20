#!/bin/bash
# Script para ejecutar todos los tests
echo "🚀 Ejecutando todos los tests..."
python -m pytest tests/ -v --tb=short
