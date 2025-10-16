#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handler para RunPod Serverless - Módulo de IA de Prensai
"""

import runpod
import sys
import os

# Agregar el directorio actual al path para importar nuestros módulos
sys.path.append('/app')

# Importar nuestras utilidades
import Z_Utils as Z
import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import time
from datetime import datetime

def handler(event):
    """
    Handler principal para RunPod Serverless
    
    Args:
        event (dict): Contiene los datos del request
        
    Returns:
        dict: Respuesta en formato JSON
    """
    try:
        print("=" * 50)
        print("🚀 INICIO DE REQUEST")
        print(f"📅 Timestamp: {datetime.now()}")
        print(f"📦 Event completo: {event}")
        print("=" * 50)
        
        # Obtener el input del evento
        input_data = event.get('input', {})
        print(f"📥 Input data: {input_data}")
        
        # Determinar qué endpoint se está llamando
        endpoint = input_data.get('endpoint', '/health')
        print(f"🎯 Endpoint solicitado: {endpoint}")
        
        # Router de endpoints
        print(f"🔄 Procesando endpoint: {endpoint}")
        
        if endpoint == '/health':
            print("✅ Ejecutando health_check")
            result = health_check()
            print(f"📤 Resultado health_check: {result}")
            return result
        elif endpoint == '/procesar-noticias':
            print("✅ Ejecutando procesar_noticias")
            # Importar las funciones correctas de api_flask
            from api_flask import procesar_noticias_con_ia, validar_parametros_noticias
            
            # Obtener datos del request
            data = input_data.get('data', {})
            
            # Validar parámetros
            validacion_ok, error_response, datos_validados = validar_parametros_noticias(data)
            
            if not validacion_ok:
                result = (error_response, 400)
            else:
                # Procesar noticias
                resultado, status_code = procesar_noticias_con_ia(**datos_validados)
                result = (resultado, status_code)
                
            print(f"📤 Resultado procesar_noticias: {result}")
            return result
        elif endpoint == '/procesar-noticias-export-excel':
            print("✅ Ejecutando procesar_noticias_export_excel")
            result = procesar_noticias_export_excel(input_data.get('data', {}))
            print(f"📤 Resultado procesar_noticias_export_excel: {result}")
            return result
        elif endpoint == '/generate-informe':
            print("✅ Ejecutando generate_informe")
            result = generate_informe(input_data.get('data', {}))
            print(f"📤 Resultado generate_informe: {result}")
            return result
        elif endpoint == '/config/estado':
            print("✅ Ejecutando get_config_estado")
            result = get_config_estado()
            print(f"📤 Resultado get_config_estado: {result}")
            return result
        elif endpoint == '/config/gpt-active':
            print("✅ Ejecutando config_gpt_active")
            result = config_gpt_active(input_data.get('data', {}))
            print(f"📤 Resultado config_gpt_active: {result}")
            return result
        elif endpoint == '/config/limite-texto':
            print("✅ Ejecutando config_limite_texto")
            result = config_limite_texto(input_data.get('data', {}))
            print(f"📤 Resultado config_limite_texto: {result}")
            return result
        else:
            print(f"❌ Endpoint no encontrado: {endpoint}")
            error_response = {
                "error": f"Endpoint '{endpoint}' no encontrado",
                "endpoints_disponibles": [
                    "/health",
                    "/procesar-noticias", 
                    "/procesar-noticias-export-excel",
                    "/generate-informe",
                    "/config/estado",
                    "/config/gpt-active",
                    "/config/limite-texto"
                ]
            }
            print(f"📤 Error response: {error_response}")
            return error_response, 404
            
    except Exception as e:
        print("=" * 50)
        print("❌ ERROR EN HANDLER")
        print(f"📅 Timestamp: {datetime.now()}")
        print(f"🚨 Error: {str(e)}")
        print(f"📦 Event que causó el error: {event}")
        print("=" * 50)
        error_response = {
            "error": f"Error interno del servidor: {str(e)}",
            "timestamp": str(datetime.now())
        }
        print(f"📤 Error response: {error_response}")
        return error_response, 500

def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Prensai IA API",
        "version": "1.0.0"
    }

def procesar_noticias(data):
    """Procesar noticias endpoint"""
    try:
        urls = data.get('urls', [])
        activar_gpt = data.get('activar_gpt', False)
        limite_texto = data.get('limite_texto', 14900)
        
        if not urls:
            return {"error": "No se proporcionaron URLs"}, 400
            
        resultado = Z.procesar_noticias(urls, activar_gpt, limite_texto)
        return resultado
        
    except Exception as e:
        return {"error": f"Error procesando noticias: {str(e)}"}, 500

def procesar_noticias_export_excel(data):
    """Procesar noticias y exportar a Excel endpoint"""
    try:
        urls = data.get('urls', [])
        activar_gpt = data.get('activar_gpt', False)
        limite_texto = data.get('limite_texto', 14900)
        
        if not urls:
            return {"error": "No se proporcionaron URLs"}, 400
            
        resultado = Z.procesar_noticias_export_excel(urls, activar_gpt, limite_texto)
        return resultado
        
    except Exception as e:
        return {"error": f"Error procesando noticias para Excel: {str(e)}"}, 500

def generate_informe(data):
    """Generar informe endpoint"""
    try:
        metricas = data.get('metricas', {})
        
        if not metricas:
            return {"error": "No se proporcionaron métricas"}, 400
            
        resultado = Oll.generar_informe_con_ollama(metricas)
        return resultado
        
    except Exception as e:
        return {"error": f"Error generando informe: {str(e)}"}, 500

def get_config_estado():
    """Obtener estado de configuración"""
    return {
        "gpt_active": False,  # Configuración por defecto
        "limite_texto": 14900
    }

def config_gpt_active(data):
    """Configurar GPT activo"""
    # En serverless, la configuración no persiste entre requests
    return {"message": "Configuración actualizada (no persiste en serverless)"}

def config_limite_texto(data):
    """Configurar límite de texto"""
    # En serverless, la configuración no persiste entre requests
    return {"message": "Configuración actualizada (no persiste en serverless)"}

# Iniciar el servidor serverless
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO RUNPOD SERVERLESS HANDLER")
    print(f"📅 Timestamp: {datetime.now()}")
    print("=" * 60)
    print("📡 Endpoints disponibles:")
    print("  - /health")
    print("  - /procesar-noticias")
    print("  - /procesar-noticias-export-excel") 
    print("  - /generate-informe")
    print("  - /config/estado")
    print("  - /config/gpt-active")
    print("  - /config/limite-texto")
    print("=" * 60)
    print("🔧 Iniciando RunPod SDK...")
    
    runpod.serverless.start({'handler': handler})
