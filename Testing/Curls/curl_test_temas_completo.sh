#!/bin/bash

# ============================================================================
# CURL TEST: Clasificación de Temas Completa con /procesar-noticias
# ============================================================================
# Este script prueba la clasificación de temas usando el endpoint real
# con todos los URLs del test_clasificar_tema_gpt.py
# ============================================================================

# Detectar si ngrok está activo
if pgrep -f "ngrok" > /dev/null; then
    # ngrok está activo, obtener la URL
    API_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url']) if data['tunnels'] else print('http://localhost:5000')")
    echo "🌐 Usando ngrok: $API_URL"
else
    # ngrok no está activo, usar localhost
    API_URL="http://localhost:5000"
    echo "🏠 ngrok no detectado, usando localhost: $API_URL"
fi

echo "🧪 TEST: Clasificación de Temas Completa con /procesar-noticias"
echo "📊 Endpoint: /procesar-noticias"
echo "🌐 URL: $API_URL"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83794060",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=86687392",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24340866",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89356448",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85875989",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=87565297",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85044950",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=86911152",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20340562",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19581596",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19246424",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=15633461",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89317383",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89311718",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84985229",
      "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84990078",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19619285",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=15613613",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24338399",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24262318",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208"
    ],
    "temas": [
      "Entre el varón alemán y el amante argentino: peripecias de una mujer liberal de los años 20",
      "Juventus Lyrica",
      "¡URGENTE!",
      "34° Fiesta Nacional del Chamamé",
      "40 años Barrio Chino",
      "40 años de Camila",
      "9 de Julio en la Feria de Mataderos",
      "Abasto Barrio Cultural",
      "BAFICI",
      "Recorrido por eventos y estrenos",
      "Anuncio de obras CCGSM",
      "Centenario elencos estables",
      "Premios municipales y nacionales"
    ],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn", "Gerardo Grieco", "Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"],
    "tema_default": "Actividades Programadas"
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"
