#!/bin/bash

# ==============================================================================
# CURL PARA TESTING RÁPIDO EN GOOGLE CLOUD RUN - 2 NOTICIAS
# ==============================================================================

# URL de la API en Cloud Run
CLOUD_RUN_URL="https://prensai-api-2857713417.us-central1.run.app"

echo ""
echo "☁️  TESTING GOOGLE CLOUD RUN - MINI"
echo "============================================================"
echo "🌐 URL: $CLOUD_RUN_URL"
echo "📊 Endpoint: /procesar-noticias"
echo "🎯 Total URLs: 2 noticias"
echo "⏱️  Timeout: 300s (5 min)"
echo "============================================================"
echo ""
echo "🚀 Iniciando request..."
echo ""

time curl -X POST $CLOUD_RUN_URL/procesar-noticias \
  -H "Content-Type: application/json" \
  --max-time 300 \
  -v \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades programadas", "Tango BA", "Presentaciones"],
    "tema_default": "Cultura",
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn", "Gerardo Grieco", "Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }' | python3 -m json.tool

echo ""
echo "============================================================"
echo "✅ Request completado"
echo ""

