import requests
import logging
import pandas as pd
import Z_Utils as Z
import re
from datetime import datetime

# Modelo por defecto - Opciones disponibles: "llama3:8b", "llama3.1:8b"
MODELO_OLLAMA = "llama3.1:8b"  
OLLAMA_URL = "http://localhost:11434/api/generate"


# Control para imprimir el estado del servicio solo una vez
_ollama_estado_reportado = False

def _verificar_e_imprimir_estado_ollama(timeout_seconds: int = 2) -> bool:
    """
    Verifica si el servicio de Ollama está accesible y lo imprime por consola UNA sola vez.
    Retorna True si responde 200 en /api/tags, False en caso contrario o error.
    """
    global _ollama_estado_reportado
    if _ollama_estado_reportado:
        # Ya reportado previamente en esta ejecución
        return True
    try:
        tags_url = OLLAMA_URL.replace("/api/generate", "/api/tags")
        resp = requests.get(tags_url, timeout=timeout_seconds)
        if resp.status_code == 200:
            print("[Ollama] Servicio activo (HTTP 200)")
            logging.info("[Ollama] Servicio activo (HTTP 200)")
            _ollama_estado_reportado = True
            return True
        else:
            print(f"[Ollama] No disponible (HTTP {resp.status_code})")
            logging.error(f"[Ollama] No disponible (HTTP {resp.status_code})")
            _ollama_estado_reportado = True
            return False
    except Exception as e:
        print("[Ollama] No disponible (error de conexión)")
        logging.error(f"[Ollama] Error verificando servicio: {repr(e)}")
        _ollama_estado_reportado = True
        return False

def set_modelo_ollama(modelo):
    """
    Actualiza el modelo de Ollama globalmente.
    
    Args:
        modelo (str): Nombre del modelo (ej: "llama3:8b", "llama3.1:8b", "mistral:7b")
    """
    global MODELO_OLLAMA
    MODELO_OLLAMA = modelo
    logging.info(f"Modelo de Ollama actualizado a: {modelo}")

def get_modelo_ollama():
    """
    Obtiene el modelo de Ollama actualmente configurado.
    
    Returns:
        str: Nombre del modelo actual
    """
    return MODELO_OLLAMA

# ============================================================================
# FUNCIONES DE VALORACIÓN
# ============================================================================

def valorar_noticia_con_ollama_base(texto):
    """
    Función base para valorar noticias con Ollama.
    Retorna "NEGATIVA" o "NO_NEGATIVA" (sin "OTRO").
    """
    prompt = (
        "Analizá el siguiente texto y determiná si la noticia es NEGATIVA o NO_NEGATIVA.\n\n"
        "CRITERIO PARA CONSIDERARLA NEGATIVA:\n"
        "- Contiene críticas, denuncias, problemas, conflictos, errores, fallas\n"
        "- Menciona escándalos, polémicas, controversias, malestar\n"
        "- Describe situaciones problemáticas, dificultades, obstáculos\n"
        "- Incluye quejas, reclamos, protestas, descontento\n"
        "- Habla de crisis, emergencias, urgencias, problemas graves\n\n"
        "CRITERIO PARA CONSIDERARLA NO_NEGATIVA:\n"
        "- Contiene anuncios positivos, logros, éxitos, avances\n"
        "- Menciona inauguraciones, presentaciones, estrenos, eventos\n"
        "- Describe mejoras, soluciones, acuerdos, colaboraciones\n"
        "- Incluye reconocimientos, premios, homenajes, celebraciones\n"
        "- Habla de proyectos, iniciativas, propuestas, actividades\n\n"
        "IMPORTANTE:\n"
        "- Si NO es claramente negativa, es NO_NEGATIVA\n"
        "- Respondé únicamente con NEGATIVA o NO_NEGATIVA\n"
        "- NO agregues explicaciones ni texto adicional\n\n"
        f"TEXTO A ANALIZAR:\n{texto}\n"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        salida = result.get("response", "").strip().upper()
        if salida == "NEGATIVA":
            return "NEGATIVA"
        else:
            return "NO_NEGATIVA"
    except Exception as e:
        logging.error(f"[Ollama] Error valorando noticia: {repr(e)} | Texto: {texto[:120]}...")
        return "NO_NEGATIVA"  # Fallback conservador

def valorar_noticia_con_ollama(texto, ministro_key_words=None, ministerios_key_words=None):
    """
    Valora noticias con Ollama y aplica heurística para POSITIVA/NEUTRA.
    
    Args:
        texto (str): Texto a analizar
        ministro_key_words (str or list, optional): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
    """
    valoracion_base = valorar_noticia_con_ollama_base(texto)
    
    if valoracion_base == "NEGATIVA":
        return "NEGATIVA"
    elif valoracion_base == "NO_NEGATIVA":
        # Aplicar heurística para POSITIVA/NEUTRA
        if (ministro_key_words or ministerios_key_words):
            return Z.aplicar_heuristica_valoracion(valoracion_base, texto, ministro_key_words, ministerios_key_words)
        else:
            return "NEUTRA"
    else:
        return "NEUTRA"  # Fallback

# ============================================================================
# FUNCIONES DE CLASIFICACIÓN DE TIPO DE PUBLICACIÓN
# ============================================================================

def es_agenda_ollama(texto):
    """
    Detecta si es una AGENDA usando Ollama: noticia que enumera actividades/eventos culturales.
    """
    if not texto or pd.isnull(texto):
        return False
    
    prompt = (
        "¿El siguiente texto es una AGENDA cultural?\n\n"
        "CRITERIOS PARA CONSIDERARLO AGENDA:\n"
        "- Enumera o describe AL MENOS DOS actividades/eventos diferentes\n"
        "- Cada actividad debe tener fecha, lugar y descripción\n"
        "- Suele estar organizada en formato de lista\n"
        "- Puede mencionar 'agenda', 'guía', 'propuestas', 'programación'\n\n"
        "EJEMPLOS DE AGENDA:\n"
        "- 'Sábado 15: concierto en Teatro X. Domingo: exposición en Museo Y'\n"
        "- 'Esta semana: lunes cine, miércoles teatro, viernes música'\n"
        "- 'Agenda cultural: martes inauguración, jueves presentación'\n\n"
        "EJEMPLOS DE NO AGENDA:\n"
        "- Una sola actividad o evento\n"
        "- Noticia general sobre cultura\n"
        "- Información sin fechas específicas\n\n"
        f"TEXTO: {texto}\n\n"
        "Respondé únicamente SI o NO:"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        salida = result.get("response", "").strip().upper()
        
        if salida.startswith("SI"):
            return True
        else:
            return False
            
    except Exception as e:
        logging.error(f"[Ollama] Error detectando agenda: {repr(e)} | Texto: {texto[:120]}...")
        return False  # Fallback conservador

def es_entrevista_ollama(texto):
    """
    Detecta si es una ENTREVISTA usando Ollama: formato pregunta-respuesta o diálogo.
    """
    if not texto or pd.isnull(texto):
        return False
    
    prompt = (
        "¿El siguiente texto es una ENTREVISTA periodística?\n\n"
        "CRITERIOS PARA CONSIDERARLO ENTREVISTA:\n"
        "- Formato pregunta-respuesta entre periodista y entrevistado\n"
        "- Puede tener guiones (-), iniciales, o nombres antes de cada intervención\n"
        "- Preguntas que empiezan con '¿' seguidas de respuestas\n"
        "- Diálogo con atribuciones ('explicó X', 'respondió Y')\n"
        "- Menciones de 'entrevista', 'charló con', 'podés escuchar'\n\n"
        "EJEMPLOS DE ENTREVISTA:\n"
        "- '-¿Por qué elegiste este proyecto?\n- Porque me representa...'\n"
        "- 'Periodista: ¿Cómo empezó? Entrevistado: Hace 20 años...'\n"
        "- 'Charló con Teresa Ricardi. Escuchá la nota: http://...'\n\n"
        "EJEMPLOS DE NO ENTREVISTA:\n"
        "- Solo citas sueltas sin preguntas\n"
        "- Comunicado o información general\n"
        "- Relato sin diálogo\n\n"
        f"TEXTO: {texto}\n\n"
        "Respondé únicamente SI o NO:"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        salida = result.get("response", "").strip().upper()
        
        if salida.startswith("SI"):
            return True
        else:
            return False
            
    except Exception as e:
        logging.error(f"[Ollama] Error detectando entrevista: {repr(e)} | Texto: {texto[:120]}...")
        return False  # Fallback conservador

def es_declaracion_ollama(texto, ministro_key_words, ministerios_key_words=None):
    """
    Detecta si es una DECLARACIÓN usando Ollama: nota con cita textual atribuida al ministro o ministerio.
    
    Args:
        texto (str): Texto a analizar
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
    """
    if not texto or pd.isna(texto):
        return False
    
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
        else:
            actores.append(ministro_key_words)
    
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
        else:
            actores.append(ministerios_key_words)
    
    # Verificar que tengamos actores válidos
    if not actores:
        logging.warning("No se encontraron actores válidos para buscar declaraciones en Ollama")
        return False
    
    # Convertir a string legible
    actores_str = ", ".join(actores)
    
    # Prompt unificado para buscar citas adjudicadas a actores
    prompt = (
        "¿El siguiente texto contiene AL MENOS UNA DECLARACIÓN (cita textual) atribuida a alguno de estos actores?\n\n"
        f"ACTORES A BUSCAR: {actores_str}\n\n"
        "CRITERIOS FLEXIBLES PARA CONSIDERARLO DECLARACIÓN:\n"
        "✅ DEBE tener AL MENOS UNA CITA entre comillas (\"...\" o '...') atribuida a alguno de los actores\n"
        "✅ El actor puede ser referenciado de forma directa o indirecta (fuentes, cartera, ministerio, etc.)\n"
        "✅ Debe contener verbos de comunicación/acción (dijo, anunció, informó, explicaron, señaló, etc.)\n"
        "✅ Una noticia puede contener MÚLTIPLES declaraciones de diferentes actores\n"
        "✅ Las citas pueden ser extensas y detalladas\n"
        "✅ Solo importa que esté entre comillas y atribuida a un actor\n\n"
        "EJEMPLOS CLAROS DE DECLARACIÓN:\n"
        "- 'Estamos trabajando en el proyecto', dijo Gabriela Ricardes\n"
        "- El Ministerio de Cultura anunció: 'Vamos a implementar nuevas políticas'\n"
        "- La ministra expresó: 'Es fundamental apoyar la cultura'\n"
        "- Desde la cartera cultural se informó que 'se realizarán inversiones'\n"
        "- La funcionaria manifestó: 'Es importante preservar el patrimonio'\n"
        "- 'Según explicaron fuentes del ministerio: 'la plataforma ya la creamos...''\n"
        "- 'La ministra señaló: 'Es una muestra concreta de cómo...''\n"
        "- 'Fuentes del área informaron que 'la aplicación funcionará como...''\n\n"
        "EJEMPLOS CLAROS DE NO DECLARACIÓN:\n"
        "- La ministra presentó el programa (sin cita textual)\n"
        "- Se inauguró el teatro (sin cita ni actor)\n"
        "- El programa incluye actividades culturales (sin cita)\n"
        "- Se realizó una conferencia (sin cita ni actor)\n"
        "- La funcionaria asistió al evento (sin cita)\n"
        "- Se anunció la nueva política (sin cita textual)\n\n"
        "IMPORTANTE: Si hay AL MENOS UNA cita textual atribuida a un actor, es DECLARACIÓN.\n"
        f"TEXTO: {texto}\n\n"
        "Respondé únicamente SI o NO:"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        salida = result.get("response", "").strip().upper()
        
        if salida.startswith("SI"):
            return True
        else:
            return False
            
    except Exception as e:
        logging.error(f"[Ollama] Error detectando declaración: {repr(e)} | Texto: {texto[:120]}...")
        return False  # Fallback conservador

def clasificar_tipo_publicacion_unificado(texto, ministro_key_words="Gabriela Ricardes", ministerios_key_words=None):
    """
    Clasifica el tipo de publicación con orden de prioridad:
    1. Agenda (más frecuente)
    2. Entrevista (formato distintivo)
    3. Declaración (citas específicas)
    4. Nota (default)
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_key_words (str or list): Palabras clave para identificar al ministro
        ministerios_key_words (str or list, optional): Palabras clave para identificar al ministerio
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        # Verificar e informar estado del servicio la primera vez
        _verificar_e_imprimir_estado_ollama()

        if not texto or pd.isnull(texto):
            return "Nota"
        
        logging.debug(f"Clasificando con ministro_key_words: {ministro_key_words}, ministerios_key_words: {ministerios_key_words}")
        
        # 1. PRIORIDAD ALTA: Agenda (más frecuente, regla clara)
        logging.debug("Verificando si es Agenda...")
        if es_agenda_ollama(texto):
            logging.debug(f"Clasificado como Agenda")
            return "Agenda"
        
        # 2. PRIORIDAD MEDIA: Entrevista (formato distintivo)
        logging.debug("Verificando si es Entrevista...")
        if es_entrevista_ollama(texto):
            logging.debug(f"Clasificado como Entrevista")
            return "Entrevista"
        
        # 3. PRIORIDAD MEDIA: Declaración (citas específicas)
        logging.debug("Verificando si es Declaración...")
        logging.debug(f"Pasando a es_declaracion_ollama: ministro_key_words={ministro_key_words}, ministerios_key_words={ministerios_key_words}")
        if es_declaracion_ollama(texto, ministro_key_words, ministerios_key_words):
            logging.debug(f"Clasificado como Declaración")
            return "Declaración"
        
        # 4. DEFAULT: Nota (lo que no cabe claramente en otras categorías)
        logging.debug(f"Clasificado como Nota (default)")
        return "Nota"
        
    except Exception as e:
        logging.error(f"Error al clasificar tipo de publicación: {e}")
        logging.error(f"Parámetros: texto={texto[:100]}..., ministro_key_words={ministro_key_words}, ministerios_key_words={ministerios_key_words}")
        return "Nota"  # Fallback seguro

# ============================================================================
# FUNCIONES DE CLASIFICACIÓN DE TEMAS
# ============================================================================

def clasificar_tema_ollama(texto, lista_temas, tipo_publicacion=None):
    """
    Clasifica una noticia en un tema específico usando heurísticas + IA.
    Combina coincidencias exactas, reglas de negocio y consulta a Ollama.
    
    Args:
        texto (str): Texto plano de la noticia
        lista_temas (list): Lista de temas disponibles
        tipo_publicacion (str): Tipo de publicación (para fallback)
    
    Returns:
        str: Tema asignado o "Revisar Manual"
    """
    if not texto or not lista_temas:
        return "Revisar Manual"

    # 1. Heurísticas muy estrictas para coincidencias exactas
    texto_lower = texto.lower()
    for tema in lista_temas:
        tema_lower = tema.lower()
        if tema_lower in texto_lower or texto_lower.count(tema_lower) > 0:
            return tema

    # 2. Fallback por tipo de publicación
    if tipo_publicacion == "Agenda":
        return "Actividades programadas"

    # 3. Consulta a IA si las heurísticas fallan
    return _promptear_clasificacion_tema_ollama(texto, lista_temas)

#Funcion privada aux para Tema_ollama
def _promptear_clasificacion_tema_ollama(texto, lista_temas):
    """
    Función privada que consulta a Ollama para clasificar el tema.
    Construye el prompt y maneja la respuesta de la IA.
    """
    # Construir lista textual completa de temas (lista cerrada de elegibles)
    temas_str = "\n".join([f"- {t}" for t in lista_temas])

    # Armar prompt simplificado (versión mejorada)
    prompt = (
        f"ANALIZA esta noticia (título + cuerpo completo) y asígnale el tema MÁS ADECUADO de la lista disponible.\n\n"
        f"IMPORTANTE: Solo puedes elegir de esta lista, NO inventes temas:\n{temas_str}\n\n"
        "CRITERIOS DE EVALUACIÓN (APLICAR EN ESTE ORDEN):\n"
        "1. PRIORIDAD ALTA: Si el nombre EXACTO de un tema aparece en el título o cuerpo → elegir ese tema\n"
        "2. PRIORIDAD MEDIA: Si hay palabras clave específicas de un tema (ej: 'BAFICI', 'Juventus Lyrica', 'Abasto') → elegir ese tema\n"
        "3. PRIORIDAD BAJA: Solo si NO hay evidencia específica clara → elegir 'Actividades programadas'\n\n"
        "REGLAS IMPORTANTES:\n"
        "- NUNCA ignores un tema específico que está claramente mencionado en el texto\n"
        "- Los temas genéricos son SOLO para noticias que realmente no encajan con temas específicos\n"
        "- Si hay dudas entre temas similares, elige el MÁS ESPECÍFICO\n\n"
        f"NOTICIA A ANALIZAR:\n{texto}\n\n"
        "RESPUESTA: Responde ÚNICAMENTE con el nombre exacto del tema elegido (sin comillas, sin puntos, sin texto adicional)."
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        tema_asignado = result.get("response", "").strip()
        
        # Validar que el tema asignado esté en la lista
        if tema_asignado in lista_temas:
            return tema_asignado
        else:
            return "Actividades programadas"  # Fallback
            
    except Exception as e:
        logging.error(f"[Ollama] Error clasificando tema: {repr(e)} | Texto: {texto[:120]}...")
        return "Actividades programadas"  # Fallback

# ============================================================================
# FUNCIONES DE EXTRACCIÓN
# ============================================================================

def extraer_entrevistado_con_ollama(texto):
    """
    Extrae el nombre completo del entrevistado usando Ollama.
    """
    prompt = (
        "Identificá quién está siendo entrevistado en la siguiente noticia.\n\n"
        "IMPORTANTE:\n"
        "- Extraé ÚNICAMENTE el NOMBRE COMPLETO (nombre + apellido)\n"
        "- NO agregues explicaciones, títulos, cargos ni texto adicional\n"
        "- Si no hay entrevistado claro, respondé 'No identificado'\n"
        "- Si hay múltiples entrevistados, elegí el principal\n\n"
        f"TEXTO:\n{texto}\n\n"
        "NOMBRE COMPLETO DEL ENTREVISTADO:"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        entrevistado = result.get("response", "").strip()
        
        # Limpiar respuesta
        if entrevistado and entrevistado.lower() not in ["no identificado", "no hay entrevistado"]:
            return entrevistado
        else:
            return None
            
    except Exception as e:
        logging.error(f"[Ollama] Error extrayendo entrevistado: {repr(e)} | Texto: {texto[:120]}...")
        return None

# ============================================================================
# FUNCIONES DE DETECCIÓN FACTOR POLÍTICO
# ============================================================================

def detectar_factor_politico_con_ollama(texto):
    """
    Detecta si la noticia tiene contenido político (elecciones, campaña, candidatos).
    """
    prompt = (
        "Analizá el siguiente texto y determiná si tiene FACTOR POLÍTICO.\n\n"
        "CRITERIO PARA CONSIDERARLO POLÍTICO:\n"
        "- Menciona elecciones, campaña electoral, candidatos políticos\n"
        "- Habla de encuestas electorales o medición de candidatos\n"
        "- Se refiere a procesos electorales, votaciones, partidos políticos\n"
        "- Contenido relacionado con campañas políticas o propaganda electoral\n\n"
        "IMPORTANTE:\n"
        "- Si NO menciona estos temas, es NO POLÍTICO\n"
        "- Respondé únicamente con SI o NO\n"
        "- NO agregues explicaciones ni texto adicional\n\n"
        f"TEXTO A ANALIZAR:\n{texto}\n"
    )
    
    data = {"model": MODELO_OLLAMA, "prompt": prompt, "stream": False, "options": {"temperature": 0}}
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        result = response.json()
        salida = result.get("response", "").strip().upper()
        
        if salida in ["SI", "SÍ"]:
            return "SI"
        elif salida in ["NO"]:
            return "NO"
        else:
            # Validación adicional por palabras clave
            if any(palabra in salida for palabra in ["ELECCION", "CANDIDAT", "CAMPAÑA", "ENCUESTA", "VOTACION", "PARTIDO", "POLITIC"]):
                return "SI"
            else:
                return "NO"
                
    except Exception as e:
        logging.error(f"[Ollama] Error detectando factor político: {repr(e)} | Texto: {texto[:120]}...")
        return "NO"

