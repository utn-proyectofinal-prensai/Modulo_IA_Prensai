#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask para el módulo de IA de Prensai
Endpoint principal: /procesar-noticias
"""

from flask import Flask, request, jsonify
import pandas as pd
import Z_Utils as Z
import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import time
from datetime import timedelta
import logging
import os

app = Flask(__name__)

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
    menciones: list = None,
    ministro_key_words: list = None,
    ministerios_key_words: list = None
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
        
        # Configurar logger
        Z.setup_logger('Procesamiento_Noticias_API.log')
        
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
            return {
                "success": True,
                "recibidas": len(urls),
                "procesadas": 0,
                "urls_no_procesadas": urls_no_validas,
                "motivos_rechazo": validacion_urls['motivos'],
                "tiempo_procesamiento": "0:00:00",
                "noticias_procesadas": 0,
                "data": []
            }
        
        # 2. Configurar DataFrame solo con URLs válidas
        df = pd.DataFrame(columns=CAMPOS_FIJOS)
        df['LINK'] = urls_validas
        
        # 3. Extraer texto plano para cada link válido (con reintentos)
        df['TEXTO_PLANO'] = df['LINK'].apply(lambda x: Z.procesar_link_robusto(x, 'texto', 3))
        
        # 4. Procesar HTML y rellenar campos (con reintentos)
        df['HTML_OBJ'] = df['LINK'].apply(lambda x: Z.procesar_link_robusto(x, 'html', 3))
        df['TITULO'] = df['HTML_OBJ'].apply(Z.get_titulo_from_html_obj)
        df['FECHA'] = df['HTML_OBJ'].apply(Z.get_fecha_from_html_obj)
        df['MEDIO'] = df['HTML_OBJ'].apply(Z.get_medio_from_html_obj).apply(Z.normalizar_medio)
        df['SOPORTE'] = df['HTML_OBJ'].apply(Z.get_soporte_from_html_obj)
        df['SECCION'] = df['HTML_OBJ'].apply(Z.get_seccion_from_html_obj)
        df['COTIZACION'] = df['HTML_OBJ'].apply(Z.get_cotizacion_from_html_obj)
        df['ALCANCE'] = df['HTML_OBJ'].apply(Z.get_alcance_from_html_obj)
        df['AUTOR'] = df['HTML_OBJ'].apply(Z.get_autor_from_html_obj)
        
        # 5. Inferencias con IA
        # Clasificación de tipo de publicación (GPT con fallback a Ollama)
        df['TIPO PUBLICACION'] = df['TEXTO_PLANO'].apply(
            lambda x: Z.marcar_o_valorar_con_ia(
                x, 
                lambda t: Gpt.clasificar_tipo_publicacion_con_ia(t, ministro_key_words, ministerios_key_words, gpt_active), 
                limite_texto
            )
        )
        
        # Factor político
        df['FACTOR POLITICO'] = df['TEXTO_PLANO'].apply(
            lambda x: Z.marcar_o_valorar_con_ia(
                x, 
                Oll.detectar_factor_politico_con_ollama, 
                limite_texto
            )
        )
        
        # Valoración
        df['VALORACION'] = df['TEXTO_PLANO'].apply(
            lambda x: Z.marcar_o_valorar_con_ia(
                x, 
                lambda t: Gpt.valorar_con_ia(t, ministro_key_words=ministro_key_words, ministerios_key_words=ministerios_key_words, gpt_active=gpt_active), 
                limite_texto
            )
        )
        
        # Clasificación de temas
        df['TEMA'] = df.apply(
            lambda row: Z.marcar_o_valorar_con_ia(
                row['TEXTO_PLANO'], 
                lambda t: Gpt.clasificar_tema_con_ia(
                    texto=t,
                    lista_temas=temas,
                    tipo_publicacion=row['TIPO PUBLICACION'],
                    gpt_active=gpt_active
                ), 
                limite_texto
            ), 
            axis=1
        )
        
        # 6. Extraer entrevistado
        df['ENTREVISTADO'] = df.apply(
            lambda row: Oll.extraer_entrevistado_con_ollama(row['TEXTO_PLANO']) 
            if row['TIPO PUBLICACION'] == 'Entrevista' else None, 
            axis=1
        )
    
        # 8. Detectar menciones solo si se especificaron
        if menciones:
            df = Z.buscar_menciones(df, lista_menciones)
        else:
            # Si no hay menciones, asignar lista vacía
            df['MENCIONES'] = [[] for _ in range(len(df))]
        
                
        # 9. Limpiar DataFrame para respuesta
        df_final = df.drop(columns=['HTML_OBJ', 'TEXTO_PLANO'])
        
        # Medición tiempo final
        t1 = time.time()
        tiempo_total = str(timedelta(seconds=int(t1 - t0)))
        
        logging.info(f"Procesamiento completado en {tiempo_total}")
        
        # Convertir a JSON
        resultado_json = df_final.to_dict('records')
        
        #TODO avisar al back como viene esta respuesta.
        return {
            "success": True,
            "recibidas": len(urls),
            "procesadas": len(urls_validas),
            "urls_no_procesadas": urls_no_validas,
            "motivos_rechazo": validacion_urls['motivos'],
            "tiempo_procesamiento": tiempo_total,
            "noticias_procesadas": len(resultado_json),
            "data": resultado_json
        }
        
    except Exception as e:
        logging.error(f"Error en procesamiento: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "recibidas": len(urls),
            "procesadas": 0,
            "urls_no_procesadas": urls,
            "motivos_rechazo": {url: f"Error en procesamiento: {str(e)}" for url in urls},
            "data": []
        }

def validar_parametros_noticias(data):
    """
    Función reutilizable para validar parámetros de entrada en endpoints de noticias
    Retorna: (success, error_response, datos_validados)
    """
    try:
        # Validar que venga JSON
        if not request.is_json:
            return False, {
                "success": False,
                "error": "Content-Type debe ser application/json"
            }, None
        
        # Validar campos obligatorios
        if 'urls' not in data:
            return False, {
                "success": False,
                "error": "Campo 'urls' es obligatorio"
            }, None
        
        if 'temas' not in data:
            return False, {
                "success": False,
                "error": "Campo 'temas' es obligatorio"
            }, None
        
        urls = data.get('urls', [])
        temas = data.get('temas', [])
        menciones = data.get('menciones', [])
        ministro_key_words = data.get('ministro_key_words', [])
        ministerios_key_words = data.get('ministerios_key_words', [])
        
        # Validaciones adicionales
        if not urls:
            return False, {
                "success": False,
                "error": "La lista de URLs no puede estar vacía"
            }, None
        
        if not temas:
            return False, {
                "success": False,
                "error": "La lista de temas no puede estar vacía"
            }, None
        
        # Validar campos obligatorios
        if not ministro_key_words:
            return False, {
                "success": False,
                "error": "Campo 'ministro_key_words' es obligatorio"
            }, None
        
        if not isinstance(ministro_key_words, list):
            return False, {
                "success": False,
                "error": "Campo 'ministro_key_words' debe ser una lista"
            }, None
        
        if not ministerios_key_words:
            return False, {
                "success": False,
                "error": "Campo 'ministerios_key_words' es obligatorio"
            }, None
        
        if not isinstance(ministerios_key_words, list):
            return False, {
                "success": False,
                "error": "Campo 'ministerios_key_words' debe ser una lista"
            }, None
        
        # Si todo está bien, retornar datos validados
        datos_validados = {
            'urls': urls,
            'temas': temas,
            'menciones': menciones if menciones else None,
            'ministro_key_words': ministro_key_words if ministro_key_words else None,
            'ministerios_key_words': ministerios_key_words if ministerios_key_words else None
        }
        
        return True, None, datos_validados
        
    except Exception as e:
        return False, {
            "success": False,
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
        resultado = procesar_noticias_con_ia(**datos_validados)
        
        if resultado["success"]:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
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
def configurar_limite_texto():
    """
    Endpoint para configurar el límite de texto
    """
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        nuevo_limite = data.get('limite_texto')
        
        if nuevo_limite is None:
            return jsonify({
                "success": False,
                "error": "Campo 'limite_texto' es obligatorio"
            }), 400
        
        if not isinstance(nuevo_limite, int) or nuevo_limite <= 0:
            return jsonify({
                "success": False,
                "error": "limite_texto debe ser un número entero positivo"
            }), 400
        
        # Actualizar configuración
        RUNTIME_CONFIG['limite_texto'] = nuevo_limite
        
        return jsonify({
            "success": True,
            "message": f"Límite de texto actualizado a {nuevo_limite}",
            "nuevo_limite": nuevo_limite
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/config/gpt-active', methods=['POST'])
def configurar_gpt_active():
    """
    Endpoint para configurar si GPT está activo
    """
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        nuevo_valor = data.get('gpt_active')
        
        if nuevo_valor is None:
            return jsonify({
                "success": False,
                "error": "Campo 'gpt_active' es obligatorio"
            }), 400
        
        if not isinstance(nuevo_valor, bool):
            return jsonify({
                "success": False,
                "error": "gpt_active debe ser un valor booleano (true/false)"
            }), 400
        
        # Actualizar configuración
        RUNTIME_CONFIG['gpt_active'] = nuevo_valor
        
        return jsonify({
            "success": True,
            "message": f"GPT Active actualizado a {nuevo_valor}",
            "nuevo_valor": nuevo_valor
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/config/estado', methods=['GET'])
def obtener_estado_config():
    """
    Endpoint para obtener el estado actual de la configuración
    """
    return jsonify({
        "success": True,
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
                'success': False,
                'error': 'Archivo de logs no encontrado'
            }), 404
            
        with open(log_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        return jsonify({
            'success': True,
            'archivo': 'Procesamiento_Noticias_API.log',
            'contenido': contenido,
            'lineas': len(contenido.split('\n'))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
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
        resultado = procesar_noticias_con_ia(**datos_validados)
        
        if not resultado['success']:
            return jsonify(resultado), 500
        
        # Si no hay noticias procesadas, no exportar
        if resultado['procesadas'] == 0:
            return jsonify({
                "success": True,
                "message": "No hay noticias para exportar",
                "recibidas": resultado['recibidas'],
                "procesadas": 0,
                "urls_no_procesadas": resultado['urls_no_procesadas'],
                "motivos_rechazo": resultado['motivos_rechazo'],
                "tiempo_procesamiento": resultado['tiempo_procesamiento'],
                "archivo_excel": None
            }), 200
        
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
            "success": True,
            "message": f"Noticias procesadas y exportadas exitosamente a Excel",
            "recibidas": resultado['recibidas'],
            "procesadas": resultado['procesadas'],
            "urls_no_procesadas": resultado['urls_no_procesadas'],
            "motivos_rechazo": resultado['motivos_rechazo'],
            "tiempo_procesamiento": resultado['tiempo_procesamiento'],
            "noticias_procesadas": resultado['noticias_procesadas'],
            "archivo_excel": nombre_archivo,
            "ruta_completa": ruta_archivo,
            "registros_exportados": len(df_export)
        }), 200
        
    except Exception as e:
        logging.error(f"Error en exportación a Excel: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}",
            "recibidas": len(datos_validados['urls']) if 'datos_validados' in locals() else 0,
            "procesadas": 0,
            "urls_no_procesadas": datos_validados['urls'] if 'datos_validados' in locals() else [],
            "motivos_rechazo": {url: f"Error en exportación: {str(e)}" for url in (datos_validados['urls'] if 'datos_validados' in locals() else [])},
            "archivo_excel": None
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando API de Prensai IA...")
    print("📡 Endpoint principal: POST /procesar-noticias")
    print("📊 Exportar a Excel: POST /procesar-noticias-export-excel")
    print("🏥 Health check: GET /health")
    print("⚙️  Configuración: POST /config/limite-texto, POST /config/gpt-active")
    print("📋 Consultar logs: GET /logs")
    print("📊 Estado config: GET /config/estado")
    print("🔧 Puerto: 5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
