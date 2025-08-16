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


def es_entrevista_con_gpt(texto: str) -> bool:
    """
    Función auxiliar para determinar si una noticia es entrevista usando GPT.
    Con fallback automático a Ollama si GPT falla por cualquier motivo.
    
    Args:
        texto (str): Texto plano de la noticia
    
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
        
        # Preparar request para GPT
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en identificar entrevistas periodísticas. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                return False
            else:
                # Si GPT devuelve algo inesperado, usar fallback
                logging.warning(f"GPT devolvió respuesta inesperada: '{content}'. Usando fallback a Ollama.")
                return _fallback_a_ollama_entrevista(texto)
                
        else:
            logging.warning(f"Error en API de GPT: {response.status_code}. Usando fallback a Ollama.")
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


def es_agenda_con_gpt(texto: str) -> bool:
    """
    Función auxiliar para determinar si una noticia es agenda usando GPT.
    Con fallback automático a Ollama si GPT falla por cualquier motivo.
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        bool: True si es agenda, False si no
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return _fallback_a_ollama_agenda(texto)
        
        # Prompt para detectar agendas
        prompt = f"""
        Eres un experto en clasificar noticias periodísticas. Tu tarea es determinar si un texto es una AGENDA o NO.

        TEXTO DE LA NOTICIA:
        {texto}

        CRITERIOS PARA AGENDA:
        ✅ Anuncios de eventos, actividades o actividades programadas
        ✅ Información sobre fechas, horarios y lugares específicos
        ✅ Programación de espectáculos, exposiciones, conciertos
        ✅ Calendario de actividades culturales o institucionales
        ✅ Anuncios de inauguraciones, presentaciones o lanzamientos
        ✅ Información sobre fechas límite, inscripciones o convocatorias
        ✅ Programación de festivales, ferias o eventos masivos

        NO ES AGENDA:
        ❌ Noticias sobre eventos que ya sucedieron
        ❌ Crónicas o reseñas de actividades pasadas
        ❌ Entrevistas o declaraciones sobre eventos
        ❌ Análisis o opiniones sobre programación
        ❌ Notas informativas sin fechas específicas
        ❌ Reportajes sobre eventos en general

        IMPORTANTE: 
        - Analiza TODO el texto completo, no solo el inicio
        - Las agendas tienen fechas, horarios o información programática
        - Debe haber información sobre eventos futuros o programados
        - No solo menciones de eventos, sino información programática

        RESPONDE SOLO: "SI" si es agenda, "NO" si no lo es.
        """
        
        # Preparar request para GPT
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en identificar agendas periodísticas. Responde solo con SI o NO."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 10
        }
        
        response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip().upper()
            
            # Normalizar respuesta
            if content in ['SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO']:
                return True
            elif content in ['NO', 'FALSE', 'FALSO']:
                return False
            else:
                # Si GPT devuelve algo inesperado, usar fallback
                logging.warning(f"GPT devolvió respuesta inesperada: '{content}'. Usando fallback a Ollama.")
                return _fallback_a_ollama_agenda(texto)
                
        else:
            logging.warning(f"Error en API de GPT: {response.status_code}. Usando fallback a Ollama.")
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


def clasificar_tipo_publicacion_con_gpt(texto: str) -> str:
    """
    Clasifica el tipo de publicación usando funciones GPT especializadas.
    Procesa secuencialmente: Agenda → Entrevista → Nota (por defecto)
    
    Args:
        texto (str): Texto plano de la noticia
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        logging.info("🔍 Clasificando tipo de publicación con GPT...")
        
        # 1. AGENDA (primera prioridad - más usual)
        logging.info("📅 Verificando si es Agenda...")
        if es_agenda_con_gpt(texto):
            logging.info("✅ Clasificado como: Agenda")
            return "Agenda"
        
        # 2. ENTREVISTA (segunda prioridad)
        logging.info("🎤 Verificando si es Entrevista...")
        if es_entrevista_con_gpt(texto):
            logging.info("✅ Clasificado como: Entrevista")
            return "Entrevista"
        
        # 3. Por defecto (si no es Agenda ni Entrevista)
        logging.info("📰 No es Agenda ni Entrevista, clasificando como: Nota")
        return "Nota"
        
    except Exception as e:
        logging.error(f"❌ Error en clasificar_tipo_publicacion_con_gpt: {e}")
        # En caso de error, devolver "Nota" como fallback seguro
        return "Nota"


def clasificar_tipo_publicacion_con_ia(texto: str, ministro_actual: str = "Gabriela Ricardes", gpt_active: bool = False) -> str:
    """
    Función unificada para clasificar tipo de publicación con GPT y fallback a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_actual (str): Nombre del ministro actual
        gpt_active (bool): Si usar GPT o ir directo a Ollama
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        # Importar aquí para evitar dependencias circulares
        from O_Utils_Ollama import clasificar_tipo_publicacion_unificado
        
        if gpt_active:
            logging.info("Intentando clasificar tipo de publicación con GPT...")
            resultado_gpt = clasificar_tipo_publicacion_con_gpt(texto)
            
            # GPT siempre devuelve algo (Agenda, Entrevista, o Nota)
            # Solo fallback a Ollama si hay error de API o excepción
            if resultado_gpt is not None:
                logging.info(f"GPT clasificó como: {resultado_gpt}")
                return resultado_gpt
            else:
                logging.info("GPT falló por error de API, usando fallback a Ollama...")
        
        # Fallback a Ollama (cuando gpt_active=False o GPT falló por error)
        logging.info("Clasificando tipo de publicación con Ollama...")
        resultado_ollama = clasificar_tipo_publicacion_unificado(texto, ministro_actual)
        logging.info(f"Ollama clasificó como: {resultado_ollama}")
        return resultado_ollama
        
    except Exception as e:
        logging.error(f"Error en clasificar_tipo_publicacion_con_ia: {e}")
        # Fallback seguro
        return "Nota"


def clasificar_tipo_publicacion_con_gpt(texto: str, ministro_actual: str = "Gabriela Ricardes") -> Optional[str]:
    """
    Clasifica el tipo de publicación usando GPT con fallback a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_actual (str): Nombre del ministro actual
    
    Returns:
        str: Tipo de publicación clasificado o None si falla
    """
    try:
        api_key = leer_api_key_desde_env()
        
        if not api_key:
            logging.warning("No se encontró API key de OpenAI. Usando fallback a Ollama.")
            return None
        
        # Prompt para GPT basado en la lógica de Ollama
        prompt = f"""
        TAREA: Clasificar el tipo de publicación de la siguiente noticia.

        TEXTO DE LA NOTICIA:
        {texto}

        MINISTRO ACTUAL: {ministro_actual}

        INSTRUCCIONES:
        Analiza el contenido y clasifica como UNO de estos tipos:

        1. "Agenda" - Si es información sobre eventos, actividades, programación, horarios, fechas, lugares, actividades culturales, espectáculos, festivales, inauguraciones, etc.

        2. "Entrevista" - Si contiene preguntas y respuestas, formato de entrevista, diálogo con periodista, citas entrecomilladas extensas, formato "pregunta-respuesta"

        3. "Declaración" - Si contiene citas específicas del ministro {ministro_actual} o autoridades, declaraciones oficiales, comunicados, anuncios de políticas, pero NO en formato de entrevista

        4. "Nota de opinión" - Si es un artículo de opinión, editorial, análisis personal, crítica subjetiva, columna de opinión (muy raro, <1%)

        5. "Nota" - Si es información general, noticia estándar, reportaje, crónica, información que no cabe claramente en las categorías anteriores

        CRITERIOS DE PRIORIDAD:
        - PRIORIDAD ALTA: Agenda (más frecuente, eventos y actividades)
        - PRIORIDAD MEDIA: Entrevista (formato distintivo de preguntas-respuestas)
        - PRIORIDAD MEDIA: Declaración (citas específicas del ministro)
        - PRIORIDAD BAJA: Nota de opinión (muy rara)
        - DEFAULT: Nota (lo que no cabe claramente en otras categorías)

        Responde ÚNICAMENTE con: Agenda, Entrevista, Declaración, Nota de opinión, o Nota
        """
        
        # Preparar request para GPT
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": "Eres un clasificador especializado en tipos de publicaciones periodísticas. Responde solo con el tipo exacto."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Baja temperatura para respuestas más consistentes
            "max_tokens": 20
        }
        
        response = requests.post(GPT_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Normalizar respuesta
            content_lower = content.lower()
            if 'agenda' in content_lower:
                return "Agenda"
            elif 'entrevista' in content_lower:
                return "Entrevista"
            elif 'declaración' in content_lower or 'declaracion' in content_lower or 'declaración' in content_lower:
                return "Declaración"
            elif 'opinión' in content_lower or 'opinion' in content_lower:
                return "Nota de opinión"
            elif 'nota' in content_lower:
                return "Nota"
            else:
                # GPT funcionó pero no pudo clasificar claramente - usar "Nota" como default
                logging.warning(f"GPT devolvió respuesta inesperada: '{content}'. Usando 'Nota' como default.")
                return "Nota"
                
        else:
            logging.warning(f"Error en API de GPT: {response.status_code}. Usando fallback.")
            return None
            
    except Exception as e:
        logging.error(f"Error en clasificación GPT: {e}. Usando fallback.")
        return None

if __name__ == "__main__":
    # Test básico de la función
    print("Testing clasificar_tipo_publicacion_con_gpt...")
    resultado = clasificar_tipo_publicacion_con_gpt("Esta es una noticia sobre un evento cultural que se realizará el próximo fin de semana")
    print(f"Resultado: {resultado}")
