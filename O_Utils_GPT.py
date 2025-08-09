import requests
import logging
import os
from typing import Optional, Dict, List
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


# =============================================================================
# CLASIFICACIÓN DE TEMAS (GPT con fallback a Ollama)
# =============================================================================

def _construir_contexto_temporal_no_restrictivo(lista_temas: List[str], tema_a_fecha: Optional[Dict[str, str]], fecha_noticia: Optional[str], k: int = 7) -> str:
    """
    Genera un bloque de 'contexto temporal' NO RESTRICTIVO con los k temas más cercanos
    a la fecha de la noticia. Devuelve un string listo para insertar en el prompt.
    """
    if not tema_a_fecha or not fecha_noticia:
        return "(sin datos temporales relevantes)"
    try:
        from datetime import datetime
        noticia_dt = datetime.fromisoformat(str(fecha_noticia))
        def distancia_dias(tema: str) -> int:
            try:
                f = tema_a_fecha.get(tema)
                if not f:
                    return 999999
                dt = datetime.fromisoformat(str(f))
                return abs((dt - noticia_dt).days)
            except Exception:
                return 999999
        ordenados = sorted(lista_temas, key=distancia_dias)
        top = [t for t in ordenados if tema_a_fecha.get(t)][:k]
        if not top:
            return "(sin datos temporales relevantes)"
        lineas = [f"- {t} (fecha_carga: {tema_a_fecha[t]})" for t in top]
        return "\n".join(lineas)
    except Exception:
        return "(sin datos temporales relevantes)"


def clasificar_tema_con_gpt(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    fecha_noticia: Optional[str] = None,
    tema_a_fecha: Optional[Dict[str, str]] = None,
    gpt_active: bool = True,
) -> str:
    """
    Clasifica un tema usando GPT como primera opción y fallback a Ollama.

    - Debe devolver EXACTAMENTE uno de lista_temas
    - Si tipo_publicacion == 'Agenda' → 'Actividades programadas'
    - Usa 'contexto temporal' como desempate NO restrictivo
    """
    try:
        if not texto or not lista_temas:
            return "Revisar Manual"

        # Regla simple por tipo de publicación
        if tipo_publicacion == "Agenda":
            return "Actividades programadas"

        if gpt_active:
            api_key = leer_api_key_desde_env()
            if api_key:
                temas_str = "\n".join([f"- {t}" for t in lista_temas])
                contexto_str = _construir_contexto_temporal_no_restrictivo(
                    lista_temas, tema_a_fecha, fecha_noticia, k=7
                )

                # PROMPT reforzado
                system_msg = (
                    "Sos un clasificador ESTRICTO. Debés asignar EXACTAMENTE 1 tema "
                    "de una lista cerrada. No inventes nombres ni sinónimos. "
                    "La salida debe ser SOLO el nombre del tema (sin comillas, sin puntos, sin texto extra)."
                )
                user_msg = (
                    f"Asigná UNO y solo UNO de los siguientes temas a la noticia (lista cerrada):\n{temas_str}\n\n"
                    "REGLAS (aplicarlas en este orden):\n"
                    "0) Normalización: considerá TÍTULO y CUERPO en minúsculas y sin acentos/diacríticos.\n"
                    "1) Coincidencia literal inequívoca (en TÍTULO o CUERPO) → elegí ese tema.\n"
                    "2) Si hay varias coincidencias literales:\n"
                    "   2.1) Prioridad al que aparezca en el TÍTULO.\n"
                    "   2.2) Si persiste el empate, elegí el MÁS ESPECÍFICO (string más largo).\n"
                    "   2.3) Si persiste, elegí el que aparezca MÁS VECES en el texto.\n"
                    "3) Sin coincidencia literal: permití paráfrasis SOLO si es claramente el mismo evento/proyecto (sin ambigüedad).\n"
                    "   3.1) Si hay más de una opción por paráfrasis, aplicá 2.1 → 2.3.\n"
                    "4) Contexto temporal (NO restrictivo, solo como desempate final): si quedás entre 2-3 opciones plausibles y ninguna es clara, "
                    "preferí un tema del bloque siguiente por recencia:\n"
                    f"{contexto_str}\n"
                    "5) Umbral de confianza: si no hay evidencia clara (ni literal ni paráfrasis inequívoca), elegí exactamente: Actividades programadas.\n"
                    "6) Prohibido: múltiples temas, explicaciones, texto adicional o un tema fuera de la lista.\n\n"
                    f"TEXTO:\n{texto}\n\n"
                    "RESPUESTA (solo el nombre exacto del tema):"
                )

                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {
                    "model": GPT_MODEL,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 16,
                }

                try:
                    response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=20)
                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"].strip()

                        # Saneo mínimo de salida (quitar comillas/puntos sueltos)
                        content = content.strip().strip('"').strip("'").rstrip(".").strip()

                        # Validación estricta
                        if content in lista_temas:
                            return content

                        # Intento de match por casefold (sin alterar la decisión final)
                        mapeo_lower = {t.casefold(): t for t in lista_temas}
                        if content.casefold() in mapeo_lower:
                            return mapeo_lower[content.casefold()]

                        # Si no es válido → fallback a Ollama
                    else:
                        logging.warning(f"GPT tema status {response.status_code}: {response.text}")
                except Exception as e:
                    logging.warning(f"GPT tema error: {e}")

        # Fallback a Ollama (misma lógica que el proyecto usa hoy)
        try:
            from O_Utils_Ollama import matchear_tema_con_fallback
            return matchear_tema_con_fallback(
                texto,
                lista_temas,
                tipo_publicacion,
                fecha_noticia=fecha_noticia,
                tema_a_fecha=tema_a_fecha,
            )
        except Exception as e:
            logging.error(f"Fallback Ollama tema falló: {e}")
            return "Actividades programadas"

    except Exception as e:
        logging.error(f"Error inesperado en clasificar_tema_con_gpt: {e}")
        return "Actividades programadas"


def clasificar_tema_con_ia(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    fecha_noticia: Optional[str] = None,
    tema_a_fecha: Optional[Dict[str, str]] = None,
    gpt_active: bool = True,
) -> str:
    """
    Interfaz unificada similar a valorar_con_ia:
    - Si gpt_active y hay API key → intenta GPT (clasificar_tema_con_gpt)
    - Si falla o está desactivado → fallback a Ollama (matchear_tema_con_fallback)
    """
    try:
        if not texto or not lista_temas:
            return "Revisar Manual"

        if gpt_active:
            resultado = clasificar_tema_con_gpt(
                texto=texto,
                lista_temas=lista_temas,
                tipo_publicacion=tipo_publicacion,
                fecha_noticia=fecha_noticia,
                tema_a_fecha=tema_a_fecha,
                gpt_active=True,
            )
            if resultado:
                return resultado

        # Fallback a Ollama
        from O_Utils_Ollama import matchear_tema_con_fallback
        return matchear_tema_con_fallback(
            texto,
            lista_temas,
            tipo_publicacion,
            fecha_noticia=fecha_noticia,
            tema_a_fecha=tema_a_fecha,
        )
    except Exception as e:
        logging.error(f"clasificar_tema_con_ia error: {e}")
        return "Actividades programadas"
