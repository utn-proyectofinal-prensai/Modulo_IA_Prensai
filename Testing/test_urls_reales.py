#!/usr/bin/env python3
"""
Script para probar con URLs reales de ejes.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z
import logging

# Configurar logging para ver los mensajes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def test_urls_reales():
    """Prueba con URLs reales de ejes.com"""
    
    print("🧪 Probando con URLs reales de ejes.com...")
    print("=" * 60)
    
    # URLs reales de ejes.com (algunas funcionarán, otras fallarán)
    urls_reales = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595633",  # ✅ Existe
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=99999999",  # ❌ No existe (404)
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595797",  # ✅ Existe
        "https://ejes.com/noticia-que-no-existe-12345",                           # ❌ No existe
    ]
    
    for i, url in enumerate(urls_reales, 1):
        print(f"\n🔗 Probando URL {i}: {url}")
        print("-" * 50)
        
        # Probar extracción de texto
        texto = Z.procesar_link_robusto(url, 'texto', 3)
        if texto:
            print(f"✅ TEXTO extraído: {texto[:100]}...")
        else:
            print(f"❌ TEXTO falló: None")
        
        # Probar extracción de HTML
        html_obj = Z.procesar_link_robusto(url, 'html', 3)
        if html_obj:
            print(f"✅ HTML extraído: Objeto BeautifulSoup válido")
        else:
            print(f"❌ HTML falló: None")
        
        print()

if __name__ == "__main__":
    test_urls_reales()
