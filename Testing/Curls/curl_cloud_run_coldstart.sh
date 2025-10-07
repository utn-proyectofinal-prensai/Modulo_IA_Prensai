#!/bin/bash

# ==============================================================================
# TEST DE COLD START - GOOGLE CLOUD RUN
# Usa health check para medir tiempo de arranque desde cero
# ==============================================================================

CLOUD_RUN_URL="https://prensai-api-2857713417.us-central1.run.app"

echo ""
echo "❄️  COLD START TEST - GOOGLE CLOUD RUN"
echo "============================================================"
echo "🌐 URL: $CLOUD_RUN_URL/health"
echo "📝 Nota: Si la instancia está dormida, esto medirá el cold start"
echo "============================================================"
echo ""
echo "🚀 Iniciando request..."
echo ""

time curl -s $CLOUD_RUN_URL/health \
  -w "\n\n⏱️  Tiempo de respuesta: %{time_total}s\n📊 HTTP Status: %{http_code}\n🔌 Tiempo conexión: %{time_connect}s\n⚡ Tiempo primer byte: %{time_starttransfer}s\n" \
  | head -20

echo ""
echo "============================================================"
echo "✅ Test completado"
echo ""
echo "📊 INTERPRETACIÓN:"
echo "  - < 1s:    Instancia ya estaba activa (warm)"
echo "  - 30-60s:  Cold start RÁPIDO (modelo pre-cargado) ✅"
echo "  - > 2min:  Cold start LENTO (descargando modelo) ❌"
echo ""

