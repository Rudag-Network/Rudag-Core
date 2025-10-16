#!/bin/bash
# Conectar nodos RGD rápidamente - VERSIÓN MEJORADA
echo "🔗 Conectando a nodos RGD..."

# Conectar al nodo principal via HTTPS (Cloudflare Tunnel)
curl -X POST 'http://localhost:5000/addnode' \
  -H 'Content-Type: application/json' \
  -d '{"nodes": "rudagnetwork2.canariannode.uk"}'

echo ""

# También conectar al otro nodo
curl -X POST 'http://localhost:5000/addnode' \
  -H 'Content-Type: application/json' \
  -d '{"nodes": "rudagnetwork.canariannode.uk"}'

echo ""
echo "✅ Nodos RGD conectados ⚡"
echo "🔄 La red compartirá automáticamente estos peers con otros nodos"
