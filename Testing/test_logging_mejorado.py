#!/usr/bin/env python3
"""
Script de prueba para verificar el logging mejorado de procesar_link_robusto
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

def test_logging_mejorado():
    """Prueba el logging mejorado con URLs que sabemos que fallan"""
    
    print("🧪 Probando logging mejorado de procesar_link_robusto...")
    print("=" * 60)
    
    # URL que sabemos que falla (servidor inexistente)
    url_falla = "https://servidor-inexistente-12345.com/test"
    
    print(f"🔗 Probando URL que falla: {url_falla}")
    print("-" * 40)
    
    # Probar con tipo 'texto'
    resultado = Z.procesar_link_robusto(url_falla, tipo='texto', max_reintentos=3)
    
    print(f"\n📊 Resultado: {resultado}")
    print("=" * 60)
    
    # URL que podría fallar por timeout (servidor muy lento)
    url_timeout = "https://httpstat.us/200?sleep=15000"  # 15 segundos de delay
    
    print(f"🔗 Probando URL con timeout: {url_timeout}")
    print("-" * 40)
    
    # Probar con tipo 'html'
    resultado = Z.procesar_link_robusto(url_timeout, tipo='html', max_reintentos=2)
    
    print(f"\n📊 Resultado: {resultado}")
    print("=" * 60)

if __name__ == "__main__":
    test_logging_mejorado()
