#!/usr/bin/env python3
"""
Script específico para analizar una URL 'caída' que técnicamente responde con HTML
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z
import logging
from bs4 import BeautifulSoup

# Configurar logging para ver los mensajes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def analizar_url_caida():
    """Analiza específicamente la URL caída para entender cómo la interpreta el sistema"""
    
    print("🧪 Analizando URL 'caída' específica...")
    print("=" * 70)
    
    # La URL específica que quieres analizar
    url_caida = "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=14632596"
    
    print(f"🔗 URL a analizar: {url_caida}")
    print("-" * 50)
    
    # PASO 1: Probar con procesar_link_robusto (tipo='texto')
    print("📝 PASO 1: Probando extracción de TEXTO PLANO...")
    print("-" * 30)
    
    texto_plano = Z.procesar_link_robusto(url_caida, 'texto', 3)
    
    if texto_plano:
        print(f"✅ TEXTO extraído exitosamente:")
        print(f"📏 Longitud: {len(texto_plano)} caracteres")
        print(f"📄 Contenido: {texto_plano}")
        print()
    else:
        print("❌ TEXTO falló: None")
        print()
    
    # PASO 2: Probar con procesar_link_robusto (tipo='html')
    print("🌐 PASO 2: Probando extracción de HTML...")
    print("-" * 30)
    
    html_obj = Z.procesar_link_robusto(url_caida, 'html', 3)
    
    if html_obj:
        print(f"✅ HTML extraído exitosamente:")
        print(f"📏 Longitud del HTML: {len(str(html_obj))} caracteres")
        
        # Analizar el contenido del HTML
        print(f"🏷️ Título de la página: {html_obj.title.string if html_obj.title else 'No encontrado'}")
        
        # Buscar el mensaje de error específico
        error_msg = html_obj.find(text=lambda text: text and "no se encuentra" in text.lower())
        if error_msg:
            print(f"⚠️ Mensaje de error detectado: {error_msg.strip()}")
        
        # Mostrar las primeras líneas del HTML
        html_text = html_obj.get_text(separator=' ', strip=True)
        print(f"📄 Texto extraído del HTML: {html_text[:200]}...")
        print()
        
    else:
        print("❌ HTML falló: None")
        print()
    
    # PASO 3: Análisis manual directo con requests
    print("🔍 PASO 3: Análisis manual directo...")
    print("-" * 30)
    
    try:
        import requests
        response = requests.get(url_caida, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📏 Tamaño de respuesta: {len(response.content)} bytes")
        print(f"🔤 Encoding: {response.encoding}")
        
        if response.status_code == 200:
            print("✅ Servidor respondió exitosamente")
            
            # Parsear manualmente
            soup_manual = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar elementos específicos
            titulo_manual = soup_manual.find('title')
            if titulo_manual:
                print(f"🏷️ Título manual: {titulo_manual.string}")
            
            # Buscar el mensaje de error
            error_manual = soup_manual.find(text=lambda text: text and "no se encuentra" in text.lower())
            if error_manual:
                print(f"⚠️ Error manual: {error_manual.strip()}")
            
            # Mostrar estructura del HTML
            print(f"🏗️ Estructura HTML: {len(soup_manual.find_all())} elementos encontrados")
            
        else:
            print(f"❌ Servidor respondió con error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en análisis manual: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 ANÁLISIS COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    analizar_url_caida()
