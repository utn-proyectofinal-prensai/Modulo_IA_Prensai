# 🚀 Deployment en Google Cloud Run via GitHub + Cloud Build

## 📋 Archivos creados para deployment

- `Dockerfile` - Configuración del container (incluye Ollama + llama3.1:8b)
- `start.sh` - Script de inicio para Ollama + API Flask
- `.dockerignore` - Archivos a excluir del build
- `requirements.txt` - Dependencias de Python
- `cloudbuild.yaml` - Configuración de Cloud Build para deployment automático

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

## 🚀 Deployment Automático via GitHub + Cloud Build

### 1. Configurar Cloud Build Trigger
En Google Cloud Console:
1. **Cloud Build** → **Triggers** → **CREATE TRIGGER**
2. **Name**: `prensai-deployment`
3. **Event**: Push to a branch
4. **Source**: Conectar con GitHub (`utn-proyectofinal-prensai/Modulo_IA_Prensai`)
5. **Branch**: `deployment/google-cloud`
6. **Configuration**: Cloud Build configuration file
7. **Location**: `/cloudbuild.yaml`

### 2. Deployment Automático
- **Push a la rama** `deployment/google-cloud` → **Deploy automático**
- **Sin comandos manuales** → Todo se hace automáticamente

### 2. Con GPU (recomendado para Ollama)
```bash
gcloud run deploy prensai-api \
  --image gcr.io/TU_PROJECT_ID/prensai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 8Gi \
  --cpu 4 \
  --accelerator type=nvidia-t4,count=1 \
  --port 8080 \
  --timeout 900 \
  --set-env-vars OPENAI_API_KEY=tu_api_key
```

### 3. Sin GPU (solo CPU - más lento pero más barato)
```bash
gcloud run deploy prensai-api \
  --image gcr.io/TU_PROJECT_ID/prensai-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 8Gi \
  --cpu 4 \
  --port 8080 \
  --timeout 900 \
  --set-env-vars OPENAI_API_KEY=tu_api_key
```

## 🔍 Verificación

1. **Health check**: `GET https://tu-url.run.app/health`
2. **Test básico**: Usar curl con una URL de prueba
3. **Logs**: Verificar en Google Cloud Console

## 💰 Consideraciones de costo

- **Sin GPU**: ~$0.20-0.80 por request (más lento, Ollama en CPU)
- **Con GPU**: ~$0.50-2.00 por request (más rápido, Ollama en GPU)
- **Escalado a 0**: No hay costo cuando no hay requests
- **Tiempo de inicio**: ~2-3 minutos (descarga modelo llama3.1:8b en primer uso)

## 🔧 Troubleshooting

- Verificar variables de entorno
- Revisar logs en Google Cloud Console
- Confirmar que el puerto 8080 está expuesto
- Validar que todas las dependencias están en requirements.txt
