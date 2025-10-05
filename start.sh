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

# Descargar el modelo llama3.1:8b si no está disponible
echo "📥 Verificando modelo llama3.1:8b..."
if ! ollama list | grep -q "llama3.1:8b"; then
    echo "⬇️ Descargando modelo llama3.1:8b..."
    ollama pull llama3.1:8b
    echo "✅ Modelo descargado"
else
    echo "✅ Modelo llama3.1:8b ya está disponible"
fi

# Iniciar la API Flask
echo "🚀 Iniciando API Flask..."
python api_flask.py

# Si la API se cierra, terminar Ollama también
echo "🛑 Cerrando Ollama..."
kill $OLLAMA_PID
