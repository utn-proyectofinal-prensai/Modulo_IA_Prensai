import requests
import logging
import os
import time
from typing import Optional, Dict, List
import pandas as pd
from dotenv import load_dotenv

# Importar la función de Ollama para fallback
from O_Utils_Ollama import valorar_noticia_con_ollama

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de GPT
GPT_API_URL = "https://api.openai.com/v1/chat/completions"
GPT_MODEL = "gpt-3.5-turbo" # Modelo por defecto, en funciones especiales cambia a 4o 

def switch_4o(gpt_active: bool) -> str:
    """
    Función auxiliar para decidir qué modelo GPT usar internamente.
    Solo se aplica cuando gpt_active=True, sino se ignora el valor.
    """
    if not gpt_active:
        return "gpt-3.5-turbo"  # Valor por defecto, se ignora si va a Ollama
    return "gpt-4.1-mini"  # Modelo premium para funciones críticas


def _obtener_display_id(url_id):
    """
    Obtiene una versión compacta del identificador de la noticia para logging.
    Si la URL contiene 'id=', devuelve solo ese valor; en caso contrario,
    retorna el identificador original.
    """
    if not url_id:
        return url_id
    if isinstance(url_id, str) and "id=" in url_id:
        try:
            return url_id.split("id=")[-1]
        except Exception:
            return url_id
    return url_id

def _gpt_request_with_retry(headers: Dict, data: Dict, max_retries: int = 3, timeout: int = 15):
    """
    Función auxiliar para hacer requests a GPT con retry automático.
    
    Args:
        headers (Dict): Headers para la request
        data (Dict): Data para la request
        max_retries (int): Número máximo de reintentos
        timeout (int): Timeout en segundos para cada request
    
    Returns:
        requests.Response: Response exitosa o None si falló definitivamente
    """
    for intento in range(max_retries):
        try:
            response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=timeout)
            
            # Si la request fue exitosa, devolver la respuesta
            if response.status_code == 200:
                return response
            
            # RETRY: Solo para códigos específicos que indican problemas temporales
            if response.status_code in [429, 500, 502, 503, 504]:
                if intento < max_retries - 1:
                    delay = (2 ** intento) * 2  # 2s, 4s, 8s
                    logging.warning(f"GPT error {response.status_code}, reintento {intento + 1} en {delay}s...")
                    time.sleep(delay)
                    continue
                else:
                    logging.error(f"GPT error {response.status_code} después de {max_retries} intentos")
                    return None
            
            # Si no es retryable, no reintentar
            logging.warning(f"GPT error {response.status_code} no es retryable: {response.text}")
            return None
            
        except (requests.Timeout, requests.ConnectionError) as e:
            # RETRY: Solo para errores de red/conexión
            if intento < max_retries - 1:
                delay = (2 ** intento) * 2
                logging.warning(f"GPT timeout/conexión, reintento {intento + 1} en {delay}s... Error: {e}")
                time.sleep(delay)
                continue
            else:
                logging.error(f"GPT timeout/conexión después de {max_retries} intentos: {e}")
                return None
                
        except Exception as e:
            # Otros errores no son retryable
            logging.error(f"GPT error inesperado: {e}")
            return None
    
    return None

def leer_api_key_desde_env() -> Optional[str]:
    """
    Lee la API key de OpenAI desde el archivo .env
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key
        else:
            logging.warning("Variable OPENAI_API_KEY no encontrada en .env")
            return None
    except Exception as e:
        logging.error(f"Error leyendo .env: {e}")
        return None

# =============================================================================
# VALORACIÓN  (GPT con fallback a Ollama)
# =============================================================================

def valorar_noticia_con_gpt(texto: str, api_key: Optional[str] = None, url_id: Optional[str] = None) -> Optional[str]:
    """
    Valora una noticia usando la API de GPT.
    
    Args:
        texto (str): Texto de la noticia a valorar
        api_key (str, optional): API key de OpenAI. Si no se proporciona, busca en variables de entorno.
    
    Returns:
        str: "NEGATIVA", "NO_NEGATIVA" o None si falla
    """
    # Obtener API key
    if not api_key:
        api_key = leer_api_key_desde_env()
    
    if not api_key:
        logging.warning("No se encontró API key de OpenAI en .env. Usando fallback a Ollama.")
        logging.warning(f"GPT falló al valorar noticia. Usando fallback a Ollama. (ID: {_obtener_display_id(url_id)})")
        return None
    
    # Prompt para GPT
    prompt = f"""
    TAREA: Clasificar la siguiente noticia como NEGATIVA o NO NEGATIVA.

    TEXTO DE LA NOTICIA:
    {texto}

    INSTRUCCIONES:
    1. Analiza el tono GLOBAL de la noticia, no fragmentos aislados.
       Si el conflicto aparece solo como anécdota, contexto histórico o cita aislada,
       considerá la noticia como NO_NEGATIVA.
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
        "temperature": 0.0,  # Baja temperatura para respuestas más consistentes
        "max_tokens": 10
    }
    
    response = _gpt_request_with_retry(headers, data)
    
    if response:
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
        logging.warning("GPT falló al valorar noticia. Usando fallback a Ollama.")
        return None

def valorar_con_ia(
    texto: str,
    api_key: Optional[str] = None,
    ministro_key_words: Optional[str] = None,
    ministerios_key_words: Optional[str] = None,
    gpt_active: bool = True,
    url_id: str = None
) -> str:
    """
    Función unificada para valorar noticias con IA.
    Decide internamente si usar GPT o Ollama según configuración y disponibilidad.
    Aplica heurística de menciones del ministro/ministerio.
    
    Args:
        texto (str): Texto de la noticia a valorar
        api_key (str, optional): API key de OpenAI
        ministro_key_words (str or list, optional): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
        gpt_active (bool): Si True intenta GPT, si False usa solo Ollama
    
    Returns:
        str: "POSITIVA", "NEGATIVA", "NEUTRA", o "REVISAR MANUAL"
    """
    # Obtener valoración base (sin heurística)
    valoracion_base = None
    modelo_usado = None
    
    display_id = _obtener_display_id(url_id)

    if gpt_active:
        # Intentar con GPT primero
        valoracion_base = valorar_noticia_con_gpt(texto, api_key, url_id=url_id)
        if valoracion_base is not None:
            modelo_usado = f"GPT-{GPT_MODEL}"  # Mostrar modelo específico
        else:
            logging.info(f"GPT falló, usando Ollama (ID: {display_id})")
    
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
        logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (sin heurística) (ID: {display_id})")
    elif valoracion_base == "NO_NEGATIVA":
        # Aplicar heurística si se proporciona al menos uno (ministro_key_words o ministerios_key_words)
        if (ministro_key_words or ministerios_key_words):
            from Z_Utils import aplicar_heuristica_valoracion
            resultado_final = aplicar_heuristica_valoracion(valoracion_base, texto, ministro_key_words, ministerios_key_words)
            logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (heurística aplicada) (ID: {display_id})")
        else:
            resultado_final = "NEUTRA"
            logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (sin heurística) (ID: {display_id})")
    else:
        # Fallback conservador
        resultado_final = "NEUTRA"
        logging.info(f"Valoración: {modelo_usado} → {valoracion_base} → {resultado_final} (fallback) (ID: {display_id})")
    
    return resultado_final
 

# =============================================================================
# CLASIFICACIÓN DE TEMAS (GPT con fallback a Ollama)
# =============================================================================

def clasificar_tema_con_gpt(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    gpt_active: bool = True,
    tema_default: str = None,
    url_id: str = None,
) -> str:
    """
    Clasifica una noticia en un tema específico usando GPT-4o.
    
    Args:
        texto (str): Texto completo de la noticia (título + cuerpo)
        lista_temas (List[str]): Lista de temas disponibles para elegir
        tipo_publicacion (Optional[str]): Tipo de publicación (para reglas especiales)
        gpt_active (bool): Si usar GPT (True) o fallback a Ollama (False)
        tema_default (str): Tema específico para publicaciones de agenda
    
    Returns:
        str: Tema asignado (debe estar en lista_temas)
    """
    try:
        # Validaciones básicas
        if not texto or not lista_temas:
            return tema_default
        
        # Regla especial: si es Agenda, usar tema_default
        display_id = _obtener_display_id(url_id)

        if tipo_publicacion == "Agenda":
            logging.info(f"Tema: GPT -> Heurística (Agenda) asignó tema {tema_default} (ID: {display_id})")
            return tema_default
        
        # Solo proceder si GPT está activo
        if not gpt_active:
            logging.info(f"🔄 GPT desactivado, usando fallback a Ollama... (ID: {display_id})")
            return _fallback_a_ollama_tema(texto, lista_temas, tipo_publicacion, tema_default, url_id=display_id)
        
        # Verificar API key
        api_key = leer_api_key_desde_env()
        if not api_key:
            logging.warning(f"⚠️ No se encontró API key de OpenAI. Usando fallback a Ollama... (ID: {display_id})")
            return _fallback_a_ollama_tema(texto, lista_temas, tipo_publicacion, tema_default, url_id=display_id)
        
        # Usar GPT-4o para clasificación (activando el switch)
        GPT_MODEL = switch_4o(gpt_active)
        
        # Construir lista de temas para el prompt (incluyendo tema_default si no está)
        temas_disponibles = lista_temas.copy()
        if tema_default and tema_default not in temas_disponibles:
            temas_disponibles.append(tema_default)
        
        temas_str = "\n".join([f"- {t}" for t in temas_disponibles])
        logging.debug(f"📋 Temas disponibles: {temas_disponibles}")
        
        # PROMPT REFINADO CON PRIORIDADES CLARAS
        system_msg = (
            "Eres un editor periodístico experto en clasificar noticias por temas. "
            "Tu tarea es asignar el tema MÁS ADECUADO de una lista predefinida, "
            "priorizando temas específicos sobre temas genéricos."
        )
        
        user_msg = (
            f"ANALIZA esta noticia (título + cuerpo completo) y asígnale el tema MÁS ADECUADO de la lista disponible.\n\n"
            f"IMPORTANTE: Solo puedes elegir de esta lista, NO inventes temas:\n{temas_str}\n\n"
            f"CRITERIOS DE EVALUACIÓN (APLICAR EN ESTE ORDEN):\n"
            f"1. PRIORIDAD ALTA: Si el nombre EXACTO de un tema aparece en el título o cuerpo → elegir ese tema\n"
            f"2. PRIORIDAD MEDIA: Si hay palabras clave específicas de un tema (ej: 'BAFICI', 'Juventus Lyrica', 'Abasto') → elegir ese tema\n"
            f"3. PRIORIDAD BAJA: Solo si NO hay evidencia específica clara → elegir un tema genérico como '{tema_default}'\n\n"
            f"REGLAS IMPORTANTES:\n"
            f"- NUNCA ignores un tema específico que está claramente mencionado en el texto\n"
            f"- Los temas genéricos son SOLO para noticias que realmente no encajan con temas específicos\n"
            f"- Si hay dudas entre temas similares, elige el MÁS ESPECÍFICO\n\n"
            f"NOTICIA A ANALIZAR:\n{texto}\n\n"
            f"RESPUESTA: Responde ÚNICAMENTE con el nombre exacto del tema elegido (sin comillas, sin puntos, sin texto adicional)."
        )
        
        # Preparar request para GPT
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            "temperature": 0.0,  # Baja temperatura para respuestas consistentes
            "max_tokens": 30      # Suficiente para el nombre del tema
        }
        
        # Hacer request a GPT con retry
        response = _gpt_request_with_retry(headers, data)
        
        if response and response.status_code == 200:
            try:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Saneo básico de la respuesta
                content = content.strip().strip('"').strip("'").rstrip(".").strip()
                
                # Validar que el tema esté en la lista
                if content in temas_disponibles:
                    modelo_display = GPT_MODEL.replace("gpt-", "GPT-").replace("-turbo", "").replace("-4o", "-4o")
                    logging.info(f"Tema: {modelo_display} -> {content} (ID: {display_id})")
                    return content
                
                # Intento de match por casefold (sin sensibilidad a mayúsculas)
                mapeo_lower = {t.casefold(): t for t in temas_disponibles}
                if content.casefold() in mapeo_lower:
                    tema_correcto = mapeo_lower[content.casefold()]
                    logging.info(f"🔄 Aplicando casefold matching: '{content}' → '{tema_correcto}' (ID: {display_id})")
                    return tema_correcto
                
                # Si no es válido, loggear y usar fallback
                logging.warning(f"⚠️ {GPT_MODEL} devolvió tema inválido: '{content}'. Usando fallback... (ID: {display_id})")
                
            except Exception as e:
                logging.error(f"❌ Error procesando respuesta de {GPT_MODEL}: {e} (ID: {display_id})")
        else:
            logging.warning(f"⚠️ {GPT_MODEL} falló al clasificar tema. Usando fallback... (ID: {display_id})")
        
        # Fallback a Ollama
        logging.info(f"🔄 GPT falló, usando fallback a Ollama... (ID: {display_id})")
        return _fallback_a_ollama_tema(texto, lista_temas, tipo_publicacion, tema_default, url_id=display_id)
        
    except Exception as e:
        logging.error(f"❌ Error inesperado en clasificar_tema_con_gpt: {e} (ID: {display_id})")
        return tema_default


def _fallback_a_ollama_tema(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    tema_default: str = None,
    url_id: str = None
) -> str:
    """
    Función auxiliar para fallback a Ollama cuando GPT falla.
    """
    try:
        from O_Utils_Ollama import clasificar_tema_ollama
        resultado = clasificar_tema_ollama(texto, lista_temas, tema_default, tipo_publicacion, url_id=url_id)
        logging.info(f"Tema: Ollama -> {resultado} (ID: {_obtener_display_id(url_id)})")
        return resultado
    except requests.exceptions.ConnectionError:
        logging.warning(f"⚠️ Ollama no disponible (servicio no accesible). Usando tema por defecto. (ID: {_obtener_display_id(url_id)})")
        return tema_default
    except requests.exceptions.Timeout:
        logging.warning(f"⚠️ Ollama timeout (servicio no responde). Usando tema por defecto. (ID: {_obtener_display_id(url_id)})")
        return tema_default
    except Exception as e:
        logging.error(f"❌ Fallback Ollama tema falló: {e} (ID: {_obtener_display_id(url_id)})")
        return tema_default


def clasificar_tema_con_ia(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    gpt_active: bool = True,
    tema_default: str = None,
    url_id: str = None,
) -> str:
    """
    Interfaz unificada para clasificación de temas:
    - Si gpt_active y hay API key → intenta GPT (clasificar_tema_con_gpt)
    - Si falla o está desactivado → fallback a Ollama (clasificar_tema_ollama)
    """
    try:
        if not texto or not lista_temas:
            return tema_default

        display_id = _obtener_display_id(url_id)

        if gpt_active:
            resultado = clasificar_tema_con_gpt(
                texto=texto,
                lista_temas=lista_temas,
                tipo_publicacion=tipo_publicacion,
                gpt_active=True,
                tema_default=tema_default,
                url_id=url_id,
            )
            if resultado:
                return resultado

        # Fallback a Ollama
        return _fallback_a_ollama_tema(
            texto,
            lista_temas,
            tipo_publicacion=tipo_publicacion,
            tema_default=tema_default,
            url_id=url_id
        )
    except Exception as e:
        logging.error(f"❌ clasificar_tema_con_ia error: {e}")
        return tema_default


# =============================================================================
# TIPO DE PUBLICACION (GPT con fallback a Ollama)
# =============================================================================

def es_entrevista_con_gpt(texto: str, gpt_active: bool = True) -> bool:
    """
    Detecta si es una ENTREVISTA usando GPT: formato pregunta-respuesta entre periodista y entrevistado.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): Si usar GPT-4o (True) o GPT-3.5-turbo (False) para clasificación
    
    Returns:
        bool: True si es entrevista, False si no
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_entrevista(texto)
        
        # Prompt refinado y simplificado para entrevistas
        prompt = f"""
        Eres un experto en clasificar noticias periodísticas. Tu tarea es determinar si un texto es una ENTREVISTA o NO.

        TEXTO DE LA NOTICIA:
        {texto}

        CRITERIOS PARA ENTREVISTA:
        ✅ Formato pregunta-respuesta con guiones (–) seguidos de preguntas o respuestas extensas
        ✅ Intercambio directo entre periodista y entrevistado
        ✅ Preguntas del periodista seguidas de respuestas del entrevistado
        ✅ Patrón repetitivo de guión + contenido conversacional

        NO ES ENTREVISTA:
        ❌ Solo citas entre comillas sin formato pregunta-respuesta
        ❌ Solo declaraciones en primera persona sin intercambio
        ❌ Solo texto narrativo sin estructura conversacional
        ❌ Resúmenes periodísticos de lo que dijo alguien (aunque tengan "en diálogo con...")
        ❌ Fragmentos de declaraciones recopiladas sin intercambio directo
        ❌ Citas con contexto como "Consultado por..." pero sin guiones conversacionales
        ❌ Notas que compilan respuestas a diferentes preguntas sin formato pregunta-respuesta

        IMPORTANTE: 
        - Analiza TODO el texto completo, no solo el inicio
        - Las entrevistas reales tienen formato pregunta-respuesta con guiones (–)
        - Solo citas extensas NO son suficientes para ser entrevista
        - Debe haber intercambio conversacional real, no solo declaraciones

        RESPONDE SOLO: "SI" si es entrevista, "NO" si no lo es.
        """
        
        # Preparar request para GPT con modelo seleccionado por switch_4o
        GPT_MODEL = switch_4o(gpt_active)  # Variable local para esta función
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar la variable local
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en identificar entrevistas periodísticas. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = _gpt_request_with_retry(headers, data)
        
        if response:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                return False
            else:
                # Si GPT devolvió algo inesperado, usar fallback
                logging.warning(f"{GPT_MODEL} devolvió respuesta inesperada: '{content}'. Usando fallback a Ollama.")
                return _fallback_a_ollama_entrevista(texto)
                
        else:
            logging.warning(f"{GPT_MODEL} falló al clasificar entrevista.")
            return _fallback_a_ollama_entrevista(texto)
            
    except Exception as e:
        logging.error(f"Error en es_entrevista_con_gpt: {e}. Usando fallback a Ollama.")
        return _fallback_a_ollama_entrevista(texto)


def _fallback_a_ollama_entrevista(texto: str) -> bool:
    """
    Función de fallback que usa Ollama cuando GPT falla.
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        bool: True si es entrevista, False si no
    """
    try:
        logging.info("🔄 Usando fallback a Ollama para clasificación de entrevistas...")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import es_entrevista_ollama
        
        resultado_ollama = es_entrevista_ollama(texto)
        logging.info(f"✅ Fallback Ollama -> No_Entrevista -> Siguiente: Nota")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). Asumiendo NO es entrevista.")
        return False
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). Asumiendo NO es entrevista.")
        return False
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver False (ante la duda, NO es entrevista)
        logging.warning("⚠️ Devolviendo False por defecto (ante la duda, NO es entrevista)")
        return False


def es_agenda_con_gpt(texto: str, gpt_active: bool = True) -> bool:
    """
    Detecta si es una AGENDA usando GPT: noticia que enumera actividades/eventos culturales.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): Si usar GPT-4o (True) o GPT-3.5-turbo (False) para clasificación
    
    Returns:
        bool: True si es agenda, False si no
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_agenda(texto)
        
        # Prompt para detectar agendas basado en análisis real de ejemplos
        prompt = f"""
        Eres un experto en clasificar noticias periodísticas. Tu tarea es determinar si un texto es una AGENDA o NO.

        TEXTO DE LA NOTICIA:
        {texto}

        ✅ CRITERIOS PARA SER AGENDA (debe cumplir TODOS):
        1. TÍTULO INDICATIVO: Palabras como "Recomendados", "Imperdibles", "Agenda", "Programación", "AGENDATE"
        2. ESTRUCTURA PROGRAMÁTICA: Lista organizada de actividades por día, categoría o cronológicamente
        3. PROPÓSITO: Invitar al lector a asistir a eventos (no solo informar)
        4. INFORMACIÓN PRÁCTICA: Entradas, precios, lugares, inscripciones, cupos
        5. FECHAS: Específicas O relativas (HOY, MAÑANA, DOMINGO, "sábado 15 de junio")
        6. HORARIOS: Específicos O rangos ("a las 20:30 h", "de 18 a 21")

        ❌ EXCLUIR si:
        - Estructura narrativa descriptiva (no programática)
        - Propósito de informar sobre eventos ya realizados o convenios
        - Títulos que describen acciones pasadas o futuras lejanas

        IMPORTANTE:
        - Los títulos como "Recomendados", "Imperdibles", "Agenda" o titulos similares que hagan referencias a una agenda de actividades son indicadores FUERTES de agenda.
        - Todos los criterios de inclusión son obligatorios.
        - Si no cumple absolutamente todos, la respuesta es "NO".
        - Responde solo "SI" o "NO".
        """
        
        # Preparar request para GPT con modelo seleccionado por switch_4o
        GPT_MODEL = switch_4o(gpt_active)  # Variable local para esta función
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar la variable local
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en identificar agendas periodísticas. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = _gpt_request_with_retry(headers, data)
        
        if response:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                return False
            else:
                # Si GPT devolvió algo inesperado, usar fallback
                logging.warning(f"{GPT_MODEL} devolvió respuesta inesperada: '{content}'. Usando fallback a Ollama.")
                return _fallback_a_ollama_agenda(texto)
                
        else:
            logging.warning(f"GPT falló al clasificar agenda.")
            return _fallback_a_ollama_agenda(texto)
            
    except Exception as e:
        logging.error(f"Error en es_agenda_con_gpt: {e}. Usando fallback a Ollama.")
        return _fallback_a_ollama_agenda(texto)


def _fallback_a_ollama_agenda(texto: str) -> bool:
    """
    Función de fallback que usa Ollama cuando GPT falla para agenda.
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        bool: True si es agenda, False si no
    """
    try:
        logging.info("🔄 Usando fallback a Ollama para clasificación de agenda...")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import es_agenda_ollama
        
        resultado_ollama = es_agenda_ollama(texto)
        logging.info(f"✅ Fallback Ollama -> No_Agenda -> Siguiente: Entrevista")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). Asumiendo NO es agenda.")
        return False
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). Asumiendo NO es agenda.")
        return False
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver False (ante la duda, NO es agenda)
        logging.warning("⚠️ Devolviendo False por defecto (ante la duda, NO es agenda)")
        return False


def es_declaracion_con_gpt(texto: str, ministro_key_words, ministerios_key_words=None, gpt_active: bool = True) -> bool:
    """
    Detecta si es una DECLARACIÓN usando GPT: nota con cita textual atribuida al ministro o ministerio.
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
        gpt_active (bool): Si usar GPT-4o (True) o GPT-3.5-turbo (False) para clasificación
    
    Returns:
        bool: True si es declaración, False si no
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_declaracion(texto, ministro_key_words, ministerios_key_words)
        
        # Construir lista combinada de actores (ministros + ministerios)
        actores = []
        
        # Agregar ministros
        if ministro_key_words:
            if isinstance(ministro_key_words, list):
                # Aplanar listas anidadas y filtrar elementos None
                for item in ministro_key_words:
                    if isinstance(item, list):
                        actores.extend([m for m in item if m])
                    else:
                        if item:
                            actores.append(item)
                logging.debug(f"Ministros agregados: {actores}")
            else:
                actores.append(ministro_key_words)
                logging.debug(f"Ministro agregado: {ministro_key_words}")
        
        # Agregar ministerios si existen
        if ministerios_key_words:
            if isinstance(ministerios_key_words, list):
                # Aplanar listas anidadas y filtrar elementos None
                for item in ministerios_key_words:
                    if isinstance(item, list):
                        actores.extend([m for m in item if m])
                    else:
                        if item:
                            actores.append(item)
                logging.debug(f"Ministerios agregados: {actores}")
            else:
                actores.append(ministerios_key_words)
                logging.debug(f"Ministerio agregado: {ministerios_key_words}")
        
        # Verificar que tengamos actores válidos
        if not actores:
            logging.warning("No se encontraron actores válidos para buscar declaraciones")
            return False
        
        logging.debug(f"Array final de actores: {actores}")
        
        # Convertir a string legible
        actores_str = ", ".join(actores)
        
        # Prompt para detectar declaraciones
        prompt = f"""
        Eres un experto en clasificar noticias periodísticas. Tu tarea es determinar si un texto contiene AL MENOS UNA DECLARACIÓN (cita textual) atribuida a alguno de estos actores.

        ACTORES A BUSCAR: {actores_str}

        TEXTO DE LA NOTICIA:
        {texto}

        CRITERIOS FLEXIBLES PARA CONSIDERARLO DECLARACIÓN:
        ✅ DEBE tener AL MENOS UNA CITA entre comillas ("..." o '...') atribuida a alguno de los actores
        ✅ El actor puede ser referenciado de forma directa o indirecta (fuentes, cartera, ministerio, etc.)
        ✅ Debe contener verbos de comunicación/acción (dijo, anunció, informó, explicaron, señaló, etc.)
        ✅ Una noticia puede contener MÚLTIPLES declaraciones de diferentes actores
        ✅ Las citas pueden ser extensas y detalladas
        ✅ Solo importa que esté entre comillas y atribuida a un actor

        EJEMPLOS CLAROS DE DECLARACIÓN:
        - 'Estamos trabajando en el proyecto', dijo Gabriela Ricardes
        - El Ministerio de Cultura anunció: 'Vamos a implementar nuevas políticas'
        - La ministra expresó: 'Es fundamental apoyar la cultura'
        - Desde la cartera cultural se informó que 'se realizarán inversiones'
        - La funcionaria manifestó: 'Es importante preservar el patrimonio'
        - 'Según explicaron fuentes del ministerio: 'la plataforma ya la creamos...''
        - 'La ministra señaló: 'Es una muestra concreta de cómo...''
        - 'Fuentes del área informaron que 'la aplicación funcionará como...''

        EJEMPLOS CLAROS DE NO DECLARACIÓN:
        - La ministra presentó el programa (sin cita textual)
        - Se inauguró el teatro (sin cita ni actor)
        - El programa incluye actividades culturales (sin cita)
        - Se realizó una conferencia (sin cita ni actor)
        - La funcionaria asistió al evento (sin cita)
        - Se anunció la nueva política (sin cita textual)

        IMPORTANTE: 
        - Si hay AL MENOS UNA cita textual atribuida a un actor, es DECLARACIÓN
        - Analiza TODO el texto completo, no solo el inicio
        - Las declaraciones tienen citas textuales entre comillas
        - Debe haber atribución clara a alguno de los actores listados

        RESPONDE SOLO: "SI" si es declaración, "NO" si no lo es.
        """
        
        # Preparar request para GPT con modelo seleccionado por switch_4o
        GPT_MODEL = switch_4o(gpt_active)  # Variable local para esta función
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar la variable local
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en identificar declaraciones periodísticas. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = _gpt_request_with_retry(headers, data)
        
        if response:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                return False
            else:
                # Si GPT devolvió algo inesperado, usar fallback
                logging.warning(f"{GPT_MODEL} devolvió respuesta inesperada: '{content}'. Usando fallback a Ollama.")
                return _fallback_a_ollama_declaracion(texto, ministro_key_words, ministerios_key_words)
                
        else:
            logging.warning(f"{GPT_MODEL} falló al clasificar declaración.")
            return _fallback_a_ollama_declaracion(texto, ministro_key_words, ministerios_key_words)
            
    except Exception as e:
        logging.error(f"Error en es_declaracion_con_gpt: {e}. Usando fallback a Ollama.")
        return _fallback_a_ollama_declaracion(texto, ministro_key_words, ministerios_key_words)


def _fallback_a_ollama_declaracion(texto: str, ministro_key_words, ministerios_key_words=None) -> bool:
    """
    Función de fallback que usa Ollama cuando GPT falla para declaración.
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
    
    Returns:
        bool: True si es declaración, False si no
    """
    try:
        logging.info("🔄 Usando fallback a Ollama para clasificación de declaración...")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import es_declaracion_ollama
        
        # Validar que tengamos parámetros válidos antes de llamar a Ollama
        if not ministro_key_words and not ministerios_key_words:
            logging.warning("No hay actores válidos para buscar declaraciones en fallback")
            return False
        
        resultado_ollama = es_declaracion_ollama(texto, ministro_key_words, ministerios_key_words)
        logging.info(f"✅ Fallback Ollama -> No_Declaración -> Siguiente: Agenda")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). Asumiendo NO es declaración.")
        return False
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). Asumiendo NO es declaración.")
        return False
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver False (ante la duda, NO es declaración)
        logging.warning("⚠️ Devolviendo False por defecto (ante la duda, NO es declaración)")
        return False


def clasificar_tipo_publicacion_con_gpt(texto: str, ministro_key_words: str, ministerios_key_words: str, gpt_active: bool, url_id: str = None) -> str:
    """
    Clasifica el tipo de publicación usando funciones GPT especializadas.
    Procesa secuencialmente: Declaración → Agenda → Entrevista → Nota (por defecto)
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        # Obtener modelo real para logs
        GPT_MODEL = switch_4o(gpt_active)
        modelo_display = GPT_MODEL.replace("gpt-", "GPT-").replace("-turbo", "").replace("-4o", "-4o")
        display_id = _obtener_display_id(url_id)
        
        # 1. DECLARACIÓN (primera prioridad - más específica, evita falsos positivos)
        if es_declaracion_con_gpt(texto, ministro_key_words, ministerios_key_words, gpt_active=True):
            logging.info(f"Tipo Publicación: {modelo_display} -> Declaración (ID: {display_id})")
            time.sleep(1.5)  # Delay para evitar rate limiting
            return "Declaración"
        
        # 2. AGENDA (segunda prioridad - más frecuente, regla clara)
        if es_agenda_con_gpt(texto, gpt_active=True):
            logging.info(f"Tipo Publicación: {modelo_display} -> NO_Declaración -> Agenda (ID: {display_id})")
            time.sleep(1.5)  # Delay para evitar rate limiting
            return "Agenda"
        
        # 3. ENTREVISTA (tercera prioridad - formato distintivo)
        if es_entrevista_con_gpt(texto, gpt_active=True):
            logging.info(f"Tipo Publicación: {modelo_display} -> NO_Declaración -> NO_Agenda -> Entrevista (ID: {display_id})")
            time.sleep(1.5)  # Delay para evitar rate limiting
            return "Entrevista"
        
        # 4. NOTA (por defecto - lo que no cabe claramente en otras categorías)
        logging.info(f"Tipo Publicación: {modelo_display} -> NO_Declaración -> NO_Agenda -> NO_Entrevista -> Nota (ID: {display_id})")
        time.sleep(1.5)  # Delay para evitar rate limiting
        return "Nota"
        
    except Exception as e:
        logging.error(f"❌ Error en clasificar_tipo_publicacion_con_gpt: {e} (ID: {display_id})")
        # En caso de error, devolver "Nota" como fallback seguro
        return "Nota"


def clasificar_tipo_publicacion_con_ia(texto: str, ministro_key_words: str, ministerios_key_words: str = None, gpt_active: bool = False, url_id: str = None) -> str:
    """
    Función unificada para clasificar tipo de publicación con GPT y fallback a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
        gpt_active (bool): Si usar GPT o ir directo a Ollama
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import clasificar_tipo_publicacion_unificado
        
        display_id = _obtener_display_id(url_id)

        if gpt_active:
            resultado_gpt = clasificar_tipo_publicacion_con_gpt(
                texto,
                ministro_key_words,
                ministerios_key_words,
                gpt_active,
                url_id=url_id
            )
            
            # GPT siempre devuelve algo (Agenda, Entrevista, Declaración, o Nota)
            # Solo fallback a Ollama si hay error de API o excepción
            if resultado_gpt is not None:
                return resultado_gpt
            else:
                logging.info(f"GPT falló por error de API, usando fallback a Ollama... (ID: {display_id})")
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló por error)
        resultado_ollama = clasificar_tipo_publicacion_unificado(texto, ministro_key_words, ministerios_key_words)
        logging.info(f"Tipo Publicación: Ollama -> {resultado_ollama} (ID: {display_id})")
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en clasificar_tipo_publicacion_con_ia: {e} (ID: {display_id})")
        # Fallback seguro
        return "Nota"


# =============================================================================
# EXTRACCIÓN DE ENTREVISTADO (GPT con fallback a Ollama)
# =============================================================================

def extraer_entrevistado_con_gpt(texto: str, gpt_active: bool = True, url_id: str = None) -> Optional[str]:
    """
    Extrae el nombre completo del entrevistado usando GPT-3.5-turbo.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): No usado, mantenido por compatibilidad
    
    Returns:
        str: Nombre completo del entrevistado o None si no se identifica
    """
    try:
        api_key = leer_api_key_desde_env()
        display_id = _obtener_display_id(url_id)
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_entrevistado(texto)
        
        # Prompt para extraer entrevistado (igual que Ollama)
        prompt = f"""
        Identificá quién está siendo entrevistado en la siguiente noticia.

        TEXTO DE LA NOTICIA:
        {texto}

        IMPORTANTE:
        - Extraé ÚNICAMENTE el NOMBRE COMPLETO (nombre + apellido)
        - NO agregues explicaciones, títulos, cargos ni texto adicional
        - Si no hay entrevistado claro, respondé 'No identificado'
        - Si hay múltiples entrevistados, elegí el principal

        NOMBRE COMPLETO DEL ENTREVISTADO:
        """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar modelo por defecto (gpt-3.5-turbo)
            "messages": [
                {"role": "system", "content": "Eres un extractor especializado en identificar entrevistados en noticias. Responde solo con el nombre completo."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 50
        }
        
        response = _gpt_request_with_retry(headers, data)
        
        if response:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Limpiar respuesta
            if content and content.lower() not in ["no identificado", "no hay entrevistado", "ninguno", "n/a"]:
                logging.info(f"Entrevistado: {GPT_MODEL} -> {content} (ID: {display_id})")
                return content
            else:
                logging.info(f"Entrevistado: {GPT_MODEL} -> No identificado (ID: {display_id})")
                return None
                
        else:
            logging.warning(f"{GPT_MODEL} falló al extraer entrevistado. (ID: {display_id})")
            return _fallback_a_ollama_entrevistado(texto, url_id=url_id)
            
    except Exception as e:
        logging.error(f"Error en extraer_entrevistado_con_gpt: {e}. Usando fallback a Ollama.")
        return _fallback_a_ollama_entrevistado(texto, url_id=url_id)


def _fallback_a_ollama_entrevistado(texto: str, url_id: str = None) -> Optional[str]:
    """
    Función de fallback que usa Ollama cuando GPT falla para extraer entrevistado.
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        str: Nombre completo del entrevistado o None si no se identifica
    """
    try:
        logging.info(f"🔄 Usando fallback a Ollama para extracción de entrevistado... (ID: {_obtener_display_id(url_id)})")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import extraer_entrevistado_con_ollama
        
        resultado_ollama = extraer_entrevistado_con_ollama(texto, url_id=url_id)
        
        if resultado_ollama:
            logging.info(f"✅ Fallback Ollama -> Entrevistado: {resultado_ollama} (ID: {_obtener_display_id(url_id)})")
        else:
            logging.info(f"✅ Fallback Ollama -> Entrevistado: No identificado (ID: {_obtener_display_id(url_id)})")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). No se pudo identificar entrevistado.")
        return None
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). No se pudo identificar entrevistado.")
        return None
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver None
        logging.warning("⚠️ Devolviendo None por defecto (no se pudo identificar)")
        return None


def extraer_entrevistado_con_ia(texto: str, gpt_active: bool = False, url_id: str = None) -> Optional[str]:
    """
    Función unificada para extraer entrevistado con GPT y fallback a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): Si usar GPT o ir directo a Ollama
    
    Returns:
        str: Nombre completo del entrevistado o None si no se identifica
    """
    try:
        if not texto or pd.isna(texto):
            return None
        
        display_id = _obtener_display_id(url_id)
        if gpt_active:
            resultado_gpt = extraer_entrevistado_con_gpt(texto, gpt_active=True, url_id=url_id)
            
            # GPT puede devolver None (no identificado) o un nombre
            # Solo fallback a Ollama si hay error de API (resultado_gpt sería None por excepción)
            if resultado_gpt is not None or resultado_gpt == "":
                return resultado_gpt
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló por error)
        from O_Utils_Ollama import extraer_entrevistado_con_ollama
        resultado_ollama = extraer_entrevistado_con_ollama(texto, url_id=url_id)
        
        if resultado_ollama:
            logging.info(f"Entrevistado: Ollama -> {resultado_ollama} (ID: {display_id})")
        else:
            logging.info(f"Entrevistado: Ollama -> No identificado (ID: {display_id})")
        
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en extraer_entrevistado_con_ia: {e}")
        # Fallback seguro
        return None


# =============================================================================
# DETECCIÓN DE FACTOR POLÍTICO (GPT con fallback a Ollama)
# =============================================================================

def detectar_factor_politico_con_gpt(texto: str, gpt_active: bool = True, url_id: str = None) -> str:
    """
    Detecta si la noticia tiene contenido político usando GPT-3.5-turbo.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): No usado, mantenido por compatibilidad
    
    Returns:
        str: "SI" si tiene factor político, "NO" si no
    """
    try:
        api_key = leer_api_key_desde_env()
        display_id = _obtener_display_id(url_id)
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_factor_politico(texto)
        
        # Prompt ultra-estricto para detectar factor político electoral
        prompt = f"""
        ¿El siguiente texto menciona ELECCIONES, CAMPAÑA ELECTORAL o CANDIDATOS?

        TEXTO:
        {texto}

        MARCA "SI" SOLO SI EL TEXTO MENCIONA:
        - Elecciones (presidenciales, legislativas, provinciales, municipales)
        - Campaña electoral o actos de campaña
        - Candidatos que se postulan a cargos electivos
        - Encuestas electorales o intención de voto
        - Debates entre candidatos
        - Propaganda electoral

        MARCA "NO" SI EL TEXTO HABLA DE:
        - Funcionarios, ministros, autoridades (sin elecciones)
        - Gobierno, gestión pública, políticas públicas
        - Inauguraciones, eventos, anuncios culturales
        - Reclamos o críticas al gobierno
        - Periodismo, poder, instituciones (sin elecciones)
        - Debates académicos sobre política

        IMPORTANTE: Solo marca SI si menciona EXPLÍCITAMENTE elecciones o campaña.
        Si NO menciona elecciones/campaña, es NO.

        Responde SOLO: SI o NO
        """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar modelo por defecto (gpt-3.5-turbo)
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en detectar contenido político en noticias. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = _gpt_request_with_retry(headers, data)
        
        if response:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                resultado = "SI"
            elif content in ['NO', 'FALSE', 'FALSO']:
                resultado = "NO"
            else:
                # Validación adicional por palabras clave
                if any(palabra in content for palabra in ["ELECCION", "CANDIDAT", "CAMPAÑA", "ENCUESTA", "VOTACION", "PARTIDO", "POLITIC"]):
                    resultado = "SI"
                else:
                    resultado = "NO"
            
            logging.info(f"Factor Político: {GPT_MODEL} -> {resultado} (ID: {display_id})")
            return resultado
                
        else:
            logging.warning(f"{GPT_MODEL} falló al detectar factor político. (ID: {display_id})")
            return _fallback_a_ollama_factor_politico(texto, url_id=url_id)
            
    except Exception as e:
        logging.error(f"Error en detectar_factor_politico_con_gpt: {e}. Usando fallback a Ollama.")
        return _fallback_a_ollama_factor_politico(texto, url_id=url_id)


def _fallback_a_ollama_factor_politico(texto: str, url_id: str = None) -> str:
    """
    Función de fallback que usa Ollama cuando GPT falla para detectar factor político.
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        str: "SI" si tiene factor político, "NO" si no
    """
    try:
        logging.info(f"🔄 Usando fallback a Ollama para detección de factor político... (ID: {_obtener_display_id(url_id)})")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import detectar_factor_politico_con_ollama
        
        resultado_ollama = detectar_factor_politico_con_ollama(texto, url_id=url_id)
        logging.info(f"✅ Fallback Ollama -> Factor Político: {resultado_ollama} (ID: {_obtener_display_id(url_id)})")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). Asumiendo NO es político.")
        return "NO"
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). Asumiendo NO es político.")
        return "NO"
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver "NO" (conservador)
        logging.warning("⚠️ Devolviendo NO por defecto (ante la duda, NO es político)")
        return "NO"


def detectar_factor_politico_con_ia(texto: str, gpt_active: bool = False, url_id: str = None) -> str:
    """
    Función unificada para detectar factor político con GPT y fallback a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        gpt_active (bool): Si usar GPT o ir directo a Ollama
    
    Returns:
        str: "SI" si tiene factor político, "NO" si no
    """
    try:
        if not texto or pd.isna(texto):
            return "NO"
        
        display_id = _obtener_display_id(locals().get('url_id', None))
        display_id = _obtener_display_id(url_id)
        if gpt_active:
            resultado_gpt = detectar_factor_politico_con_gpt(texto, gpt_active=True, url_id=url_id)
            
            # GPT siempre devuelve "SI" o "NO"
            if resultado_gpt is not None:
                return resultado_gpt
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló por error)
        from O_Utils_Ollama import detectar_factor_politico_con_ollama
        resultado_ollama = detectar_factor_politico_con_ollama(texto, url_id=url_id)
        logging.info(f"Factor Político: Ollama -> {resultado_ollama} (ID: {display_id})")
        
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en detectar_factor_politico_con_ia: {e}")
        # Fallback seguro
        return "NO"


# =============================================================================
# GENERACIÓN DE INFORMES (GPT con fallback a Ollama)
# =============================================================================

def generar_informe_con_gpt(metricas: dict, contexto: dict = None, modelo: str = None, gpt_active: bool = True) -> dict:
    """
    Genera un informe profesional de análisis de medios usando GPT-3.5-turbo.
    
    Args:
        metricas (dict): Métricas del clipping con estructura idéntica a Ollama
        contexto (dict, optional): Contexto adicional (no utilizado actualmente)
        modelo (str, optional): No usado, mantenido por compatibilidad
        gpt_active (bool): No usado, mantenido por compatibilidad
    
    Returns:
        dict: Estructura idéntica a generar_informe_con_ollama
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_informe(metricas, contexto, modelo)
        
        # PASO 1: Generar el prompt usando la misma función auxiliar de Ollama
        from O_Utils_Ollama import _generar_prompt_informe
        prompt = _generar_prompt_informe(metricas, contexto or {})
        
        # PASO 2: Preparar request para GPT
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,  # Usar modelo por defecto (gpt-3.5-turbo)
            "messages": [
                {"role": "system", "content": "Eres un analista de comunicación política experto en análisis de medios. SIEMPRE respondes en ESPAÑOL."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Baja temperatura para respuestas consistentes (igual que Ollama)
            "max_tokens": 2000   # Máximo de tokens a generar (igual que Ollama)
        }
        
        # PASO 3: Enviar request a GPT con retry y timeout
        inicio = time.time()
        response = _gpt_request_with_retry(headers, data, max_retries=3, timeout=60)
        tiempo_transcurrido = time.time() - inicio
        
        if response and response.status_code == 200:
            # PASO 4: Procesar respuesta exitosa
            result = response.json()
            informe_texto = result['choices'][0]['message']['content'].strip()
            
            # PASO 5: Limpiar el texto del informe (usar función de Ollama)
            #from O_Utils_Ollama import _limpiar_texto_informe
            #informe_limpio = _limpiar_texto_informe(informe_texto)
            
            # PASO 6: Construir respuesta exitosa (formato idéntico a Ollama)
            total_tokens = result['usage']['total_tokens']
            
            logging.info(f"[Informe] ✅ {GPT_MODEL} generó informe exitosamente | Tokens: {total_tokens} | Tiempo: {tiempo_transcurrido:.1f}s")
            
            return {
                "informe": informe_texto,
                "modelo_usado": GPT_MODEL,
                "metricas_utilizadas": metricas,
                "contexto_utilizado": contexto,
                "metadatos": {
                    "total_tokens": total_tokens,
                    "tiempo_generacion": tiempo_transcurrido,
                    "fecha_generacion": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        else:
            # Error HTTP de GPT
            error_msg = f"Error en GPT: Status code {response.status_code if response else 'None'}"
            logging.error(f"[Informe] ❌ {error_msg}")
            return _fallback_a_ollama_informe(metricas, contexto, modelo)
            
    except Exception as e:
        error_msg = f"Error generando informe con GPT: {str(e)}"
        logging.error(f"[Informe] ❌ {error_msg}")
        return _fallback_a_ollama_informe(metricas, contexto, modelo)


def _fallback_a_ollama_informe(metricas: dict, contexto: dict = None, modelo: str = None) -> dict:
    """
    Función de fallback que usa Ollama cuando GPT falla para generar informe.
    
    Args:
        metricas (dict): Métricas del clipping
        contexto (dict, optional): Contexto adicional
        modelo (str, optional): Modelo (se ignora en Ollama, usa su propio modelo)
    
    Returns:
        dict: Resultado de generar_informe_con_ollama
    """
    try:
        logging.info("🔄 Usando fallback a Ollama para generación de informe...")
        
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import generar_informe_con_ollama
        
        resultado_ollama = generar_informe_con_ollama(metricas, contexto, modelo)
        logging.info(f"✅ Fallback Ollama -> Informe generado exitosamente")
        
        return resultado_ollama
    
    except requests.exceptions.ConnectionError:
        logging.warning("⚠️ Ollama no disponible (servicio no accesible). No se pudo generar informe.")
        return {
            "error": "Error generando informe: Ollama no está disponible (servicio no accesible)"
        }
    except requests.exceptions.Timeout:
        logging.warning("⚠️ Ollama timeout (servicio no responde). No se pudo generar informe.")
        return {
            "error": "Error generando informe: Ollama timeout (servicio no responde)"
        }
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver error
        return {
            "error": f"Error generando informe: Tanto GPT como Ollama fallaron. {str(e)}"
        }


def generar_informe_con_ia(metricas: dict, contexto: dict = None, modelo: str = None, gpt_active: bool = False) -> dict:
    """
    Función unificada para generar informes con GPT y fallback a Ollama.
    
    Args:
        metricas (dict): Métricas del clipping con estructura idéntica a Ollama
        contexto (dict, optional): Contexto adicional
        modelo (str, optional): Modelo a usar (GPT o Ollama según gpt_active)
        gpt_active (bool): Si usar GPT o ir directo a Ollama
    
    Returns:
        dict: Diccionario con informe generado y metadatos
    """
    try:
        if gpt_active:
            resultado_gpt = generar_informe_con_gpt(metricas, contexto, modelo, gpt_active=True)
            
            # Si GPT devolvió un informe válido (sin campo "error"), retornarlo
            if "informe" in resultado_gpt and "error" not in resultado_gpt:
                return resultado_gpt
            else:
                logging.info("GPT falló, usando fallback a Ollama...")
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló)
        from O_Utils_Ollama import generar_informe_con_ollama
        resultado_ollama = generar_informe_con_ollama(metricas, contexto, modelo)
        logging.info(f"Informe: Ollama -> Generado exitosamente")
        
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en generar_informe_con_ia: {e}")
        # Fallback seguro
        return {
            "error": f"Error generando informe: {str(e)}"
        }


if __name__ == "__main__":
    # Test básico de la función
    print("Testing clasificar_tipo_publicacion_con_gpt...")
    resultado = clasificar_tipo_publicacion_con_gpt("Esta es una noticia sobre un evento cultural que se realizará el próximo fin de semana", "Gabriela Ricardes", "Ministerio de Cultura")
    print(f"Resultado: {resultado}")
