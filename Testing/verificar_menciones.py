#!/usr/bin/env python3
"""
Script para verificar que la nueva funcionalidad de menciones funcione correctamente
Llama directamente a la función de la API sin Flask, simulando datos reales del backend
"""

import sys
import os
import json
import pandas as pd

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la función de la API
from api_flask import procesar_noticias_con_ia

def test_menciones_directo():
    """Test directo de la función procesar_noticias_con_ia con datos reales"""
    
    print("🧪 Test directo de la función procesar_noticias_con_ia")
    print("=" * 60)
    
    # URLs reales que sabemos que funcionan (simulando lo que enviaría el backend)
    urls_prueba = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=18961573",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17867914",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17918357",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17815252",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89819217",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89161318",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89163058",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89129117"
    ]
    
    # Temas reales del archivo (simulando lo que enviaría el backend)
    temas_prueba = [
        "9 de Julio en la Feria de Mataderos",
        "Abasto Barrio Cultural", 
        "Actividades por la Revolución de Mayo",
        "Actividades programadas",
        "BAFICI",
        "Mecenazgo",
        "Temporada 2025",
        "Gestión cultural del GCBA"
    ]
    
    # Menciones hardcodeadas del main (simulando lo que enviaría el backend)
    menciones_prueba = [
        "Ministerio de Cultura",
        "Ministra de Cultura", 
        "Gabriela Ricardes",
        "Jorge Macri"
    ]
    
    print(f"📰 URLs reales: {len(urls_prueba)}")
    print(f"🏷️  Temas reales: {len(temas_prueba)} temas")
    print(f"🔍 Menciones reales: {len(menciones_prueba)} menciones")
    print()
    
    try:
        # Llamar directamente a la función (simulando llamada de la API)
        print("🚀 Ejecutando procesar_noticias_con_ia...")
        resultado = procesar_noticias_con_ia(
            urls=urls_prueba,
            temas=temas_prueba,
            menciones=menciones_prueba,
            ministro="Gabriela Ricardes",
            ministerio="Ministerio de Cultura"
        )
        
        print("✅ Función ejecutada exitosamente")
        print(f"📊 Resultado: {resultado['success']}")
        print(f"📝 Tiempo: {resultado.get('tiempo_procesamiento', 'N/A')}")
        
        if resultado['success']:
            data = resultado['data']
            print(f"📋 Datos generados con {len(data)} registros")
            print(f"🔍 Columnas disponibles: {list(data[0].keys()) if data else []}")
            
            # Verificar campo MENCIONES
            if data and 'MENCIONES' in data[0]:
                print(f"\n✅ Campo 'MENCIONES' encontrado")
                
                # Verificar contenido de las primeras filas
                print(f"\n🔍 Primeras 3 filas del campo MENCIONES:")
                for i, registro in enumerate(data[:3]):
                    menciones = registro.get('MENCIONES', [])
                    print(f"  Fila {i+1}: {menciones} (tipo: {type(menciones)})")
                    print(f"    - Es lista: {isinstance(menciones, list)}")
                    print(f"    - Longitud: {len(menciones) if isinstance(menciones, list) else 'N/A'}")
                
                # Verificar que todas las filas tengan listas
                todas_listas = all(isinstance(reg.get('MENCIONES', []), list) for reg in data)
                print(f"\n✅ Todas las filas tienen listas: {todas_listas}")
                
                # Estadísticas
                print(f"\n📊 Estadísticas del campo MENCIONES:")
                print(f"  - Noticias con menciones: {len([reg for reg in data if len(reg.get('MENCIONES', [])) > 0])}")
                print(f"  - Noticias sin menciones: {len([reg for reg in data if len(reg.get('MENCIONES', [])) == 0])}")
                
                # Contar menciones totales
                todas_menciones = []
                for registro in data:
                    menciones = registro.get('MENCIONES', [])
                    if isinstance(menciones, list):
                        todas_menciones.extend(menciones)
                
                if todas_menciones:
                    from collections import Counter
                    conteo = Counter(todas_menciones)
                    print(f"  - Total de menciones encontradas: {len(todas_menciones)}")
                    print(f"  - Distribución de menciones:")
                    for mencion, count in conteo.most_common():
                        print(f"    * {mencion}: {count}")
                
                # Test de JSON (ya tenemos los datos en formato JSON)
                print(f"\n🧪 Verificando estructura JSON del campo MENCIONES:")
                for i, registro in enumerate(data[:3]):
                    menciones_json = registro.get('MENCIONES', [])
                    print(f"  Registro {i+1}: {menciones_json} (tipo: {type(menciones_json)})")
                    print(f"    - Es lista: {isinstance(menciones_json, list)}")
                    print(f"    - Longitud: {len(menciones_json) if isinstance(menciones_json, list) else 'N/A'}")
                
                # Verificar que todas las filas en JSON tengan listas
                todas_listas_json = all(isinstance(reg.get('MENCIONES', []), list) for reg in data)
                print(f"\n✅ Todas las filas en JSON tienen listas: {todas_listas_json}")
                
                # Mostrar JSON completo de las primeras 5 noticias
                print(f"\n📋 JSON COMPLETO de las primeras 5 noticias:")
                print("=" * 80)
                for i, registro in enumerate(data[:5]):
                    print(f"\n🔍 NOTICIA {i+1}:")
                    print(f"URL: {registro.get('LINK', 'N/A')}")
                    print(f"TÍTULO: {registro.get('TITULO', 'N/A')}")
                    print(f"FECHA: {registro.get('FECHA', 'N/A')}")
                    print(f"TEMA: {registro.get('TEMA', 'N/A')}")
                    print(f"MENCIONES: {registro.get('MENCIONES', [])}")
                    print(f"VALORACIÓN: {registro.get('VALORACION', 'N/A')}")
                    print(f"ALCANCE: {registro.get('ALCANCE', 'N/A')}")
                    print(f"CRISIS: {registro.get('CRISIS', 'N/A')}")
                    print(f"GESTIÓN: {registro.get('GESTION', 'N/A')}")
                    print("-" * 50)
                
            else:
                print(f"❌ Campo 'MENCIONES' NO encontrado")
                if data:
                    campos_menciones = [col for col in data[0].keys() if 'mencion' in col.lower()]
                    if campos_menciones:
                        print(f"🔍 Campos relacionados con menciones encontrados: {campos_menciones}")
        
        else:
            print(f"❌ Error en el procesamiento: {resultado.get('error', 'Error desconocido')}")
            
    except Exception as e:
        print(f"❌ Error al ejecutar la función: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Verificando nueva funcionalidad de menciones (test con datos reales)...")
    test_menciones_directo()
