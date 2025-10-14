# Dockerfile optimizado para RunPod con GPU
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Establecer variables de entorno para evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema, Python y herramientas necesarias
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear enlace simbólico para python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Instalar Ollama con soporte GPU
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Configurar Ollama para usar GPU
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_ORIGINS=*

# Crear usuario para Ollama (por seguridad)
RUN groupadd -r ollama && useradd -r -g ollama ollama

# Crear directorio para Ollama y configurar permisos
RUN mkdir -p /root/.ollama && chown -R ollama:ollama /root/.ollama

# Pre-descargar modelo llama3.1:8b durante el build (OPTIMIZACIÓN CLAVE)
RUN ollama serve & \
    OLLAMA_PID=$! && \
    echo "🚀 Esperando que Ollama inicie..." && \
    sleep 15 && \
    echo "📥 Descargando modelo llama3.1:8b..." && \
    ollama pull llama3.1:8b && \
    echo "✅ Modelo descargado exitosamente" && \
    kill $OLLAMA_PID && \
    wait $OLLAMA_PID 2>/dev/null || true

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p Logs

# Exponer puertos (5000 para Flask, 11434 para Ollama)
EXPOSE 5000 11434

# Variables de entorno para Flask
ENV FLASK_APP=api_flask.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Script de inicio optimizado para RunPod
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Health check para RunPod
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando para ejecutar el script de inicio
CMD ["/start.sh"]
