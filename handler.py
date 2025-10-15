#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handler para RunPod/Curno - Módulo de IA de Prensai
Formato específico para serverless functions
"""

import json
import asyncio
import sys
import os

# =============================================================================
# DEBUG INFO - DIAGNÓSTICO DEL PROBLEMA
# =============================================================================
print("=== 🔍 DEBUG INFO ===")
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Files in /app:", os.listdir('/app'))
print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'No definido'))
print("========================")

# Verificar importaciones críticas
try:
    import pandas as pd
    print("✅ pandas importado exitosamente")
    print("   pandas location:", pd.__file__)
    print("   pandas version:", pd.__version__)
except ImportError as e:
    print("❌ Error importando pandas:", e)

try:
    import requests
    print("✅ requests importado exitosamente")
    print("   requests version:", requests.__version__)
except ImportError as e:
    print("❌ Error importando requests:", e)

try:
    import numpy as np
    print("✅ numpy importado exitosamente")
    print("   numpy version:", np.__version__)
except ImportError as e:
    print("❌ Error importando numpy:", e)

try:
    import ollama
    print("✅ ollama importado exitosamente")
    print("   ollama version:", ollama.__version__)
except ImportError as e:
    print("❌ Error importando ollama:", e)

print("========================")

# Agregar el directorio actual al path para importar nuestros módulos
sys.path.append('/app')

# Importar nuestras utilidades
try:
    import Z_Utils as Z
    print("✅ Z_Utils importado exitosamente")
except ImportError as e:
    print("❌ Error importando Z_Utils:", e)
    sys.exit(1)

try:
    import O_Utils_Ollama as Oll
    print("✅ O_Utils_Ollama importado exitosamente")
except ImportError as e:
    print("❌ Error importando O_Utils_Ollama:", e)
    sys.exit(1)

try:
    import O_Utils_GPT as Gpt
    print("✅ O_Utils_GPT importado exitosamente")
except ImportError as e:
    print("❌ Error importando O_Utils_GPT:", e)
    sys.exit(1)

import time
from datetime import datetime

print("=== ✅ TODAS LAS IMPORTACIONES EXITOSAS ===")
print("🚀 Handler listo para procesar requests")
print("==========================================")

# Configuración por defecto
DEFAULT_CONFIG = {
    'gpt_active': False,
    'limite_texto': 14900
}

def handler(event):
    """
    Handler principal para RunPod/Curno
    
    Args:
        event: Diccionario con los datos del request
        
    Returns:
        dict: Respuesta en formato JSON
    """
    try:
        print(f"🚀 Recibido request: {event}")
        
        # Obtener el input del evento
        input_data = event.get('input', {})
        
        # Determinar qué endpoint se está llamando
        endpoint = input_data.get('endpoint', '/health')
        
        # Router de endpoints
        if endpoint == '/health':
            return health_check()
        elif endpoint == '/procesar-noticias':
            return procesar_noticias(input_data.get('data', {}))
        elif endpoint == '/procesar-noticias-export-excel':
            return procesar_noticias_export_excel(input_data.get('data', {}))
        elif endpoint == '/generate-informe':
            return generate_informe(input_data.get('data', {}))
        elif endpoint == '/config/estado':
            return get_config_estado()
        elif endpoint == '/config/gpt-active':
            return config_gpt_active(input_data.get('data', {}))
        elif endpoint == '/config/limite-texto':
            return config_limite_texto(input_data.get('data', {}))
        else:
            return {
                'error': f'Endpoint no encontrado: {endpoint}',
                'endpoints_disponibles': [
                    '/health',
                    '/procesar-noticias',
                    '/procesar-noticias-export-excel',
                    '/generate-informe',
                    '/config/estado',
                    '/config/gpt-active',
                    '/config/limite-texto'
                ]
            }
            
    except Exception as e:
        print(f"❌ Error en handler: {str(e)}")
        return {
            'error': f'Error interno del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def health_check():
    """
    Health check endpoint
    """
    try:
        # Verificar Ollama
        ollama_status = "✅ OK"
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code != 200:
                ollama_status = "❌ Error"
        except:
            ollama_status = "❌ No disponible"
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'ollama': ollama_status,
                'gpu': 'NVIDIA RTX 4000 Ada Generation' if os.system('nvidia-smi > /dev/null 2>&1') == 0 else 'No disponible'
            },
            'endpoints': [
                '/health',
                '/procesar-noticias',
                '/procesar-noticias-export-excel',
                '/generate-informe',
                '/config/estado',
                '/config/gpt-active',
                '/config/limite-texto'
            ]
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def procesar_noticias(data):
    """
    Procesar noticias individuales
    """
    try:
        # Validar datos requeridos
        required_fields = ['urls', 'temas', 'ministro_key_words', 'ministerios_key_words']
        for field in required_fields:
            if field not in data:
                return {
                    'error': f'Campo requerido faltante: {field}',
                    'required_fields': required_fields
                }
        
        # Obtener configuración
        config = DEFAULT_CONFIG.copy()
        config.update(data.get('config', {}))
        
        # Procesar cada URL
        resultados = []
        for url in data['urls']:
            try:
                print(f"📰 Procesando: {url}")
                
                # Extraer texto
                texto = Z.extraer_texto_de_url(url)
                if not texto:
                    resultados.append({
                        'url': url,
                        'error': 'No se pudo extraer texto',
                        'texto_extraido': ''
                    })
                    continue
                
                # Truncar texto si es necesario
                if len(texto) > config['limite_texto']:
                    texto = texto[:config['limite_texto']] + "..."
                
                # Determinar qué modelo usar
                if config['gpt_active']:
                    print("🤖 Usando GPT-4...")
                    resultado = Gpt.procesar_con_gpt(
                        texto=texto,
                        temas=data['temas'],
                        menciones=data.get('menciones', []),
                        ministro_key_words=data['ministro_key_words'],
                        ministerios_key_words=data['ministerios_key_words']
                    )
                    modelo_usado = "GPT-4"
                else:
                    print("🦙 Usando Ollama...")
                    resultado = Oll.procesar_con_ollama(
                        texto=texto,
                        temas=data['temas'],
                        menciones=data.get('menciones', []),
                        ministro_key_words=data['ministro_key_words'],
                        ministerios_key_words=data['ministerios_key_words']
                    )
                    modelo_usado = "Ollama (llama3.1:8b)"
                
                # Agregar metadatos
                resultado.update({
                    'url': url,
                    'texto_extraido': texto[:500] + "..." if len(texto) > 500 else texto,
                    'modelo_usado': modelo_usado,
                    'timestamp': datetime.now().isoformat()
                })
                
                resultados.append(resultado)
                
            except Exception as e:
                print(f"❌ Error procesando {url}: {str(e)}")
                resultados.append({
                    'url': url,
                    'error': str(e),
                    'texto_extraido': ''
                })
        
        return {
            'success': True,
            'resultados': resultados,
            'total_procesadas': len(resultados),
            'configuracion': config,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en procesar_noticias: {str(e)}")
        return {
            'error': f'Error procesando noticias: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def procesar_noticias_export_excel(data):
    """
    Procesar noticias y exportar a Excel
    """
    try:
        # Procesar noticias primero
        resultado = procesar_noticias(data)
        
        if 'error' in resultado:
            return resultado
        
        # Convertir a DataFrame
        import pandas as pd
        
        df_data = []
        for item in resultado['resultados']:
            if 'error' not in item:
                df_data.append({
                    'URL': item.get('url', ''),
                    'Tipo': item.get('tipo_publicacion', ''),
                    'Temas': ', '.join(item.get('temas_detectados', [])),
                    'Valoración': item.get('valoracion', ''),
                    'Menciones': ', '.join(item.get('menciones_detectadas', [])),
                    'Ministerio': item.get('ministerio_detectado', ''),
                    'Texto': item.get('texto_extraido', ''),
                    'Modelo': item.get('modelo_usado', ''),
                    'Timestamp': item.get('timestamp', '')
                })
        
        if df_data:
            df = pd.DataFrame(df_data)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prensai_resultados_{timestamp}.xlsx"
            
            # Guardar Excel
            excel_path = f"/app/{filename}"
            df.to_excel(excel_path, index=False)
            
            return {
                'success': True,
                'resultados': resultado['resultados'],
                'excel_generado': filename,
                'total_procesadas': len(resultado['resultados']),
                'configuracion': resultado['configuracion'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'error': 'No se generaron resultados válidos',
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Error en procesar_noticias_export_excel: {str(e)}")
        return {
            'error': f'Error generando Excel: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def generate_informe(data):
    """
    Generar informe de análisis
    """
    try:
        # Validar datos
        if 'metricas' not in data:
            return {
                'error': 'Campo requerido faltante: metricas',
                'timestamp': datetime.now().isoformat()
            }
        
        metricas = data['metricas']
        
        # Generar informe con Ollama
        informe = Oll.generar_informe_completo(
            metricas=metricas,
            contexto=data.get('contexto', {}),
            modelo=data.get('modelo', 'llama3.1:8b')
        )
        
        return {
            'success': True,
            'informe': informe,
            'modelo_usado': data.get('modelo', 'llama3.1:8b'),
            'metadatos': {
                'tema': metricas.get('temaSeleccionado', 'N/A'),
                'total_noticias': metricas.get('totalNoticias', 0),
                'fecha_generacion': datetime.now().isoformat()
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en generate_informe: {str(e)}")
        return {
            'error': f'Error generando informe: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def get_config_estado():
    """
    Obtener estado de configuración
    """
    try:
        return {
            'success': True,
            'configuracion': DEFAULT_CONFIG,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': f'Error obteniendo configuración: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def config_gpt_active(data):
    """
    Configurar si GPT está activo
    """
    try:
        # Validar datos
        if 'gpt_active' not in data:
            return {
                'error': 'Campo requerido faltante: gpt_active',
                'timestamp': datetime.now().isoformat()
            }
        
        # Actualizar configuración
        nuevo_valor = bool(data['gpt_active'])
        DEFAULT_CONFIG['gpt_active'] = nuevo_valor
        
        return {
            'success': True,
            'message': f'GPT {"activado" if nuevo_valor else "desactivado"} correctamente',
            'configuracion_actualizada': DEFAULT_CONFIG.copy(),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'error': f'Error configurando GPT: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def config_limite_texto(data):
    """
    Configurar límite de texto
    """
    try:
        # Validar datos
        if 'limite_texto' not in data:
            return {
                'error': 'Campo requerido faltante: limite_texto',
                'timestamp': datetime.now().isoformat()
            }
        
        nuevo_limite = int(data['limite_texto'])
        
        # Validar rango
        if nuevo_limite < 1000 or nuevo_limite > 50000:
            return {
                'error': 'Límite de texto debe estar entre 1000 y 50000 caracteres',
                'timestamp': datetime.now().isoformat()
            }
        
        # Actualizar configuración
        DEFAULT_CONFIG['limite_texto'] = nuevo_limite
        
        return {
            'success': True,
            'message': f'Límite de texto actualizado a {nuevo_limite} caracteres',
            'configuracion_actualizada': DEFAULT_CONFIG.copy(),
            'timestamp': datetime.now().isoformat()
        }
        
    except ValueError:
        return {
            'error': 'limite_texto debe ser un número entero',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': f'Error configurando límite de texto: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

# Función principal para RunPod
if __name__ == "__main__":
    # Para testing local
    test_event = {
        'input': {
            'endpoint': '/health'
        }
    }
    
    result = handler(test_event)
    print(json.dumps(result, indent=2, ensure_ascii=False))
