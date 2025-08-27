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
echo "📊 Endpoint: /procesar-noticias-export-excel"
echo "🌐 URL: $API_URL"
echo "🎯 Probando: es_agenda_gpt con MUESTRA AMPLIADA (SÍ y NO agenda)"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias-export-excel \
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
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595633",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595797",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22335229",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22335604",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23059116",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21949478",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24069245",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24136111",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24049682",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23932884",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23370658",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23432671",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24137173",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23973943",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23990873"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades programadas", "Tango BA", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn","Gerardo Grieco","Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"
echo "🎯 Objetivo: Verificar que es_agenda_gpt clasifique correctamente TODAS las URLs"
echo "📰 URLs: 23 noticias totales (14 que SÍ son agenda + 9 que NO son agenda)"
echo ""
echo "📋 DESGLOSE:"
echo "   ✅ URLs que SÍ son agenda: 14 (IDs: 24294600, 24302208, 24347481, 24196084, 24185308, 24257893, 23662034, 23595633, 23595797, 22335229, 22335604, 23059116, 21949478)"
echo "   ❌ URLs que NO son agenda: 9 (IDs: 24069245, 24136111, 24049682, 23932884, 23370658, 23432671, 24137173, 23973943, 23990873)"
echo ""
echo "🎯 RESULTADO ESPERADO:"
echo "   - Las primeras 14 deben clasificarse como 'AGENDA'"
echo "   - Las últimas 9 deben clasificarse como 'NOTA' o 'DECLARACIÓN' (NO agenda)"
echo ""
echo "🚀 MUESTRA AMPLIADA: Mejor evaluación de la precisión del prompt híbrido optimizado"
