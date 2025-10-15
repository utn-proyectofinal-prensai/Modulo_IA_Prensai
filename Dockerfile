# Dockerfile optimizado para RunPod con GPU
FROM ubuntu:22.04

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

# Instalar NVIDIA drivers básicos (RunPod ya tiene GPU configurada)
RUN apt-get update && apt-get install -y \
    nvidia-utils-525 \
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

# Instalar dependencias de Python con upgrade de pip
RUN python -m pip install --upgrade pip

# Instalar dependencias críticas directamente
RUN pip install --no-cache-dir pandas==2.0.3 numpy==1.24.3 requests==2.31.0

# Instalar resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Verificar instalación de dependencias críticas
RUN python -c "import pandas; print('Pandas version:', pandas.__version__)"
RUN python -c "import requests; print('Requests version:', requests.__version__)"

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p Logs

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Exponer puertos de Ollama y Flask
EXPOSE 11434
EXPOSE 5000

# Variables de entorno para Flask
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=api_flask.py
ENV FLASK_ENV=production

# Health check para RunPod (verificar que Ollama esté funcionando)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Comando para ejecutar el script de inicio que levanta Ollama + handler
CMD ["/app/start.sh"]
