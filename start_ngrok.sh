#!/bin/bash

# Script para levantar ngrok con dominio fijo (Dev Domain gratuito)
# Configura tu dominio aquí después de reclamarlo en: https://dashboard.ngrok.com/cloud-edge/domains

# Dev Domain fijo (gratuito)
NGROK_DOMAIN="unsallow-frankie-incubative.ngrok-free.dev"

# Puerto local (siempre 5000 para Flask)
PORT=5000

# Verificar si el dominio está configurado
if [ "$NGROK_DOMAIN" = "tu-dominio.ngrok-free.app" ]; then
    echo "⚠️  ADVERTENCIA: Debes configurar tu Dev Domain en este script."
    echo "📝 Pasos:"
    echo "   1. Ve a: https://dashboard.ngrok.com/cloud-edge/domains"
    echo "   2. Reclama tu Dev Domain gratuito"
    echo "   3. Edita este script (línea 7) y reemplaza 'tu-dominio.ngrok-free.app' con tu dominio"
    echo ""
    echo "🔄 Levantando ngrok con dominio aleatorio (cambiará cada vez)..."
    ngrok http $PORT
else
    echo "🚀 Levantando ngrok con dominio fijo: $NGROK_DOMAIN"
    echo "📡 Puerto local: $PORT"
    ngrok http --domain=$NGROK_DOMAIN $PORT
fi

