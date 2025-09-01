#!/usr/bin/env python3
"""
Test simple para verificar el logging de marcar_o_valorar_con_ia
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Z_Utils import marcar_o_valorar_con_ia
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_funcion(texto):
    """Función de prueba para la IA"""
    return f"PROCESADO: {texto[:10]}..."

def main():
    print("🧪 Test de logging en marcar_o_valorar_con_ia")
    print("=" * 50)
    
    # Test 1: Texto normal
    print("\n📝 Test 1: Texto normal")
    resultado1 = marcar_o_valorar_con_ia(
        "Este es un texto normal de prueba", 
        test_funcion, 
        14900, 
        "https://ejemplo.com/1"
    )
    print(f"Resultado: {resultado1}")
    
    # Test 2: Texto nulo
    print("\n📝 Test 2: Texto nulo")
    resultado2 = marcar_o_valorar_con_ia(
        None, 
        test_funcion, 
        14900, 
        "https://ejemplo.com/2"
    )
    print(f"Resultado: {resultado2}")
    
    # Test 3: Texto muy largo
    print("\n📝 Test 3: Texto muy largo")
    texto_largo = "A" * 15000  # 15,000 caracteres
    resultado3 = marcar_o_valorar_con_ia(
        texto_largo, 
        test_funcion, 
        14900, 
        "https://ejemplo.com/3"
    )
    print(f"Resultado: {resultado3}")
    
    # Test 4: Texto vacío
    print("\n📝 Test 4: Texto vacío")
    resultado4 = marcar_o_valorar_con_ia(
        "", 
        test_funcion, 
        14900, 
        "https://ejemplo.com/4"
    )
    print(f"Resultado: {resultado4}")
    
    print("\n✅ Test completado!")

if __name__ == "__main__":
    main()
