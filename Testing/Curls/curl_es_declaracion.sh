#!/bin/bash

# Detectar automáticamente si ngrok está activo
if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
    # ngrok está activo, obtener la URL pública
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['tunnels']:
        print(data['tunnels'][0]['public_url'])
    else:
        print('http://localhost:5000')
except:
    print('http://localhost:5000')
")
    API_URL="$NGROK_URL"
    echo "🌐 ngrok detectado, usando URL: $API_URL"
else
    # ngrok no está activo, usar localhost
    API_URL="http://localhost:5000"
    echo "🏠 ngrok no detectado, usando localhost: $API_URL"
fi

echo "📊 Endpoint: /procesar-noticias-export-excel"
echo "🌐 URL: $API_URL"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias-export-excel \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22704241",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22787748",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22651539",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22627194",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22583651",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22606260"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades", "Tango BA", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"

