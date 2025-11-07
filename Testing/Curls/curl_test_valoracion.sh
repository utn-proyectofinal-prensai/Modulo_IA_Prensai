#!/bin/bash

# ============================================================================
# CURL TEST: Valoración de noticia específica con /procesar-noticias
# ============================================================================
# Este script prueba la valoración y heurística de menciones para el artículo
# de Paco Ignacio Taibo II, permitiendo verificar el ajuste reciente del prompt.
# ============================================================================

# Detectar si ngrok está activo
if pgrep -f "ngrok" > /dev/null 2>&1; then
    API_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url']) if data.get('tunnels') else print('http://localhost:5000')")
    echo "🌐 Usando ngrok: $API_URL"
else
    API_URL="http://localhost:5000"
    echo "🏠 ngrok no detectado, usando localhost: $API_URL"
fi

echo "🧪 TEST: Valoración puntual con /procesar-noticias"
echo "📊 Endpoint: /procesar-noticias"
echo "🌐 URL: $API_URL"
echo "============================================================"

curl -X POST "$API_URL/procesar-noticias" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=35410529"
    ],
    "temas": [
      "Nochde de los museos",
      "Campaña Solidaria",
      "Recortes Presupuestarios",
      "Agravios"
    ],
    "menciones": [
      "Gabriela Ricardes",
      "Jorge Macri"
    ],
    "ministro_key_words": [
      "Gabriela Ricardes",
      "Ministra de Cultura",
      "Jorge Macri"
    ],
    "ministerios_key_words": [
      "Ministerio de Cultura",
      "Ministerio de Cultura de Buenos Aires"
    ],
    "tema_default": "Actividades Programadas"
  }'

echo ""
echo "✅ Curl ejecutado. Revisá la respuesta JSON para evaluar la valoración."

