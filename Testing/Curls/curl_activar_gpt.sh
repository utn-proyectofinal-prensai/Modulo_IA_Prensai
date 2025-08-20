#!/bin/bash

echo "🚀 Activando modo GPT en la API..."
echo "📊 Endpoint: /config/gpt-active"
echo "🤖 GPT Active: true"
echo "=" * 60

curl -X POST http://localhost:5000/config/gpt-active \
  -H "Content-Type: application/json" \
  -d '{
    "gpt_active": true
  }'

echo ""
echo "✅ Curl ejecutado para activar GPT!"
echo "🤖 Modo GPT activado en la API"
echo "📊 Ahora puedes usar otros endpoints con GPT como primera opción"


curl -X POST http://localhost:5000/config/gpt-active \
  -H "Content-Type: application/json" \
  -d '{
    "gpt_active": false
  }'