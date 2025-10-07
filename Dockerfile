# Usar Python 3.11 slim como base principal
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y Ollama
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instalar Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Crear usuario para Ollama (por seguridad)
RUN groupadd -r ollama && useradd -r -g ollama ollama

# Crear directorio para Ollama
RUN mkdir -p /root/.ollama && chown -R ollama:ollama /root/.ollama

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p Logs

# Exponer puertos (8080 para Flask, 11434 para Ollama)
EXPOSE 8080 11434

# Variable de entorno para Flask
ENV FLASK_APP=api_flask.py
ENV FLASK_ENV=production

# Script de inicio que ejecuta Ollama en background y luego la API
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Comando para ejecutar el script de inicio
CMD ["/start.sh"]
