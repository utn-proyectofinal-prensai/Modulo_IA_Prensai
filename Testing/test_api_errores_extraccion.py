#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva lógica de manejo de errores de extracción
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

# Configuración
API_URL = "http://localhost:5000"
API_KEY = "prensai-config-2025"  # API key real

def test_api_errores_extraccion():
    """Prueba la API con URLs que sabemos que fallarán en extracción"""
    
    print("🧪 Probando nueva lógica de manejo de errores de extracción...")
    print("=" * 70)
    
    # URLs de prueba: algunas válidas, otras que fallarán
    urls_test = [
        "https://ejes.com/noticia-inexistente-12345",  # ❌ Servidor caído o no existe
        "https://ejes.com/noticia-inexistente-67890",  # ❌ Servidor caído o no existe
        "https://ejemplo.com/noticia",                  # ❌ No es ejes.com
        "https://ejes.com/noticia-valida-123",         # ✅ Debería funcionar (si existe)
    ]
    
    # Datos de prueba
    payload = {
        "urls": urls_test,
        "temas": ["Política", "Economía", "Sociedad"],
        "menciones": [],
        "ministro_key_words": ["Gabriela Ricardes"],
        "ministerios_key_words": ["Ministerio de Transporte"]
    }
    
    print(f"📤 Enviando {len(urls_test)} URLs a la API...")
    print(f"🔗 URLs: {urls_test}")
    print("-" * 50)
    
    try:
        # Llamada a la API
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(
            f"{API_URL}/procesar-noticias",
            json=payload,
            headers=headers,
            timeout=120  # 2 minutos de timeout
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"⏱️ Tiempo de respuesta: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ RESPUESTA EXITOSA:")
            print(f"📊 Recibidas: {result.get('recibidas', 0)}")
            print(f"✅ Procesadas: {result.get('procesadas', 0)}")
            print(f"❌ Errores: {len(result.get('errores', []))}")
            print(f"⏱️ Tiempo: {result.get('tiempo_procesamiento', 'N/A')}")
            
            print("\n🔍 DETALLE DE ERRORES:")
            for i, error in enumerate(result.get('errores', []), 1):
                print(f"  {i}. {error.get('url', 'N/A')}")
                print(f"     Motivo: {error.get('motivo', 'N/A')}")
                print()
            
            print("\n📋 DATOS PROCESADOS:")
            for i, item in enumerate(result.get('data', []), 1):
                print(f"  {i}. {item.get('TITULO', 'Sin título')}")
                print(f"     Tipo: {item.get('TIPO PUBLICACION', 'N/A')}")
                print(f"     Tema: {item.get('TEMA', 'N/A')}")
                print()
                
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API. ¿Está corriendo?")
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La API tardó demasiado en responder")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_api_errores_extraccion()
