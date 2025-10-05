# 🚀 Deployment en Google Cloud Run

## 📋 Archivos creados para deployment

- `Dockerfile` - Configuración del container
- `.dockerignore` - Archivos a excluir del build
- `requirements.txt` - Dependencias de Python
- `app.yaml` - Configuración de Google Cloud Run

## 🔧 Variables de entorno requeridas

Configurar en Google Cloud Console:

```bash
# OpenAI API (OBLIGATORIO)
OPENAI_API_KEY=tu_openai_api_key_aqui

# Ollama (opcional, para fallback local)
OLLAMA_BASE_URL=http://localhost:11434

# Configuración de la aplicación
FLASK_ENV=production
PORT=8080
LOG_LEVEL=INFO
DEFAULT_LIMITE_TEXTO=14900
```

## 🚀 Comandos para deployment

### 1. Build y push a Google Container Registry
```bash
# Configurar proyecto
gcloud config set project TU_PROJECT_ID

# Build de la imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/prensai-api

# Deploy a Cloud Run
gcloud run deploy prensai-api \
  --image gcr.io/TU_PROJECT_ID/prensai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --port 8080 \
  --set-env-vars OPENAI_API_KEY=tu_api_key
```

### 2. Con GPU (si es necesario)
```bash
gcloud run deploy prensai-api \
  --image gcr.io/TU_PROJECT_ID/prensai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 8Gi \
  --cpu 4 \
  --accelerator type=nvidia-t4,count=1 \
  --port 8080
```

## 🔍 Verificación

1. **Health check**: `GET https://tu-url.run.app/health`
2. **Test básico**: Usar curl con una URL de prueba
3. **Logs**: Verificar en Google Cloud Console

## 💰 Consideraciones de costo

- **Sin GPU**: ~$0.10-0.50 por request
- **Con GPU**: ~$0.50-2.00 por request
- **Escalado a 0**: No hay costo cuando no hay requests

## 🔧 Troubleshooting

- Verificar variables de entorno
- Revisar logs en Google Cloud Console
- Confirmar que el puerto 8080 está expuesto
- Validar que todas las dependencias están en requirements.txt
