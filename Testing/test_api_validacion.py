#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para la API con validación de URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import api_flask
import json

def test_api_validacion():
    """
    Prueba la API con URLs mixtas para verificar la validación
    """
    print("🧪 Probando API con validación de URLs...")
    
    # URLs de prueba (mixtas: válidas y no válidas)
    urls_prueba = [
        # URLs válidas de ejes.com
        "https://www.ejes.com/noticia1",
        "http://ejes.com/noticia2",
        
        # URLs no válidas
        "https://otro-sitio.com/noticia",
        "no-es-url",
        "",
        None,
        "https://ejes.org/noticia"
    ]
    
    # Parámetros de prueba
    temas = ["Tema1", "Tema2", "Tema3"]
    menciones = ["Mencion1", "Mencion2"]
    ministro = "Ministro Test"
    ministerio = "Ministerio Test"
    
    print(f"📋 URLs de prueba ({len(urls_prueba)}):")
    for i, url in enumerate(urls_prueba):
        print(f"  {i+1:2d}. {url}")
    
    print(f"\n🔧 Parámetros:")
    print(f"  • Temas: {temas}")
    print(f"  • Menciones: {menciones}")
    print(f"  • Ministro: {ministro}")
    print(f"  • Ministerio: {ministerio}")
    
    print(f"\n🔍 Ejecutando procesamiento...")
    
    # Ejecutar procesamiento (sin levantar el servidor Flask)
    resultado = api_flask.procesar_noticias_con_ia(
        urls=urls_prueba,
        temas=temas,
        menciones=menciones,
        ministro=ministro,
        ministerio=ministerio
    )
    
    # Mostrar resultados
    print(f"\n📊 Resultado de la API:")
    print(f"  • Success: {resultado['success']}")
    print(f"  • Recibidas: {resultado['recibidas']}")
    print(f"  • Procesadas: {resultado['procesadas']}")
    print(f"  • URLs no procesadas: {len(resultado['urls_no_procesadas'])}")
    
    if 'motivos_rechazo' in resultado:
        print(f"\n❌ Motivos de rechazo:")
        for url, motivo in resultado['motivos_rechazo'].items():
            print(f"  • {url} - {motivo}")
    
    if 'tiempo_procesamiento' in resultado:
        print(f"  • Tiempo: {resultado['tiempo_procesamiento']}")
    
    if 'noticias_procesadas' in resultado:
        print(f"  • Noticias procesadas: {resultado['noticias_procesadas']}")
    
    # Mostrar estructura de respuesta
    print(f"\n🔍 Estructura de respuesta:")
    print(f"  • Campos disponibles: {list(resultado.keys())}")
    
    # Verificar que la respuesta tenga el formato esperado
    campos_esperados = [
        'success', 'recibidas', 'procesadas', 'urls_no_procesadas', 
        'motivos_rechazo', 'tiempo_procesamiento', 'noticias_procesadas', 'data'
    ]
    
    campos_faltantes = [campo for campo in campos_esperados if campo not in resultado]
    campos_extra = [campo for campo in resultado.keys() if campo not in campos_esperados]
    
    print(f"\n✅ Validación de estructura:")
    print(f"  • Campos faltantes: {campos_faltantes if campos_faltantes else 'Ninguno'}")
    print(f"  • Campos extra: {campos_extra if campos_extra else 'Ninguno'}")
    
    # Verificar que las estadísticas sean consistentes
    if resultado['success']:
        recibidas = resultado['recibidas']
        procesadas = resultado['procesadas']
        no_procesadas = len(resultado['urls_no_procesadas'])
        
        print(f"\n🔢 Verificación de estadísticas:")
        print(f"  • Recibidas: {recibidas}")
        print(f"  • Procesadas: {procesadas}")
        print(f"  • No procesadas: {no_procesadas}")
        print(f"  • Total: {procesadas + no_procesadas}")
        print(f"  • Consistente: {'✅' if (procesadas + no_procesadas) == recibidas else '❌'}")
    
    print(f"\n🎯 Test completado!")
    return resultado

if __name__ == "__main__":
    test_api_validacion()
