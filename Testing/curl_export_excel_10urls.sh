#!/bin/bash

echo "🚀 Probando endpoint de exportación a Excel con 10 URLs..."
echo "📊 Endpoint: /procesar-noticias-export-excel"
echo "=" * 60

curl -X POST http://localhost:5000/procesar-noticias-export-excel \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21945409",     
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21814945"
    ],
    "temas": ["BAFICI", "Cultura", "Actividades", "Tango BA", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro": "Gabriela Ricardes",
    "ministerio": "Ministerio de Cultura"
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"