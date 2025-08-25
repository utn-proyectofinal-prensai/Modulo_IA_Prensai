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

echo "🚀 Probando endpoint de exportación a Excel con 35 URLs para testing exhaustivo..."
echo "📊 Endpoint: /procesar-noticias-export-excel"
echo "🌐 URL: $API_URL"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias-export-excel \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83794060",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=86687392",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24340866",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24338399",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89357620",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89369109",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89342438",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85877128",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85888585",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85893377",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83422116",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83206972",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83083374",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=92495585",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85715754",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=87690826",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85044950",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84974527",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=77230700",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=77238032",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20274602",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20327053",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20263750",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19864288",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19727121",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19659559",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19670457",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19460749",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19227393",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19227244",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19214812",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19274449",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19246424",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19246910",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19253479"
    ],
    "temas": [
      "Actividades programadas",
      "Entre el varón alemán y el amante argentino: peripecias de una mujer liberal de los años 20",
      "Juventus Lyrica",
      "¡URGENTE!",
      "34° Fiesta Nacional del Chamamé",
      "40 años Barrio Chino",
      "40 años de Camila",
      "68a edición del Salón Manuel Belgrano",
      "6ta. Edición Premio Azcuy",
      "6ta. Edición Premio Azcuy",
      "9 de Julio en la Feria de Mataderos",
      "Abasto Barrio Cultural",
      "Actividades por la Revolución de Mayo",
      "Actividades programadas",
      "BAFICI",
      "Recorrido por eventos y estrenos",
      "Mecenazgo",
      "Anuncio de obras CCGSM",
      "Temporada 2025",
      "Apertura Temporada del Ballet 2025",
      "Apertura Temporada CTBA",
      "Premios municipales y nacionales",
      "Centenario elencos estables"
    ],
    "menciones": ["Gabriela Ricardes", "Jorge Macri", "Ministra de Cultura"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"
echo "🎯 Este test incluye 35 URLs para testing exhaustivo de la funcionalidad de declaraciones"