import requests
import logging
import os
from typing import Optional
import pandas as pd
from dotenv import load_dotenv

# Importar la función de Ollama para fallback
from O_Utils_Ollama import valorar_noticia_con_ollama

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de GPT
GPT_API_URL = "https://api.openai.com/v1/chat/completions"
GPT_MODEL = "gpt-3.5-turbo"  # Puedes cambiar a gpt-4 si tienes acceso

def leer_api_key_desde_env() -> Optional[str]:
    """
    Lee la API key de OpenAI desde el archivo .env
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            logging.info("API key de OpenAI encontrada en .env")
            return api_key
        else:
            logging.warning("Variable OPENAI_API_KEY no encontrada en .env")
            return None
    except Exception as e:
        logging.error(f"Error leyendo .env: {e}")
        return None

def valorar_noticia_con_gpt(texto: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    Valora una noticia usando la API de GPT.
    
    Args:
        texto (str): Texto de la noticia a valorar
        api_key (str, optional): API key de OpenAI. Si no se proporciona, busca en variables de entorno.
    
    Returns:
        str: "NEGATIVO", "NO_NEGATIVO", "OTRO" o None si falla
    """
    # Obtener API key
    if not api_key:
        api_key = leer_api_key_desde_env()
    
    if not api_key:
        logging.warning("No se encontró API key de OpenAI en .env. Usando fallback a Ollama.")
        return None
    
    # Prompt para GPT
    prompt = f"""
    TAREA: Clasificar la siguiente noticia como NEGATIVA o NO NEGATIVA.

    TEXTO DE LA NOTICIA:
    {texto}

    INSTRUCCIONES:
    1. Analiza el contenido de la noticia
    2. Clasifica como:
       - "NEGATIVA" si la noticia es negativa, crítica, problemática, conflictiva
       - "NO_NEGATIVA" si la noticia es positiva, neutral, informativa, constructiva

    CRITERIOS:
    - NEGATIVA: críticas, problemas, conflictos, escándalos, crisis, denuncias
    - NO_NEGATIVA: logros, inauguraciones, eventos, anuncios positivos, información neutral

    Responde ÚNICAMENTE con: NEGATIVA o NO_NEGATIVA
    """
    
    # Preparar request para GPT
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": GPT_MODEL,
        "messages": [
            {"role": "system", "content": "Eres un clasificador de noticias especializado en identificar contenido negativo."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,  # Baja temperatura para respuestas más consistentes
        "max_tokens": 10
    }
    
    try:
        response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['NEGATIVO', 'NEGATIVA']:
                return "NEGATIVA"
            elif content in ['NO_NEGATIVO', 'NO NEGATIVO', 'NO_NEGATIVA', 'POSITIVO', 'POSITIVA', 'NEUTRAL']:
                return "NO_NEGATIVA"
            else:
                # Si no reconoce la respuesta, asumir NO_NEGATIVA (más conservador)
                return "NO_NEGATIVA"
        else:
            logging.error(f"Error en API de GPT: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logging.warning("Timeout en API de GPT. Usando fallback a Ollama.")
        return None
    except requests.exceptions.ConnectionError:
        logging.warning("Error de conexión con API de GPT. Usando fallback a Ollama.")
        return None
    except Exception as e:
        logging.error(f"Error inesperado con API de GPT: {e}")
        return None

def valorar_con_ia(texto: str, api_key: Optional[str] = None, ministro: Optional[str] = None, ministerio: Optional[str] = None, gpt_active: bool = True) -> str:
    """
    Función unificada para valorar noticias con IA.
    Decide internamente si usar GPT o Ollama según configuración y disponibilidad.
    Aplica heurística de menciones del ministro/ministerio.
    
    Args:
        texto (str): Texto de la noticia a valorar
        api_key (str, optional): API key de OpenAI
        ministro (str, optional): Nombre del ministro
        ministerio (str, optional): Nombre del ministerio
        gpt_active (bool): Si True intenta GPT, si False usa solo Ollama
    
    Returns:
        str: "POSITIVA", "NEGATIVA", "NEUTRA", o "REVISAR MANUAL"
    """
    # Obtener valoración base (sin heurística)
    valoracion_base = None
    modelo_usado = None
    
    if gpt_active:
        # Intentar con GPT primero
        valoracion_base = valorar_noticia_con_gpt(texto, api_key)
        if valoracion_base is not None:
            modelo_usado = "GPT"
        else:
            logging.info("GPT falló, usando Ollama")
    
    # Si GPT no está activo o falló, usar Ollama
    if valoracion_base is None:
        # Usar Ollama sin heurística (la función base)
        from O_Utils_Ollama import valorar_noticia_con_ollama_base
        valoracion_base = valorar_noticia_con_ollama_base(texto)
        modelo_usado = "Ollama"
    
    # Determinar resultado final y loggear
    resultado_final = None
    
    if valoracion_base == "NEGATIVA":
        resultado_final = "NEGATIVA"
        logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (sin heurística)")
    elif valoracion_base == "NO_NEGATIVA":
        # Aplicar heurística si se proporciona al menos uno (ministro o ministerio)
        if (ministro or ministerio):
            from Z_Utils import aplicar_heuristica_valoracion
            resultado_final = aplicar_heuristica_valoracion(valoracion_base, texto, ministro, ministerio)
            logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (heurística aplicada)")
        else:
            resultado_final = "NEUTRA"
            logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (sin heurística)")
    else:
        # Fallback conservador
        resultado_final = "NEUTRA"
        logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (fallback)")
    
    return resultado_final 

