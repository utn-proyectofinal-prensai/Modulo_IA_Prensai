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

app = Flask(__name__)

# Los campos ministro y ministerio ahora son obligatorios
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
    'FACTOR POLITICO','GESTION','TEXTO_PLANO', 'CRISIS', 'MENCIONES'
]

def procesar_noticias_con_ia(
    urls: list,
    temas: list,
    menciones: list = None,
    ministro: str = None,
    ministerio: str = None
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
        
        # 1. Configurar DataFrame
        df = pd.DataFrame(columns=CAMPOS_FIJOS)
        df['LINK'] = urls
        
        # 2. Extraer texto plano para cada link
        df['TEXTO_PLANO'] = df['LINK'].apply(Z.get_texto_plano_from_link)
        
        # 3. Procesar HTML y rellenar campos
        df['HTML_OBJ'] = df['LINK'].apply(Z.get_html_object_from_link)
        df['TITULO'] = df['HTML_OBJ'].apply(Z.get_titulo_from_html_obj)
        df['FECHA'] = df['HTML_OBJ'].apply(Z.get_fecha_from_html_obj)
        df['MEDIO'] = df['HTML_OBJ'].apply(Z.get_medio_from_html_obj).apply(Z.normalizar_medio)
        df['SOPORTE'] = df['HTML_OBJ'].apply(Z.get_soporte_from_html_obj)
        df['SECCION'] = df['HTML_OBJ'].apply(Z.get_seccion_from_html_obj)
        df['COTIZACION'] = df['HTML_OBJ'].apply(Z.get_cotizacion_from_html_obj)
        df['ALCANCE'] = df['HTML_OBJ'].apply(Z.get_alcance_from_html_obj)
        df['AUTOR'] = df['HTML_OBJ'].apply(Z.get_autor_from_html_obj)
        df['GESTION'] = df['HTML_OBJ'].apply(Z.get_gestion_from_html_obj)
        
        # 4. Inferencias con IA
        # Clasificación de tipo de publicación
        df['TIPO PUBLICACION'] = df['TEXTO_PLANO'].apply(
            lambda x: Z.marcar_o_valorar_con_ia(
                x, 
                lambda t: Oll.clasificar_tipo_publicacion_unificado(t, ministro), 
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
                lambda t: Gpt.valorar_con_ia(t, ministro=ministro, ministerio=ministerio, gpt_active=gpt_active), 
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
                    fecha_noticia=row.get('FECHA'),
                    tema_a_fecha={},  # Por ahora vacío, se puede extender después
                    gpt_active=gpt_active
                ), 
                limite_texto
            ), 
            axis=1
        )
        
        # 5. Extraer entrevistado
        df['ENTREVISTADO'] = df.apply(
            lambda row: Oll.extraer_entrevistado_con_ollama(row['TEXTO_PLANO']) 
            if row['TIPO PUBLICACION'] == 'Entrevista' else None, 
            axis=1
        )
        
        # 6. Detectar crisis (sin histórico por ahora)
        df['CRISIS'] = 'NO'  # Simplificado para la API
        
        # 7. Detectar menciones solo si se especificaron
        if menciones:
            df = Z.buscar_menciones(df, lista_menciones)
        else:
            # Si no hay menciones, asignar lista vacía
            df['MENCIONES'] = [[] for _ in range(len(df))]
        
                
        # 9. Limpiar DataFrame para respuesta
        df_final = df.drop(columns=['HTML_OBJ', 'TEXTO_PLANO', 'MENCIONES_EXCEL'])
        
        # Medición tiempo final
        t1 = time.time()
        tiempo_total = str(timedelta(seconds=int(t1 - t0)))
        
        logging.info(f"Procesamiento completado en {tiempo_total}")
        
        # Convertir a JSON
        resultado_json = df_final.to_dict('records')
        
        return {
            "success": True,
            "tiempo_procesamiento": tiempo_total,
            "noticias_procesadas": len(resultado_json),
            "data": resultado_json
        }
        
    except Exception as e:
        logging.error(f"Error en procesamiento: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": []
        }

@app.route('/procesar-noticias', methods=['POST'])
def procesar_noticias():
    """
    Endpoint principal para procesar noticias
    """
    try:
        # Validar que venga JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json"
            }), 400
        
        data = request.get_json()
        
        # Validar campos obligatorios
        if 'urls' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'urls' es obligatorio"
            }), 400
        
        if 'temas' not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'temas' es obligatorio"
            }), 400
        
        urls = data.get('urls', [])
        temas = data.get('temas', [])
        menciones = data.get('menciones', [])
        ministro = data.get('ministro', '')
        ministerio = data.get('ministerio', '')
        
        # Validaciones adicionales
        if not urls:
            return jsonify({
                "success": False,
                "error": "La lista de URLs no puede estar vacía"
            }), 400
        
        if not temas:
            return jsonify({
                "success": False,
                "error": "La lista de temas no puede estar vacía"
            }), 400
        
        # Validar campos obligatorios
        if not ministro:
            return jsonify({
                "success": False,
                "error": "Campo 'ministro' es obligatorio"
            }), 400
        
        if not ministerio:
            return jsonify({
                "success": False,
                "error": "Campo 'ministerio' es obligatorio"
            }), 400
        
        # Procesar noticias
        resultado = procesar_noticias_con_ia(
            urls=urls,
            temas=temas,
            menciones=menciones if menciones else None,
            ministro=ministro if ministro else None,
            ministerio=ministerio if ministerio else None
        )
        
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

if __name__ == '__main__':
    print("🚀 Iniciando API de Prensai IA...")
    print("📡 Endpoint principal: POST /procesar-noticias")
    print("🏥 Health check: GET /health")
    print("⚙️  Configuración: POST /config/limite-texto, POST /config/gpt-active")
    print("📊 Estado config: GET /config/estado")
    print("🔧 Puerto: 5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
