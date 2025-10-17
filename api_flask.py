#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask para el módulo de IA de Prensai
Endpoint principal: /procesar-noticias
"""

from flask import Flask, request, jsonify
from functools import wraps
import pandas as pd
import Z_Utils as Z
import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import time
from datetime import timedelta
import logging
import os

app = Flask(__name__)

# Autenticación por token para endpoints de configuración
VALID_TOKENS = [
    'prensai-config-2025'  # Token único para acceso a configuración
]

def require_api_key(f):
    """
    Decorator que verifica si el request tiene un token válido
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener el token del header X-API-Key
        token = request.headers.get('X-API-Key')
        
        # Si no hay token, devolver error 401 (No autorizado)
        if not token:
            return jsonify({
                'error': 'Token requerido',
                'message': 'Debes incluir el header X-API-Key para acceder a la configuración'
            }), 401
        
        # Si el token no es válido, devolver error 401
        if token not in VALID_TOKENS:
            return jsonify({
                'error': 'Token inválido',
                'message': 'El token proporcionado no es válido'
            }), 401
        
        # Si el token es válido, ejecutar la función original
        return f(*args, **kwargs)
    
    return decorated_function

# Los campos ministro_key_words y ministerios_key_words ahora son obligatorios
# Las menciones pueden venir vacías
# Configuración configurable en runtime (se puede modificar via endpoints)
RUNTIME_CONFIG = {
    'gpt_active': False,
    'limite_texto': 14900
}

# Campos fijos del DataFrame
CAMPOS_FIJOS = [
    'TITULO', 'TIPO PUBLICACION', 'FECHA', 'SOPORTE', 'MEDIO','SECCION',
    'AUTOR', 'ENTREVISTADO', 'TEMA', 'LINK', 'HTML_OBJ', 'ALCANCE', 'COTIZACION', 'VALORACION',
    'FACTOR POLITICO','TEXTO_PLANO','MENCIONES'
]

def procesar_noticias_con_ia(
    urls: list,
    temas: list,
    tema_default: str,
    menciones: list = None,
    ministro_key_words: list = None,
    ministerios_key_words: list = None,
) -> dict:
    """
    Función principal que procesa las noticias usando IA
    """
    try:
        # Usar configuración de runtime
        gpt_active = RUNTIME_CONFIG['gpt_active']
        limite_texto = RUNTIME_CONFIG['limite_texto']
        
        # Menciones pueden venir vacías (opcional)
        lista_menciones = menciones if menciones else []
        
        # Medición tiempo de ejecución
        t0 = time.time()
        
        logging.info(f"Procesando {len(urls)} noticias con API")
        
        # Informar qué modelo de IA se usará
        modelo_ia = "GPT-4" if gpt_active else "Ollama (llama3.1:8b)"
        print(f"🤖 Modelo de IA configurado: {modelo_ia}")
        logging.info(f"Modelo de IA configurado: {modelo_ia}")
        print(f"📊 Configuración: GPT_ACTIVE={gpt_active}, LIMITE_TEXTO={limite_texto}")
        logging.info(f"Configuración: GPT_ACTIVE={gpt_active}, LIMITE_TEXTO={limite_texto}")
        
        # 1. VALIDAR URLs antes de procesar
        validacion_urls = Z.validar_urls_ejes(urls)
        urls_validas = validacion_urls['validas']
        urls_no_validas = validacion_urls['no_validas']
        
        if not urls_validas:
            logging.warning("No hay URLs válidas para procesar")
            # Convertir motivos de rechazo al formato de errores
            errores = []
            for url in urls_no_validas:
                motivo = validacion_urls['motivos'].get(url, "Error desconocido")
                errores.append({
                    "url": url,
                    "motivo": motivo
                })
            
            # Retornar con código de error 422 (datos válidos pero no procesables)
            return {
                "recibidas": len(urls),
                "procesadas": 0,
                "data": [],
                "errores": errores,
                "tiempo_procesamiento": "0:00:00"
            }, 422
        
        # 2. Configurar DataFrame solo con URLs válidas
        df = pd.DataFrame(columns=CAMPOS_FIJOS)
        df['LINK'] = urls_validas
        
        # 3. Extraer texto plano para cada link válido (con reintentos)
        logging.info(f"🔄 Iniciando extracción de texto plano para {len(urls_validas)} URLs válidas")
        df['TEXTO_PLANO'] = df['LINK'].apply(lambda x: Z.procesar_link_robusto(x, 'texto', 3))
        
        # 4. Procesar HTML y rellenar campos (con reintentos)
        logging.info(f"🔄 Iniciando extracción de HTML para {len(urls_validas)} URLs válidas")
        df['HTML_OBJ'] = df['LINK'].apply(lambda x: Z.procesar_link_robusto(x, 'html', 3))
        
        # 5. VERIFICAR QUÉ URLs FALLARON EN LA EXTRACCIÓN
        logging.info("🔍 Verificando URLs que fallaron en la extracción...")
        urls_extraccion_fallida = []
        for idx, row in df.iterrows():
            if row['TEXTO_PLANO'] is None or row['HTML_OBJ'] is None:
                motivo = "No se pudo extraer contenido (servidor no disponible o contenido vacío)"
                urls_extraccion_fallida.append({
                    'url': row['LINK'],
                    'motivo': motivo
                })
                logging.warning(f"⚠️ URL falló en extracción: {row['LINK']} - {motivo}")
        
        # 6. FILTRAR SOLO URLs EXITOSAS para continuar procesamiento
        df_exitosas = df[df['TEXTO_PLANO'].notna() & df['HTML_OBJ'].notna()].copy()
        logging.info(f"✅ URLs exitosas en extracción: {len(df_exitosas)} de {len(df)}")
        
        if len(df_exitosas) == 0:
            logging.error("❌ No se pudo extraer contenido de ninguna URL válida")
            # Convertir motivos de rechazo al formato de errores
            errores = []
            for url in urls_no_validas:
                motivo = validacion_urls['motivos'].get(url, "Error desconocido")
                errores.append({
                    "url": url,
                    "motivo": motivo
                })
            # Agregar errores de extracción fallida
            errores.extend(urls_extraccion_fallida)
            
            return {
                "recibidas": len(urls),
                "procesadas": 0,
                "data": [],
                "errores": errores,
                "tiempo_procesamiento": "0:00:00"
            }, 500
        
        # 7. Procesar solo URLs exitosas
        logging.info(f"🔄 Procesando {len(df_exitosas)} URLs exitosas...")
        df_exitosas['TITULO'] = df_exitosas['HTML_OBJ'].apply(Z.get_titulo_from_html_obj)
        df_exitosas['FECHA'] = df_exitosas['HTML_OBJ'].apply(Z.get_fecha_from_html_obj)
        df_exitosas['MEDIO'] = df_exitosas['HTML_OBJ'].apply(Z.get_medio_from_html_obj).apply(Z.normalizar_medio)
        df_exitosas['SOPORTE'] = df_exitosas['HTML_OBJ'].apply(Z.get_soporte_from_html_obj)
        df_exitosas['SECCION'] = df_exitosas['HTML_OBJ'].apply(Z.get_seccion_from_html_obj)
        df_exitosas['COTIZACION'] = df_exitosas['HTML_OBJ'].apply(Z.get_cotizacion_from_html_obj)
        df_exitosas['ALCANCE'] = df_exitosas['HTML_OBJ'].apply(Z.get_alcance_from_html_obj)
        df_exitosas['AUTOR'] = df_exitosas['HTML_OBJ'].apply(Z.get_autor_from_html_obj)
        
        # 8. VERIFICAR CONTENIDO VÁLIDO POST-PROCESAMIENTO HTML
        logging.info("🔍 Verificando contenido válido post-procesamiento HTML...")
        urls_contenido_invalido = []
        
        for row in df_exitosas.iterrows():
            fecha = row[1]['FECHA']
            cotizacion = row[1]['COTIZACION']
            
            # Verificar si AMBAS son null (contenido inválido)
            if fecha is None and cotizacion is None:  # AMBAS son null
                motivo = "Contenido extraído no es una noticia válida (fecha y cotización son null)"
                urls_contenido_invalido.append({
                    'url': row[1]['LINK'],
                    'motivo': motivo
                })
                logging.warning(f"⚠️ Contenido inválido: {row[1]['LINK']} - FECHA: {fecha}, COTIZACION: {cotizacion}")
        
        # 9. FILTRAR SOLO URLs CON CONTENIDO VÁLIDO para IA
        df_contenido_valido = df_exitosas[df_exitosas['LINK'].isin([url for url in df_exitosas['LINK'] if url not in [e['url'] for e in urls_contenido_invalido]])].copy()
        
        logging.info(f"✅ URLs con contenido válido: {len(df_contenido_valido)} de {len(df_exitosas)}")
        
        if len(df_contenido_valido) == 0:
            logging.error("❌ No hay URLs con contenido válido para procesar con IA")
            # Combinar todos los errores
            errores = []
            for url in urls_no_validas:
                motivo = validacion_urls['motivos'].get(url, "Error desconocido")
                errores.append({"url": url, "motivo": motivo})
            errores.extend(urls_extraccion_fallida)
            errores.extend(urls_contenido_invalido)
            
            return {
                "recibidas": len(urls),
                "procesadas": 0,
                "data": [],
                "errores": errores,
                "tiempo_procesamiento": "0:00:00"
            }, 500
        
        # 10. Inferencias con IA (solo URLs con contenido válido)
        logging.info(f"🤖 Iniciando procesamiento con IA para {len(df_contenido_valido)} URLs válidas...")
        
        # Clasificación de tipo de publicación (GPT con fallback a Ollama)
        df_contenido_valido['TIPO PUBLICACION'] = df_contenido_valido.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.clasificar_tipo_publicacion_con_ia(t, ministro_key_words, ministerios_key_words, gpt_active), 
                limite_texto,
                row['LINK']
            ),
            axis=1
        )
        
        # Factor político
        df_contenido_valido['FACTOR POLITICO'] = df_contenido_valido.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.detectar_factor_politico_con_ia(t, gpt_active=gpt_active), 
                limite_texto,
                row['LINK']
            ),
            axis=1
        )
        
        # Valoración
        df_contenido_valido['VALORACION'] = df_contenido_valido.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.valorar_con_ia(t, ministro_key_words=ministro_key_words, ministerios_key_words=ministerios_key_words, gpt_active=gpt_active), 
                limite_texto,
                row['LINK']
            ),
            axis=1
        )
        
        # Clasificación de temas
        df_contenido_valido['TEMA'] = df_contenido_valido.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.clasificar_tema_con_ia(
                    texto=t,
                    lista_temas=temas,
                    tipo_publicacion=row['TIPO PUBLICACION'],
                    gpt_active=gpt_active,
                    tema_default=tema_default
                ), 
                limite_texto,
                row['LINK']
            ), 
            axis=1
        )
        
        # 11. Extraer entrevistado
        df_contenido_valido['ENTREVISTADO'] = df_contenido_valido.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.extraer_entrevistado_con_ia(t, gpt_active=gpt_active) if row['TIPO PUBLICACION'] == 'Entrevista' else None, 
                limite_texto,
                row['LINK']
            ) if row['TIPO PUBLICACION'] == 'Entrevista' else None,
            axis=1
        )
    
        # 12. Detectar menciones solo si se especificaron (solo URLs con contenido válido)
        if menciones:
            df_contenido_valido = Z.buscar_menciones(df_contenido_valido, lista_menciones)
        else:
            # Si no hay menciones, asignar lista vacía
            df_contenido_valido['MENCIONES'] = [[] for _ in range(len(df_contenido_valido))]
        
                
        # 13. Limpiar DataFrame para respuesta
        df_final = df_contenido_valido.drop(columns=['HTML_OBJ'])
        
        # Medición tiempo final
        t1 = time.time()
        tiempo_total = str(timedelta(seconds=int(t1 - t0)))
        
        logging.info(f"Procesamiento completado en {tiempo_total}")
        
        # Convertir a JSON
        resultado_json = df_final.to_dict('records')
        
        # 14. Combinar errores de validación + extracción + contenido inválido
        logging.info("🔍 Preparando respuesta final con errores combinados...")
        errores = []
        
        # Errores de validación previa
        for url in urls_no_validas:
            motivo = validacion_urls['motivos'].get(url, "Error desconocido")
            errores.append({
                "url": url,
                "motivo": motivo
            })
            logging.info(f"❌ Error de validación: {url} - {motivo}")
        
        # Errores de extracción fallida
        for error in urls_extraccion_fallida:
            errores.append(error)
            logging.info(f"❌ Error de extracción: {error['url']} - {error['motivo']}")
        
        # Errores de contenido inválido
        for error in urls_contenido_invalido:
            errores.append(error)
            logging.info(f"❌ Error de contenido: {error['url']} - {error['motivo']}")
        
        logging.info(f"📊 Resumen final: {len(urls)} recibidas, {len(df_final)} procesadas, {len(errores)} errores")
        
        return {
            "recibidas": len(urls),
            "procesadas": len(df_final),
            "data": resultado_json,
            "errores": errores,
            "tiempo_procesamiento": tiempo_total
        }, 200
        
    except Exception as e:
        logging.error(f"Error en procesamiento: {str(e)}")
        # Convertir URLs a formato de errores
        errores = []
        for url in urls:
            errores.append({
                "url": url,
                "motivo": f"Error en procesamiento: {str(e)}"
            })
        
        return {
            "recibidas": len(urls),
            "procesadas": 0,
            "data": [],
            "errores": errores,
            "tiempo_procesamiento": "0:00:00"
        }, 500

def validar_parametros_noticias(data):
    """
    Función reutilizable para validar parámetros de entrada en endpoints de noticias
    Retorna: (success, error_response, datos_validados)
    """
    try:
        # Validar que venga JSON
        if not request.is_json:
            return False, {
                "error": "Content-Type debe ser application/json"
            }, None
        
        # Validar campos obligatorios
        if 'urls' not in data:
            return False, {
                "error": "Campo 'urls' es obligatorio"
            }, None
        
        if 'temas' not in data:
            return False, {
                "error": "Campo 'temas' es obligatorio"
            }, None
        
        urls = data.get('urls', [])
        temas = data.get('temas', [])
        menciones = data.get('menciones', [])
        ministro_key_words = data.get('ministro_key_words', [])
        ministerios_key_words = data.get('ministerios_key_words', [])
        tema_default = data.get('tema_default', '')  # ← NUEVO CAMPO

        
        # Validaciones adicionales
        if not urls:
            return False, {
                "error": "La lista de URLs no puede estar vacía"
            }, None
        
        if not temas:
            return False, {
                "error": "La lista de temas no puede estar vacía"
            }, None
        
        # Validar campos obligatorios
        if not ministro_key_words:
            return False, {
                "error": "Campo 'ministro_key_words' es obligatorio"
            }, None
        
        if not isinstance(ministro_key_words, list):
            return False, {
                "error": "Campo 'ministro_key_words' debe ser una lista"
            }, None
        
        if not ministerios_key_words:
            return False, {
                "error": "Campo 'ministerios_key_words' es obligatorio"
            }, None
        
        if not isinstance(ministerios_key_words, list):
            return False, {
                "error": "Campo 'ministerios_key_words' debe ser una lista"
            }, None
        
        if not tema_default:
            return False, {
                "error": "Campo 'tema_default' es obligatorio"
            }, None
        
        # Si todo está bien, retornar datos validados
        datos_validados = {
            'urls': urls,
            'temas': temas,
            'menciones': menciones if menciones else None,
            'ministro_key_words': ministro_key_words if ministro_key_words else None,
            'ministerios_key_words': ministerios_key_words if ministerios_key_words else None,
            'tema_default': tema_default
        }
        
        return True, None, datos_validados
        
    except Exception as e:
        return False, {
            "error": f"Error en validación: {str(e)}"
        }, None

@app.route('/procesar-noticias', methods=['POST'])
def procesar_noticias():
    """
    Endpoint principal para procesar noticias
    """
    try:
        data = request.get_json()
        
        # Usar función de validación reutilizable
        validacion_ok, error_response, datos_validados = validar_parametros_noticias(data)
        
        if not validacion_ok:
            return jsonify(error_response), 400
        
        # Procesar noticias
        resultado, status_code = procesar_noticias_con_ia(**datos_validados)
        
        # Retornar el resultado con el código de estado correspondiente
        return jsonify(resultado), status_code
            
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de health check
    """
    return jsonify({
        "status": "OK",
        "service": "Prensai IA API",
        "version": "1.0.0"
    }), 200

@app.route('/config/limite-texto', methods=['POST'])
@require_api_key
def configurar_limite_texto():
    """
    Endpoint para configurar el límite de texto
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        nuevo_limite = data.get('limite_texto')
        
        if nuevo_limite is None:
            return jsonify({
                "error": "Campo 'limite_texto' es obligatorio"
            }), 400
        
        if not isinstance(nuevo_limite, int) or nuevo_limite <= 0:
            return jsonify({
                "error": "limite_texto debe ser un número entero positivo"
            }), 400
        
        # Actualizar configuración
        RUNTIME_CONFIG['limite_texto'] = nuevo_limite
        
        return jsonify({
            "message": f"Límite de texto actualizado a {nuevo_limite}",
            "nuevo_limite": nuevo_limite
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/config/gpt-active', methods=['POST'])
@require_api_key
def configurar_gpt_active():
    """
    Endpoint para configurar si GPT está activo
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        nuevo_valor = data.get('gpt_active')
        
        if nuevo_valor is None:
            return jsonify({
                "error": "Campo 'gpt_active' es obligatorio"
            }), 400
        
        if not isinstance(nuevo_valor, bool):
            return jsonify({
                "error": "gpt_active debe ser un valor booleano (true/false)"
            }), 400
        
        # Actualizar configuración
        RUNTIME_CONFIG['gpt_active'] = nuevo_valor
        
        return jsonify({
            "message": f"GPT Active actualizado a {nuevo_valor}",
            "nuevo_valor": nuevo_valor
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/config/estado', methods=['GET'])
@require_api_key
def obtener_estado_config():
    """
    Endpoint para obtener el estado actual de la configuración
    """
    return jsonify({
        "configuracion": RUNTIME_CONFIG
    }), 200

@app.route('/logs', methods=['GET'])
def obtener_logs():
    """
    Obtiene todo el contenido del archivo de logs de la API
    """
    try:
        log_path = 'Logs/Procesamiento_Noticias_API.log'
        
        if not os.path.exists(log_path):
            return jsonify({
                'error': 'Archivo de logs no encontrado'
            }), 404
            
        with open(log_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        return jsonify({
            'archivo': 'Procesamiento_Noticias_API.log',
            'contenido': contenido,
            'lineas': len(contenido.split('\n'))
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error al leer logs: {str(e)}'
        }), 500

@app.route('/procesar-noticias-export-excel', methods=['POST'])
def procesar_noticias_export_excel():
    """
    Endpoint para procesar noticias y exportar directamente a Excel
    """
    try:
        data = request.get_json()
        
        # Usar función de validación reutilizable
        validacion_ok, error_response, datos_validados = validar_parametros_noticias(data)
        
        if not validacion_ok:
            return jsonify(error_response), 400
        
        # Procesar noticias usando la función existente
        resultado, status_code = procesar_noticias_con_ia(**datos_validados)
        
        # Si hay error en el procesamiento, retornar el error
        if status_code != 200:
            return jsonify(resultado), status_code
        
        # Si no hay noticias procesadas, no exportar
        if resultado['procesadas'] == 0:
            return jsonify({
                "message": "No hay noticias para exportar",
                "recibidas": resultado['recibidas'],
                "procesadas": 0,
                "data": resultado['data'],
                "errores": resultado['errores'],
                "tiempo_procesamiento": resultado['tiempo_procesamiento'],
                "archivo_excel": None
            }), 422  # 422 = datos válidos pero no procesables
        
        # Crear DataFrame para exportar
        df_export = pd.DataFrame(resultado['data'])
        
        # Agregar campos adicionales para Excel
        df_export['USR_CREADOR'] = 'SOL'
        df_export['USR_REVISOR'] = 'LUNA'
        df_export['CRISIS'] = 'NO'
        
        # Generar nombre de archivo con modelo de IA (se sobrescribe cada vez)
        modelo_ia = "GPT" if RUNTIME_CONFIG['gpt_active'] else "Ollama"
        nombre_archivo = f"Noticias_Procesadas_{modelo_ia}.xlsx"
        ruta_archivo = f"Data_Results/{nombre_archivo}"
        
        # Crear directorio si no existe
        import os
        os.makedirs("Data_Results", exist_ok=True)
        
        # Exportar a Excel
        df_export.to_excel(ruta_archivo, index=False, engine='openpyxl')
        
        logging.info(f"Archivo Excel exportado: {ruta_archivo}")
        
        return jsonify({
            "message": f"Noticias procesadas y exportadas exitosamente a Excel",
            "recibidas": resultado['recibidas'],
            "procesadas": resultado['procesadas'],
            "data": resultado['data'],
            "errores": resultado['errores'],
            "tiempo_procesamiento": resultado['tiempo_procesamiento'],
            "archivo_excel": nombre_archivo,
            "ruta_completa": ruta_archivo,
            "registros_exportados": len(df_export)
        }), 200
        
    except Exception as e:
        logging.error(f"Error en exportación a Excel: {str(e)}")
        # Convertir URLs a formato de errores
        urls_error = datos_validados['urls'] if 'datos_validados' in locals() else []
        errores = []
        for url in urls_error:
            errores.append({
                "url": url,
                "motivo": f"Error en exportación: {str(e)}"
            })
        
        return jsonify({
            "recibidas": len(urls_error),
            "procesadas": 0,
            "data": [],
            "errores": errores,
            "tiempo_procesamiento": "0:00:00",
            "archivo_excel": None
        }), 500  # 500 = error interno del servidor

@app.route('/generate-informe', methods=['POST'])
def generate_informe():
    """
    Endpoint para generar informes de análisis de medios con Ollama.
    
    Recibe métricas de clipping desde el backend y genera un informe
    profesional usando el modelo llama3.1:8b.
    
    Body esperado:
        {
            "metricas": {
                "temaSeleccionado": str,
                "fechaGeneracion": str,
                "periodo": {"fechaInicio": str, "fechaFin": str},
                "totalNoticias": int,
                "valoraciones": {
                    "positivas": {"cantidad": int, "porcentaje": float},
                    "negativas": {"cantidad": int, "porcentaje": float},
                    "neutras": {"cantidad": int, "porcentaje": float},
                    "esTemaCritico": bool
                },
                "soportes": [...],
                "medios": [...],
                "menciones": [...]
            },
            "contexto": {...},        // opcional
            "modelo": "llama3.1:8b"   // opcional
        }
    
    Returns:
        200: {
            "informe": str,
            "modelo_usado": str,
            "metadatos": {...}
        }
        
        400: {"error": "Mensaje de error de validación"}
        500: {"error": "Mensaje de error"}
    """
    try:
        # Validar que venga JSON
        if not request.is_json:
            logging.warning("[Informe] Request sin JSON")
            return jsonify({
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        
        # Validar campo obligatorio: metricas
        if 'metricas' not in data:
            logging.warning("[Informe] Request sin campo 'metricas'")
            return jsonify({
                "error": "Campo 'metricas' es obligatorio"
            }), 400
        
        metricas = data.get('metricas')
        
        # Validar que metricas sea un diccionario
        if not isinstance(metricas, dict):
            logging.warning("[Informe] Campo 'metricas' no es un diccionario")
            return jsonify({
                "error": "Campo 'metricas' debe ser un objeto JSON"
            }), 400
        
        # Validar que metricas no esté vacío
        if not metricas:
            logging.warning("[Informe] Campo 'metricas' está vacío")
            return jsonify({
                "error": "Campo 'metricas' no puede estar vacío"
            }), 400
        
        # Campos opcionales
        contexto = data.get('contexto', None)
        modelo = data.get('modelo', None)
        
        # Obtener configuración de GPT desde runtime
        gpt_active = RUNTIME_CONFIG['gpt_active']
        
        # Logging de inicio (una línea con info esencial)
        tema = metricas.get('temaSeleccionado', 'N/A')
        total_noticias = metricas.get('totalNoticias', 0)
        modelo_solicitado = modelo if modelo else ("gpt-3.5-turbo" if gpt_active else "llama3.1:8b")
        
        logging.info(f"[Informe] 🚀 Iniciando | Tema: \"{tema}\" | Noticias: {total_noticias} | Modelo: {modelo_solicitado} | GPT: {gpt_active}")
        
        # Llamar a la función unificada de generación de informes
        resultado = Gpt.generar_informe_con_ia(
            metricas=metricas,
            contexto=contexto,
            modelo=modelo,
            gpt_active=gpt_active
        )
        
        # Verificar si hay error
        if 'error' in resultado:
            # Error en la generación
            error_msg = resultado.get('error', 'Error desconocido')
            logging.error(f"[Informe] ❌ Error | {error_msg}")
            
            return jsonify(resultado), 500
        else:
            # Logging de finalización (una línea con métricas)
            tokens = resultado.get('metadatos', {}).get('total_tokens', 0)
            tiempo = resultado.get('metadatos', {}).get('tiempo_generacion', 0)
            
            logging.info(f"[Informe] ✅ Completado | Tokens: {tokens} | Tiempo: {tiempo:.1f}s")
            
            return jsonify(resultado), 200
            
    except Exception as e:
        error_msg = f"Error interno del servidor: {str(e)}"
        logging.error(f"[Informe] {error_msg}")
        
        return jsonify({
            "error": error_msg
        }), 500

if __name__ == '__main__':
    # Configurar logger al inicio de la API para todos los endpoints
    Z.setup_logger('Procesamiento_Noticias_API.log')
    
    # Puerto: usar variable de entorno PORT (para cloud) o 5000 (para local)
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Iniciando API de Prensai IA...")
    print("📡 Endpoint principal: POST /procesar-noticias")
    print("📊 Exportar a Excel: POST /procesar-noticias-export-excel")
    print("📝 Generar informe: POST /generate-informe")
    print("🏥 Health check: GET /health")
    print("⚙️  Configuración: POST /config/limite-texto, POST /config/gpt-active")
    print("📋 Consultar logs: GET /logs")
    print("📊 Estado config: GET /config/estado")
    print(f"🔧 Puerto: {port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)
