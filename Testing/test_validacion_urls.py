#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para la validación de URLs de ejes.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z

def test_validacion_urls():
    """
    Prueba la función de validación de URLs con diferentes casos
    """
    print("🧪 Probando validación de URLs...")
    
    # Casos de prueba
    urls_prueba = [
        # URLs válidas
        "https://www.ejes.com/noticia1",
        "http://ejes.com/noticia2",
        "https://subdominio.ejes.com/noticia3",
        "https://www.ejes.com/noticia4?param=valor",
        
        # URLs no válidas
        "https://otro-sitio.com/noticia",
        "https://malformada.com",
        "no-es-url",
        "",
        None,
        "https://ejes.org/noticia",  # dominio diferente
        "ftp://ejes.com/noticia",    # protocolo incorrecto
        123,  # no es string
        ["no", "es", "url"]  # no es string
    ]
    
    print(f"📋 URLs de prueba ({len(urls_prueba)}):")
    for i, url in enumerate(urls_prueba):
        print(f"  {i+1:2d}. {url}")
    
    print("\n🔍 Ejecutando validación...")
    
    # Ejecutar validación
    resultado = Z.validar_urls_ejes(urls_prueba)
    
    # Mostrar resultados
    print(f"\n✅ URLs válidas ({len(resultado['validas'])}):")
    for url in resultado['validas']:
        print(f"  • {url}")
    
    print(f"\n❌ URLs no válidas ({len(resultado['no_validas'])}):")
    for url in resultado['no_validas']:
        motivo = resultado['motivos'].get(url, "Motivo no especificado")
        print(f"  • {url} - {motivo}")
    
    print(f"\n📊 Estadísticas:")
    stats = resultado['estadisticas']
    print(f"  • Total recibidas: {stats['total']}")
    print(f"  • Válidas: {stats['validas']}")
    print(f"  • No válidas: {stats['no_validas']}")
    print(f"  • Porcentaje válidas: {(stats['validas']/stats['total']*100):.1f}%")
    
    # Verificar que la función funcione correctamente
    urls_esperadas_validas = [
        "https://www.ejes.com/noticia1",
        "http://ejes.com/noticia2", 
        "https://subdominio.ejes.com/noticia3",
        "https://www.ejes.com/noticia4?param=valor"
    ]
    
    urls_esperadas_no_validas = [
        "https://otro-sitio.com/noticia",
        "https://malformada.com",
        "no-es-url",
        "",
        None,
        "https://ejes.org/noticia",
        "ftp://ejes.com/noticia",
        123,
        ["no", "es", "url"]
    ]
    
    # Verificar que las URLs válidas coincidan
    urls_validas_correctas = set(resultado['validas']) == set(urls_esperadas_validas)
    print(f"\n🔍 Verificación:")
    print(f"  • URLs válidas correctas: {'✅' if urls_validas_correctas else '❌'}")
    
    if not urls_validas_correctas:
        print(f"    - Esperadas: {urls_esperadas_validas}")
        print(f"    - Obtenidas: {resultado['validas']}")
    
    print(f"\n🎯 Test completado!")
    return resultado

if __name__ == "__main__":
    test_validacion_urls()
