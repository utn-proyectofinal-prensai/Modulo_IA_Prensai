#!/bin/bash

# Script de inicio optimizado para RunPod
echo "🚀 Iniciando API de Prensai IA en RunPod..."

# Iniciar Ollama en background con GPU
echo "🔥 Iniciando Ollama con soporte GPU..."
ollama serve &
OLLAMA_PID=$!

# Esperar a que Ollama esté listo
echo "⏳ Esperando que Ollama esté listo..."
sleep 15

# Verificar que Ollama esté funcionando (con reintentos)
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

# Mostrar información del sistema
echo "📊 Información del sistema:"
echo "GPU disponible: $(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null || echo 'No detectada')"
echo "Memoria GPU: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null || echo 'N/A') MB"

# Iniciar la API Flask
echo "🌐 Iniciando API Flask de Prensai IA..."
echo "📡 Endpoints disponibles:"
echo "  - GET /health (Health check)"
echo "  - POST /procesar-noticias (Procesar noticias)"
echo "  - POST /procesar-noticias-export-excel (Exportar a Excel)"
echo "  - POST /generate-informe (Generar informe)"
echo "  - POST /config/gpt-active (Configurar GPT)"
echo "  - POST /config/limite-texto (Configurar límite texto)"
echo "  - POST /config/estado (Estado configuración)"

# Verificar que Ollama esté funcionando antes de iniciar Flask
echo "🔍 Verificación final de Ollama..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama está funcionando correctamente"
        break
    fi
    echo "⏳ Esperando Ollama... (intento $i/30)"
    sleep 2
done

# Ejecutar la API Flask
echo "🚀 Iniciando API Flask..."
python3.11 api_flask.py

# Mantener el proceso activo y capturar señales
trap 'echo "🛑 Deteniendo servicios..."; kill $OLLAMA_PID 2>/dev/null; exit 0' SIGTERM SIGINT
wait
