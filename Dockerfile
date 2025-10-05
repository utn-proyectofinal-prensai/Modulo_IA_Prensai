# Usar Python 3.11 slim como base
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p Logs

# Exponer puerto 8080 (estándar de Google Cloud Run)
EXPOSE 8080

# Variable de entorno para Flask
ENV FLASK_APP=api_flask.py
ENV FLASK_ENV=production

# Comando para ejecutar la aplicación
CMD ["python", "api_flask.py"]
