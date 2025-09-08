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

echo "🧪 TEST: Clasificación de temas con tema_agenda"
echo "📊 Endpoint: /procesar-noticias"
echo "🌐 URL: $API_URL"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24069245",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24136111",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24049682",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23932884",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23370658",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23432671",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23231721",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22704241"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades", "Tango BA", "Presentaciones", "Eventos Especiales"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn","Gerardo Grieco","Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"],
    "tema_agenda": "Eventos Culturales de la Semana"
  }'

echo ""

