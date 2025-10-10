#!/bin/bash

# Script para testear el endpoint /generate-informe
# Genera un informe de análisis de medios con Ollama

echo "📝 Testeando endpoint /generate-informe"
echo "======================================="
echo ""

# Datos de métricas de ejemplo
curl -X POST http://localhost:5000/generate-informe \
  -H "Content-Type: application/json" \
  -d '{
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
        {"nombre": "Clarin", "cantidad": 10, "porcentaje": 15.4},
        {"nombre": "Pagina 12", "cantidad": 8, "porcentaje": 12.3},
        {"nombre": "Ambito", "cantidad": 5, "porcentaje": 7.7}
      ],
      "menciones": [
        {"nombre": "Gabriela Ricardes", "cantidad": 25, "porcentaje": 38.5},
        {"nombre": "Centro Cultural", "cantidad": 18, "porcentaje": 27.7},
        {"nombre": "Ministerio", "cantidad": 12, "porcentaje": 18.5}
      ]
    },
    "contexto": {
      "voceros": ["GR", "JM"],
      "mediosPrimeraLinea": ["Infobae", "La Nacion"]
    }
  }'

echo ""
echo ""
echo "✅ Request completado"

