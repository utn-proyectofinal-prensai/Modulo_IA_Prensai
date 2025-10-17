# 🚀 Guía de Deployment en Cloud (Solo GPT)

Esta guía describe cómo deployar el proyecto en la nube **sin GPU ni Ollama**, usando **solo GPT** (OpenAI API).

---

## 📋 **Requisitos Previos**

1. ✅ Cuenta en OpenAI con API Key válida
2. ✅ Cuenta en plataforma cloud (Render, Railway, Fly.io, etc.)
3. ✅ Código del proyecto (rama `OpenAi_full`)

---

## 🏗️ **Arquitectura Cloud**

```
┌─────────────────────────────────────────┐
│         CLOUD SERVER (Sin GPU)          │
├─────────────────────────────────────────┤
│  api_flask.py                           │
│  O_Utils_GPT.py   ──► OpenAI API       │
│  O_Utils_Ollama.py (presente pero      │
│                     no se ejecuta)      │
│  Z_Utils.py                             │
└─────────────────────────────────────────┘
```

**Flujo:**
1. Request → api_flask.py
2. Procesa con GPT (gpt_active=True)
3. Si GPT falla → Intenta Ollama (falla gracefully)
4. Retorna resultado

---

## 📦 **Archivos a Deployar**

### ✅ **Incluir:**
```
api_flask.py
O_Utils_GPT.py
O_Utils_Ollama.py    ← Incluir (no crashea si no hay Ollama)
Z_Utils.py
requirements-cloud.txt
README
```

### ❌ **NO incluir:**
```
Testing/             ← Scripts locales
Data_Results/        ← Se genera en runtime
venv/                ← Se crea en cloud
.env                 ← Usar variables de entorno del proveedor
__pycache__/
*.pyc
```

---

## ⚙️ **Variables de Entorno (Cloud)**

Configurar en el panel de tu proveedor cloud:

```bash
# OBLIGATORIA
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# OPCIONALES (tienen defaults)
PORT=5000
FLASK_ENV=production
```

---

## 🔧 **Deployment Paso a Paso**

### **Opción 1: Render.com** (Recomendado - Más fácil)

#### 1. **Crear nuevo Web Service:**
```
- New → Web Service
- Conectar repositorio Git
- Seleccionar rama: OpenAi_full
```

#### 2. **Configuración:**
```yaml
Name: prensai-ia-api
Environment: Python 3
Region: Oregon (US West)
Branch: OpenAi_full
Build Command: pip install -r requirements-cloud.txt
Start Command: python api_flask.py
```

#### 3. **Variables de entorno:**
```
Key: OPENAI_API_KEY
Value: sk-proj-xxxxxxxxxxxxx
```

#### 4. **Deploy:**
- Click "Create Web Service"
- Esperar 5-10 minutos
- Obtener URL: `https://prensai-ia-api.onrender.com`

---

### **Opción 2: Railway.app**

#### 1. **Crear nuevo proyecto:**
```
- New Project → Deploy from GitHub repo
- Seleccionar repositorio
```

#### 2. **Configuración:**
```
Build Command: pip install -r requirements-cloud.txt
Start Command: python api_flask.py
```

#### 3. **Variables de entorno:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

#### 4. **Deploy:**
- Auto-deploy activado
- URL pública generada automáticamente

---

### **Opción 3: Fly.io** (Requiere Dockerfile)

#### 1. **Crear `Dockerfile`:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

COPY api_flask.py .
COPY O_Utils_GPT.py .
COPY O_Utils_Ollama.py .
COPY Z_Utils.py .

EXPOSE 5000

CMD ["python", "api_flask.py"]
```

#### 2. **Deploy:**
```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
fly deploy
```

---

## ✅ **Verificación Post-Deploy**

### 1. **Health Check:**
```bash
curl https://tu-app.render.com/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "API de Prensai funcionando correctamente"
}
```

### 2. **Activar GPT:**
```bash
curl -X POST https://tu-app.render.com/config/gpt-active \
  -H "X-API-Key: prensai-config-2025" \
  -H "Content-Type: application/json" \
  -d '{"gpt_active": true}'
```

**Respuesta esperada:**
```json
{
  "message": "Configuración actualizada",
  "gpt_active": true
}
```

### 3. **Procesar noticia de prueba:**
```bash
curl -X POST https://tu-app.render.com/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://www.lanacion.com.ar/cultura/"],
    "temas": ["Cultura"]
  }'
```

**Respuesta esperada:**
```json
{
  "resultados": [
    {
      "url": "https://...",
      "TITULO": "...",
      "TIPO PUBLICACION": "Nota",
      "TEMA": "Cultura",
      "VALORACION": "NEUTRA",
      ...
    }
  ],
  "metadata": {...}
}
```

---

## 📊 **Monitoreo y Logs**

### **Ver logs en tiempo real:**

**Render:**
```
Dashboard → Service → Logs
```

**Railway:**
```
Dashboard → Deployment → View Logs
```

**Fly.io:**
```bash
fly logs
```

### **Logs importantes a buscar:**

✅ **Inicio correcto:**
```
🚀 Iniciando API de Prensai IA...
📡 Endpoint principal: POST /procesar-noticias
```

✅ **GPT funcionando:**
```
✅ GPT activado. Todas las solicitudes usarán OpenAI.
```

⚠️ **Ollama no disponible (esperado en cloud):**
```
⚠️ Ollama no disponible (servicio no accesible). Asumiendo NO es entrevista.
```

❌ **Error crítico (revisar):**
```
❌ Error en fallback Ollama tema falló: [ConnectionRefusedError]
```

---

## 🔒 **Seguridad**

### **Proteger endpoints sensibles:**

Los endpoints de configuración están protegidos con token:
```
POST /config/gpt-active     ← Requiere X-API-Key
POST /config/limite-texto   ← Requiere X-API-Key
```

### **Cambiar token por defecto:**

En `api_flask.py` (línea 22-24):
```python
VALID_TOKENS = [
    'tu-token-super-secreto-2025'  # ← Cambiar esto
]
```

---

## 💰 **Costos Estimados**

### **Cloud Hosting:**
- Render Free Tier: **$0/mes** (750 horas)
- Railway Free Tier: **$5 crédito/mes**
- Fly.io Free Tier: **$0/mes** (3 VMs pequeñas)

### **OpenAI API (GPT-3.5-turbo):**
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens
- **Costo por 20 noticias: ~$0.05 USD**

### **Costo total mensual (100 corridas):**
```
Cloud: $0 (free tier)
GPT: $5 USD
────────────────
TOTAL: ~$5 USD/mes
```

---

## 🐛 **Troubleshooting**

### **Problema: "Application failed to start"**
```
Solución: Verificar que requirements-cloud.txt esté completo
```

### **Problema: "OpenAI API key not found"**
```
Solución: Configurar variable de entorno OPENAI_API_KEY
```

### **Problema: "Timeout en requests"**
```
Solución: Aumentar timeout en configuración del servidor
          O usar GPT-4o (más rápido que 3.5-turbo)
```

### **Problema: "Rate limit exceeded"**
```
Solución: Agregar delay entre requests (ya implementado)
          O upgrade a plan pago de OpenAI
```

---

## 🎯 **Mejores Prácticas**

1. ✅ **Siempre activar GPT en cloud:**
   ```bash
   curl -X POST .../config/gpt-active -d '{"gpt_active": true}'
   ```

2. ✅ **Monitorear logs regularmente**
3. ✅ **Configurar alertas de error (si disponible)**
4. ✅ **Hacer backup de configuración**
5. ✅ **Testear después de cada deploy**

---

## 📞 **Soporte**

- **Logs:** `GET /logs` (últimas 100 líneas)
- **Health:** `GET /health` (status del servicio)
- **GitHub Issues:** Para reportar bugs

---

## 🚀 **Quick Deploy (Render)**

```bash
# 1. Pushear a GitHub
git push origin OpenAi_full

# 2. En Render.com:
#    - New Web Service
#    - Connect repository
#    - requirements-cloud.txt
#    - python api_flask.py

# 3. Configurar variable:
#    OPENAI_API_KEY=sk-proj-xxxxx

# 4. Deploy automático
# 5. ¡Listo! 🎉
```

---

**Última actualización:** Octubre 2025
**Versión:** 1.0.0 (Branch: OpenAi_full)

