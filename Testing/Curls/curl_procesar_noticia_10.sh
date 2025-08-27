#!/bin/bash

# Detectar automáticamente si ngrok está activo
if pgrep -x "ngrok" > /dev/null; then
    # Obtener la URL pública de ngrok
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$NGROK_URL" ]; then
        API_URL="$NGROK_URL"
        echo "🌐 ngrok detectado: $API_URL"
    else
        API_URL="http://localhost:5000"
        echo "⚠️  ngrok activo pero no se pudo obtener URL pública, usando localhost"
    fi
else
    API_URL="http://localhost:5000"
    echo "🏠 Usando API local: $API_URL"
fi

echo ""
echo "📊 Endpoint: /procesar-noticias"
echo "🌐 URL: $API_URL"
echo "🎯 Probando: CURL_procesar_noticia_10"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24347481",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196084",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24185308",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24257893",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23662034",
      "https://culturagcba.clientes.ejescom/noticia_completa.cfm?id=23595633",
      "https://culturagcba.clientes.ejeZ.com/noticia_completa.cfm?id=23595797"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades programadas", "Tango BA", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn","Gerardo Grieco","Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }'

echo ""
echo "🚀 Prueba Endpoint procesar-noticias"
