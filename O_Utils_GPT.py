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
    return "gpt-4o"  # Modelo premium para funciones críticas

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
            logging.info("API key de OpenAI encontrada en .env")
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

def valorar_con_ia(texto: str, api_key: Optional[str] = None, ministro_key_words: Optional[str] = None, ministerios_key_words: Optional[str] = None, gpt_active: bool = True) -> str:
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
    
    if gpt_active:
        # Intentar con GPT primero
        valoracion_base = valorar_noticia_con_gpt(texto, api_key)
        if valoracion_base is not None:
            modelo_usado = f"GPT-{GPT_MODEL}"  # Mostrar modelo específico
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
        # Aplicar heurística si se proporciona al menos uno (ministro_key_words o ministerios_key_words)
        if (ministro_key_words or ministerios_key_words):
            from Z_Utils import aplicar_heuristica_valoracion
            resultado_final = aplicar_heuristica_valoracion(valoracion_base, texto, ministro_key_words, ministerios_key_words)
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

def clasificar_tema_con_gpt(
    texto: str,
    lista_temas: List[str],
    tipo_publicacion: Optional[str] = None,
    gpt_active: bool = True,
) -> str:
    """
    Clasifica un tema usando GPT como primera opción y fallback a Ollama.

    - Debe devolver EXACTAMENTE uno de lista_temas
    - Si tipo_publicacion == 'Agenda' → 'Actividades programadas'
    - Solo clasificación por contenido (sin contexto temporal)
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
                logging.info(f"🔍 Clasificando tema con {GPT_MODEL} para tipo: {tipo_publicacion}")
                temas_str = "\n".join([f"- {t}" for t in lista_temas])
                # Solo clasificación por contenido - sin contexto temporal

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
                    "4) Umbral de confianza: si no hay evidencia clara (ni literal ni paráfrasis inequívoca), elegí exactamente: Actividades programadas.\n"
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
                    "max_tokens": 20,
                }

                response = _gpt_request_with_retry(headers, data)
                if response:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()

                    # Saneo mínimo de salida (quitar comillas/puntos sueltos)
                    content = content.strip().strip('"').strip("'").rstrip(".").strip()

                    # Validación estricta
                    if content in lista_temas:
                        logging.info(f"✅ {GPT_MODEL} clasificó tema como: {content}")
                        return content

                    # Intento de match por casefold (sin alterar la decisión final)
                    mapeo_lower = {t.casefold(): t for t in lista_temas}
                    if content.casefold() in mapeo_lower:
                        logging.info(f" Aplicando casefold matching: '{content}' → '{mapeo_lower[content.casefold()]}'")
                        return mapeo_lower[content.casefold()]

                    # Si no es válido → fallback a Ollama
                else:
                    logging.warning(f"GPT tema falló al clasificar tema.")
                    logging.info(f"🔄 {GPT_MODEL} no pudo clasificar, activando fallback a Ollama...")

        # Fallback a Ollama (misma lógica que el proyecto usa hoy)
        try:
            from O_Utils_Ollama import clasificar_tema_ollama
            resultado_ollama = clasificar_tema_ollama(
                texto,
                lista_temas,
                tipo_publicacion,
            )
            logging.info(f"✅ Ollama clasificó tema como: {resultado_ollama}")
            return resultado_ollama
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
    gpt_active: bool = True,
) -> str:
    """
    Interfaz unificada similar a valorar_con_ia:
    - Si gpt_active y hay API key → intenta GPT (clasificar_tema_con_gpt)
    - Si falla o está desactivado → fallback a Ollama (clasificar_tema_ollama)
    """
    try:
        if not texto or not lista_temas:
            return "Revisar Manual"

        if gpt_active:
            resultado = clasificar_tema_con_gpt(
                texto=texto,
                lista_temas=lista_temas,
                tipo_publicacion=tipo_publicacion,
                gpt_active=True,
            )
            if resultado:
                return resultado

        # Fallback a Ollama
        from O_Utils_Ollama import clasificar_tema_ollama
        return clasificar_tema_ollama(
            texto,
            lista_temas,
            tipo_publicacion,
        )
    except Exception as e:
        logging.error(f"clasificar_tema_con_ia error: {e}")
        return "Actividades programadas"


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
                logging.info(f"✅ {GPT_MODEL} clasificó como: Entrevista")
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                logging.info(f"❌ {GPT_MODEL} clasificó como: NO Entrevista")
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
        logging.info(f"✅ Fallback a Ollama completado: {resultado_ollama}")
        
        return resultado_ollama
        
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
                logging.info(f"✅ {GPT_MODEL} clasificó como: Agenda")
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                logging.info(f"❌ {GPT_MODEL} clasificó como: NO Agenda")
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
        logging.info(f"✅ Fallback a Ollama completado: {resultado_ollama}")
        
        return resultado_ollama
        
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
                logging.info(f"✅ {GPT_MODEL} clasificó como: Declaración")
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                logging.info(f"❌ {GPT_MODEL} clasificó como: NO Declaración")
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
        logging.info(f"✅ Fallback a Ollama completado: {resultado_ollama}")
        
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"❌ Fallback a Ollama también falló: {e}")
        # En caso extremo, devolver False (ante la duda, NO es declaración)
        logging.warning("⚠️ Devolviendo False por defecto (ante la duda, NO es declaración)")
        return False


def clasificar_tipo_publicacion_con_gpt(texto: str, ministro_key_words: str = "Gabriela Ricardes", ministerios_key_words: str = None) -> str:
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
        logging.info("🔍 Clasificando tipo de publicación con GPT...")
        
        # 1. DECLARACIÓN (primera prioridad - más específica, evita falsos positivos)
        logging.info("💬 Verificando si es Declaración...")
        if es_declaracion_con_gpt(texto, ministro_key_words, ministerios_key_words, gpt_active=True):
            logging.info("✅ Clasificado como: Declaración")
            return "Declaración"
        
        # 2. AGENDA (segunda prioridad - más frecuente, regla clara)
        logging.info("📅 Verificando si es Agenda...")
        if es_agenda_con_gpt(texto, gpt_active=True):
            logging.info("✅ Clasificado como: Agenda")
            return "Agenda"
        
        # 3. ENTREVISTA (tercera prioridad - formato distintivo)
        logging.info("🎤 Verificando si es Entrevista...")
        if es_entrevista_con_gpt(texto, gpt_active=True):
            logging.info("✅ Clasificado como: Entrevista")
            return "Entrevista"
        
        # 4. NOTA (por defecto - lo que no cabe claramente en otras categorías)
        logging.info("📰 No es Declaración, Agenda ni Entrevista, clasificando como: Nota")
        return "Nota"
        
    except Exception as e:
        logging.error(f"❌ Error en clasificar_tipo_publicacion_con_gpt: {e}")
        # En caso de error, devolver "Nota" como fallback seguro
        return "Nota"


def clasificar_tipo_publicacion_con_ia(texto: str, ministro_key_words: str = "Gabriela Ricardes", ministerios_key_words: str = None, gpt_active: bool = False) -> str:
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
        
        if gpt_active:
            logging.info("Intentando clasificar tipo de publicación con GPT...")
            resultado_gpt = clasificar_tipo_publicacion_con_gpt(texto, ministro_key_words, ministerios_key_words)
            
            # GPT siempre devuelve algo (Agenda, Entrevista, Declaración, o Nota)
            # Solo fallback a Ollama si hay error de API o excepción
            if resultado_gpt is not None:
                logging.info(f"GPT clasificó como: {resultado_gpt}")
                return resultado_gpt
            else:
                logging.info("GPT falló por error de API, usando fallback a Ollama...")
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló por error)
        logging.info("Clasificando tipo de publicación con Ollama...")
        resultado_ollama = clasificar_tipo_publicacion_unificado(texto, ministro_key_words, ministerios_key_words)
        logging.info(f"Ollama clasificó como: {resultado_ollama}")
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en clasificar_tipo_publicacion_con_ia: {e}")
        # Fallback seguro
        return "Nota"


if __name__ == "__main__":
    # Test básico de la función
    print("Testing clasificar_tipo_publicacion_con_gpt...")
    resultado = clasificar_tipo_publicacion_con_gpt("Esta es una noticia sobre un evento cultural que se realizará el próximo fin de semana", "Gabriela Ricardes", "Ministerio de Cultura")
    print(f"Resultado: {resultado}")
