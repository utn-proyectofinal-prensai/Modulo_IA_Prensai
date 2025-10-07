#!/bin/bash

# Script de inicio para ejecutar Ollama en background y luego la API Flask

echo "🚀 Iniciando servicio Ollama..."

# Iniciar Ollama en background
ollama serve &
OLLAMA_PID=$!

echo "⏳ Esperando que Ollama esté listo..."
sleep 10

# Verificar que Ollama esté funcionando
echo "🔍 Verificando estado de Ollama..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama está funcionando"
        break
    fi
    echo "⏳ Esperando Ollama... (intento $i/30)"
    sleep 2
done

# Verificar que el modelo esté disponible (ya fue descargado en build)
echo "📥 Verificando modelo llama3.1:8b..."
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Modelo llama3.1:8b disponible (pre-cargado en imagen)"
else
    echo "⚠️ ADVERTENCIA: Modelo no encontrado, descargando..."
    ollama pull llama3.1:8b
    echo "✅ Modelo descargado"
fi

# Iniciar la API Flask con Gunicorn
echo "🚀 Iniciando API Flask con Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 900 api_flask:app

# Si la API se cierra, terminar Ollama también
echo "🛑 Cerrando Ollama..."
kill $OLLAMA_PID
