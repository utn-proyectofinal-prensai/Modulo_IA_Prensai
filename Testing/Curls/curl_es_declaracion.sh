#!/bin/bash

echo "🚀 Probando endpoint de exportación a Excel con 15 URLs para testing de declaraciones..."
echo "📊 Endpoint: /procesar-noticias-export-excel"
echo "============================================================"

curl -X POST http://localhost:5000/procesar-noticias-export-excel \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22704241",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22787748",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22651539",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22627194",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22583651",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22606260",
    ],
    "temas": ["BAFICI", "Cultura", "Actividades", "Tango BA", "Presentaciones"],
    "menciones": ["Gabriela Ricardes", "Jorge Macri"],
    "ministro_key_words": ["Gabriela Ricardes", "Ministra de Cultura"],
    "ministerios_key_words": ["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
  }'

echo ""
echo "✅ Curl ejecutado. Revisa la respuesta y el archivo Excel generado en Data_Results/"
echo "🎯 Este test incluye 13 URLs para testing exhaustivo de la funcionalidad de declaraciones"
