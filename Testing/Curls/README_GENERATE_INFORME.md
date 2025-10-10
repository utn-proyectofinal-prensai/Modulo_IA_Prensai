# 📝 Endpoint `/generate-informe`

## **Descripción**

Endpoint para generar informes profesionales de análisis de medios usando Ollama (modelo `llama3.1:8b`).

Recibe métricas de clipping desde el backend y genera un informe conciso de máximo 500 palabras con análisis de valoraciones, soportes, medios y menciones.

---

## **📋 Request**

### **URL**
```
POST http://localhost:5000/generate-informe
```

### **Headers**
```
Content-Type: application/json
```

### **Body**

```json
{
  "metricas": {
    "temaSeleccionado": "Obras CCGSM",
    "fechaGeneracion": "2025-10-10",
    "periodo": {
      "fechaInicio": "2025-10-01",
      "fechaFin": "2025-10-10"
    },
    "totalNoticias": 65,
    "valoraciones": {
      "positivas": {
        "cantidad": 40,
        "porcentaje": 61.5
      },
      "negativas": {
        "cantidad": 15,
        "porcentaje": 23.1
      },
      "neutras": {
        "cantidad": 10,
        "porcentaje": 15.4
      },
      "esTemaCritico": false
    },
    "soportes": [
      {"nombre": "Grafica", "cantidad": 35, "porcentaje": 53.8},
      {"nombre": "Online", "cantidad": 20, "porcentaje": 30.8},
      {"nombre": "Radio", "cantidad": 10, "porcentaje": 15.4}
    ],
    "medios": [
      {"nombre": "Infobae", "cantidad": 15, "porcentaje": 23.1},
      {"nombre": "La Nacion", "cantidad": 12, "porcentaje": 18.5},
      {"nombre": "Clarin", "cantidad": 10, "porcentaje": 15.4}
    ],
    "menciones": [
      {"nombre": "Gabriela Ricardes", "cantidad": 25, "porcentaje": 38.5},
      {"nombre": "Centro Cultural", "cantidad": 18, "porcentaje": 27.7}
    ]
  },
  "contexto": {
    "voceros": ["GR", "JM"],
    "mediosPrimeraLinea": ["Infobae", "La Nacion"]
  },
  "modelo": "llama3.1:8b"
}
```

### **Campos**

#### **Obligatorios:**
- `metricas` (object): Métricas del clipping
  - `temaSeleccionado` (string): Tema del informe
  - `fechaGeneracion` (string): Fecha de generación
  - `periodo` (object): Período del clipping
    - `fechaInicio` (string): Fecha de inicio
    - `fechaFin` (string): Fecha de fin
  - `totalNoticias` (int): Total de noticias analizadas
  - `valoraciones` (object): Valoraciones de las noticias
    - `positivas` (object): `{cantidad: int, porcentaje: float}`
    - `negativas` (object): `{cantidad: int, porcentaje: float}`
    - `neutras` (object): `{cantidad: int, porcentaje: float}`
    - `esTemaCritico` (bool): Si es tema crítico
  - `soportes` (array): Lista de soportes `[{nombre, cantidad, porcentaje}]`
  - `medios` (array): Lista de medios `[{nombre, cantidad, porcentaje}]`
  - `menciones` (array): Lista de menciones `[{nombre, cantidad, porcentaje}]`

#### **Opcionales:**
- `contexto` (object): Contexto adicional (voceros, medios, eventos, etc.)
- `modelo` (string): Modelo de Ollama a usar (default: `llama3.1:8b`)

---

## **📤 Response**

### **Success (200)**

```json
{
  "success": true,
  "informe": "RESUMEN EJECUTIVO:\n\nEl analisis del clipping de noticias sobre Obras CCGSM revela...",
  "modelo_usado": "llama3.1:8b",
  "metricas_utilizadas": {
    "temaSeleccionado": "Obras CCGSM",
    "totalNoticias": 65,
    ...
  },
  "contexto_utilizado": {
    "voceros": ["GR", "JM"],
    ...
  },
  "metadatos": {
    "total_tokens": 1234,
    "tiempo_generacion": 5.67,
    "fecha_generacion": "2025-10-10 14:30:00"
  }
}
```

### **Error de validación (400)**

```json
{
  "success": false,
  "error": "Campo 'metricas' es obligatorio"
}
```

### **Error del servidor (500)**

```json
{
  "success": false,
  "error": "Ollama no está disponible - verifica que el servicio esté ejecutándose"
}
```

---

## **🧪 Testing**

### **Usando el script de prueba:**

```bash
cd /home/lauti/proyecto_final/Modulo_IA_Prensai/Testing/Curls
./curl_generate_informe.sh
```

### **Usando curl directo:**

```bash
curl -X POST http://localhost:5000/generate-informe \
  -H "Content-Type: application/json" \
  -d '{
    "metricas": {
      "temaSeleccionado": "Test",
      "totalNoticias": 10,
      "valoraciones": {
        "positivas": {"cantidad": 5, "porcentaje": 50},
        "negativas": {"cantidad": 3, "porcentaje": 30},
        "neutras": {"cantidad": 2, "porcentaje": 20},
        "esTemaCritico": false
      },
      "soportes": [],
      "medios": [],
      "menciones": []
    }
  }'
```

---

## **⚙️ Configuración**

### **Modelo por defecto:**
- `llama3.1:8b` (mismo que usamos en todas las funciones de Ollama)

### **Parámetros del modelo:**
- `temperature`: 0.1 (respuestas consistentes)
- `top_p`: 0.9
- `num_predict`: 2000 (máximo de tokens)

### **Timeout:**
- 60 segundos

---

## **📊 Características del informe generado:**

1. ✅ **Máximo 500 palabras**
2. ✅ **Resumen ejecutivo al inicio**
3. ✅ **Datos numéricos exactos** (no inventa datos)
4. ✅ **Análisis de valoraciones, soportes y menciones**
5. ✅ **Hallazgos más importantes destacados**
6. ✅ **Tono profesional y objetivo**
7. ✅ **100% en español** (sin inglés)

---

## **🔧 Troubleshooting**

### **Error: "Ollama no está disponible"**
- Verificar que Ollama esté corriendo: `ollama serve`
- Verificar que el modelo esté descargado: `ollama pull llama3.1:8b`

### **Error: "Timeout esperando respuesta"**
- El informe está tomando más de 60s
- Verificar recursos del servidor (CPU/RAM)
- Considerar reducir el tamaño de las métricas

### **Error: "Campo 'metricas' es obligatorio"**
- Verificar que el body incluya el campo `metricas`
- Verificar que sea un objeto JSON válido

---

## **📝 Logs**

Los logs del endpoint se guardan en:
```
Logs/Procesamiento_Noticias_API.log
```

Buscar por:
```
[Informe]
```

---

## **🚀 Integración con Backend**

Este endpoint está diseñado para ser llamado desde el backend que provee las métricas.

El backend debe:
1. Generar las métricas del clipping
2. Hacer POST a `/generate-informe` con las métricas
3. Recibir el informe generado
4. Almacenar/mostrar el informe

---

## **💡 Notas**

- El endpoint es **público** (no requiere API key por ahora)
- El contexto es **opcional** (puede venir vacío)
- Los caracteres especiales (tildes, ñ) se normalizan a ASCII
- El informe se genera en **tiempo real** (no se cachea)

