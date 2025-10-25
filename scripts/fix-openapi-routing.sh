#!/bin/bash

# Script to fix OpenAPI routing issue
# This script applies the updated ingress and gateway configurations

set -e

echo "🔧 Fixing OpenAPI routing configuration..."

# Apply the updated ingress configuration
echo "📝 Applying updated ingress configuration..."
kubectl apply -f k8s/ingress/medisupply-ingress.yaml

# Apply the updated gateway configuration
echo "🌐 Applying updated gateway configuration..."
kubectl apply -f k8s/gateway/medisupply-gateway.yaml

echo "✅ OpenAPI routing configuration updated successfully!"
echo ""
echo "📋 Summary of changes:"
echo "  - Added /openapi.json route to user-service"
echo "  - Added /supplier-openapi.json route to supplier-service"
echo "  - Updated both ingress and gateway configurations"
echo ""
echo "🔍 You can now access:"
echo "  - Main API docs: http://34.8.129.243/docs"
echo "  - Supplier API docs: http://34.8.129.243/supplier-docs"
echo "  - OpenAPI JSON: http://34.8.129.243/openapi.json"
echo "  - Supplier OpenAPI JSON: http://34.8.129.243/supplier-openapi.json"
echo ""
echo "⏳ Please wait a few minutes for the changes to propagate..."
