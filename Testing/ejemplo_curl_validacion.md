# Ejemplos de CURL para probar la API con validación de URLs

## 🚀 Iniciar la API
```bash
cd /home/lauti/proyecto_final/Modulo_IA_Prensai
source venv/bin/activate
python api_flask.py
```

## 📡 Ejemplos de requests con URLs REALES

### 1. URLs mixtas (válidas y no válidas)
```bash
curl -X POST http://localhost:5000/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24313595",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423181",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301580",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301733",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301275",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24361465",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24340866",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24326655",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24192610",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24172624",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24187599",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24189134",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196084",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196152",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22838274",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20420667",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20402381",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20271878",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19799678",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19674630",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=18961573",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17867914",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17918357",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17815252",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89819217",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89161318",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89163058",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89129117"
    ],
    "temas": ["Actividades", "Mecenazgo", "¡URGENTE", "Bares Notables", "Tango BA", "\"Arte es Todo\"", "Presentaciones", "Pase Cultural", "BAFICI", "Jubilaciones", "Elecciones", "Rechazo de", "Movilizacion", "Programa"],
    "menciones": ["Gabriela Ricardes", "Jorge Telerman"],
    "ministro": "Gabriela Ricardes",
    "ministerio": "Ministerio de Cultura"
  }'
```

### 2. Solo URLs válidas (ejes.com)
```bash
curl -X POST http://localhost:5000/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24313595",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
      "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423181"
    ],
    "temas": ["BAFICI", "Cultura"],
    "menciones": ["Gabriela Ricardes"],
    "ministro": "Gabriela Ricardes",
    "ministerio": "Ministerio de Cultura"
  }'
```

### 3. Solo URLs no válidas (ejes.cor)
```bash
curl -X POST http://localhost:5000/procesar-noticias \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://culturagcba.clientes.ejes.cor",
      "https://culturagcba.clientes.ejes.cor",
      "https://culturagcba.clientes.ejes.cor"
    ],
    "temas": ["BAFICI"],
    "menciones": [],
    "ministro": "Gabriela Ricardes",
    "ministerio": "Ministerio de Cultura"
  }'
```

## 📊 Respuesta esperada

### Caso exitoso con URLs mixtas (29 URLs):
```json
{
  "success": true,
  "recibidas": 29,
  "procesadas": 29,
  "urls_no_procesadas": [],
  "motivos_rechazo": {},
  "tiempo_procesamiento": "0:00:XX",
  "noticias_procesadas": 29,
  "data": [
    {
      "TITULO": "Título de la noticia procesada",
      "LINK": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24313595",
      "TEMA": "BAFICI",
      "MENCIONES": ["Gabriela Ricardes"],
      // ... otros campos
    }
    // ... 28 noticias más
  ]
}
```

### Caso sin URLs válidas (solo ejes.cor):
```json
{
  "success": true,
  "recibidas": 3,
  "procesadas": 0,
  "urls_no_procesadas": [
    "https://culturagcba.clientes.ejes.cor",
    "https://culturagcba.clientes.ejes.cor",
    "https://culturagcba.clientes.ejes.cor"
  ],
  "motivos_rechazo": {
    "https://culturagcba.clientes.ejes.cor": "URL no pertenece a ejes.com",
    "https://culturagcba.clientes.ejes.cor": "URL no pertenece a ejes.com",
    "https://culturagcba.clientes.ejes.cor": "URL no pertenece a ejes.com"
  },
  "tiempo_procesamiento": "0:00:00",
  "noticias_procesadas": 0,
  "data": []
}
```

## 🔍 Campos de respuesta

- **`recibidas`**: Total de URLs enviadas por el backend
- **`procesadas`**: URLs que pasaron validación y fueron procesadas
- **`urls_no_procesadas`**: Lista de URLs rechazadas
- **`motivos_rechazo`**: Diccionario con el motivo de rechazo de cada URL
- **`data`**: Array con las noticias procesadas (solo URLs válidas)

## ✅ Validaciones implementadas

1. **Dominio**: Solo URLs que contengan `ejes.com`
2. **Protocolo**: Solo `http://` o `https://`
3. **Formato**: Solo strings válidos
4. **Vacías**: Rechaza URLs vacías o `None`

## 🎯 **Nota importante sobre los URLs de prueba:**

- **29 URLs con `ejes.com`**: Serán **PROCESADAS** (dominio correcto)
- **0 URLs con `ejes.cor`**: No hay URLs inválidas en este caso
- **Resultado esperado**: `recibidas: 29, procesadas: 29, urls_no_procesadas: 0`
