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


echo "🎯 Probando: es_agenda_gpt con MUESTRA AMPLIADA (SÍ y NO agenda)"
echo "============================================================"

curl -X POST $API_URL/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23249425",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=18314993"
    ],
    "temas": ["Día Internacional de los Museos", "Cultura", "Feria de Mataderos", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn","Gerardo Grieco","Jorge Macri"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"],
    "tema_default": "Actividades programadas"
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"

echo "🎯 RESULTADO ESPERADO:"
echo "   - Las primeras 14 deben clasificarse como 'AGENDA'"
echo "   - Las últimas 9 deben clasificarse como 'NOTA' o 'DECLARACIÓN' (NO agenda)"

