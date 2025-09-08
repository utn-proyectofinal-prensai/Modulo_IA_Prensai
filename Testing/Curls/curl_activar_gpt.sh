#!/bin/bash

# Configuración
API_TOKEN="prensai-config-2025"

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


echo "📊 Endpoint: /config/gpt-active"
echo "🔑 Token: $API_TOKEN"
echo "🌐 URL: $API_URL"


echo ""
echo "🔄 Activando GPT..."
curl -X POST $API_URL/config/gpt-active \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_TOKEN" \
  -d '{
    "gpt_active": true
  }'

echo ""
echo "✅ Curl ejecutado para activar GPT!"

