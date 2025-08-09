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

def valorar_noticia_con_ollama(texto, ministro=None, ministerio=None):
    """
    Valora noticias con Ollama y aplica heurística para POSITIVA/NEUTRA.
    """
    valoracion_base = valorar_noticia_con_ollama_base(texto)
    
    if valoracion_base == "NEGATIVA":
        return "NEGATIVA"
    elif valoracion_base == "NO_NEGATIVA":
        # Aplicar heurística para POSITIVA/NEUTRA
        if (ministro or ministerio):
            return Z.aplicar_heuristica_valoracion(valoracion_base, texto, ministro, ministerio)
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

def es_declaracion_ollama(texto, ministro_actual):
    """
    Detecta si es una DECLARACIÓN usando Ollama: nota con cita SÍ O SÍ atribuida al MINISTRO.
    """
    if not texto or pd.isnull(texto):
        return False
    
    prompt = (
        "¿El siguiente texto es una DECLARACIÓN del ministro?\n\n"
        "CRITERIOS PARA CONSIDERARLO DECLARACIÓN:\n"
        "- Debe tener CITA (comillas) atribuida al ministro\n"
        "- Debe mencionar al MINISTRO de Cultura\n"
        "- Debe contener verbos de decir/acción (dijo, anunció, presentó, etc.)\n"
        "- El ministro debe ser el que habla o actúa\n\n"
        "EJEMPLOS DE DECLARACIÓN:\n"
        "- 'Estamos trabajando...', dijo el ministro\n"
        "- El ministro anunció: 'Vamos a...'\n"
        "- Gabriela Ricardes presentó el programa\n\n"
        "EJEMPLOS DE NO DECLARACIÓN:\n"
        "- Se presentó un programa (sin ministro)\n"
        "- El programa incluye... (sin cita)\n"
        "- Se inauguró el teatro (sin ministro)\n\n"
        f"MINISTRO: {ministro_actual}\n"
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

def es_nota_opinion_ollama(texto, ministro_actual, autor=None):
    """
    Detecta si es una NOTA DE OPINIÓN usando Ollama: firmada por el ministro.
    """
    if not texto or pd.isnull(texto):
        return False
    
    prompt = (
        "¿El siguiente texto es una NOTA DE OPINIÓN del ministro?\n\n"
        "CRITERIOS PARA CONSIDERARLO NOTA DE OPINIÓN:\n"
        "- Debe estar firmada por el MINISTRO de Cultura\n"
        "- Es una opinión personal del ministro, no un comunicado\n"
        "- Puede incluir 'por el ministro de cultura' o el nombre del ministro\n"
        "- Es un texto de opinión, no informativo\n\n"
        "EJEMPLOS DE NOTA DE OPINIÓN:\n"
        "- 'Por Gabriela Ricardes, ministra de Cultura'\n"
        "- 'El ministro opina sobre...'\n"
        "- 'Por el ministro de cultura: mi visión sobre...'\n\n"
        "EJEMPLOS DE NO NOTA DE OPINIÓN:\n"
        "- Comunicado oficial\n"
        "- Noticia informativa\n"
        "- Declaración en rueda de prensa\n\n"
        f"MINISTRO: {ministro_actual}\n"
        f"AUTOR: {autor if autor else 'No especificado'}\n"
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
        logging.error(f"[Ollama] Error detectando nota de opinión: {repr(e)} | Texto: {texto[:120]}...")
        return False  # Fallback conservador

def clasificar_tipo_publicacion_unificado(texto, ministro_actual="Gabriela Ricardes"):
    """
    Clasifica el tipo de publicación con orden de prioridad:
    1. Agenda (más frecuente)
    2. Entrevista (formato distintivo)
    3. Declaración (citas específicas)
    4. Nota de opinión (muy rara, <1%)
    5. Nota (default)
    
    Args:
        texto (str): Texto plano de la noticia
        ministro_actual (str): Nombre del ministro actual
    
    Returns:
        str: Tipo de publicación clasificado
    """
    try:
        # Verificar e informar estado del servicio la primera vez
        _verificar_e_imprimir_estado_ollama()

        if not texto or pd.isnull(texto):
            return "Nota"
        
        # 1. PRIORIDAD ALTA: Agenda (más frecuente, regla clara)
        if es_agenda_ollama(texto):
            logging.info(f"Clasificado como Agenda")
            return "Agenda"
        
        # 2. PRIORIDAD MEDIA: Entrevista (formato distintivo)
        if es_entrevista_ollama(texto):
            logging.info(f"Clasificado como Entrevista")
            return "Entrevista"
        
        # 3. PRIORIDAD MEDIA: Declaración (citas específicas)
        if es_declaracion_ollama(texto, ministro_actual):
            logging.info(f"Clasificado como Declaración")
            return "Declaración"
        
        # 4. PRIORIDAD BAJA: Nota de opinión (muy rara, <1%)
        if es_nota_opinion_ollama(texto, ministro_actual):
            logging.info(f"Clasificado como Nota de opinión")
            return "Nota de opinión"
        
        # 5. DEFAULT: Nota (lo que no cabe claramente en otras categorías)
        logging.info(f"Clasificado como Nota (default)")
        return "Nota"
        
    except Exception as e:
        logging.error(f"Error al clasificar tipo de publicación: {e}")
        return "Nota"  # Fallback seguro

# ============================================================================
# FUNCIONES DE CLASIFICACIÓN DE TEMAS
# ============================================================================

def matchear_tema_con_fallback(texto, lista_temas, tipo_publicacion=None, fecha_noticia=None, tema_a_fecha=None):
    """
    Clasifica una noticia en un tema específico usando heurísticas + IA + fallback.
    
    Args:
        texto (str): Texto plano de la noticia
        lista_temas (list): Lista de temas disponibles
        tipo_publicacion (str): Tipo de publicación (para fallback)
    
    Returns:
        str: Tema asignado o "Revisar Manual"
    """
    if not texto or not lista_temas:
        return "Revisar Manual"
    """
    # 1. Heurísticas muy estrictas para coincidencias exactas
    texto_lower = texto.lower()
    for tema in lista_temas:
        tema_lower = tema.lower()
        # Solo coincidencia exacta o muy cercana
        if tema_lower in texto_lower or texto_lower.count(tema_lower) > 0:
            return tema
    """
    # 2. Fallback por tipo de publicación
    if tipo_publicacion == "Agenda":
        return "Actividades programadas"
    
    # 3. Consulta a IA (con conocimiento opcional de fechas)
    return _consulta_ollama_tema(texto, lista_temas, fecha_noticia=fecha_noticia, tema_a_fecha=tema_a_fecha)


def matchear_tema_sin_fecha(texto, lista_temas, tipo_publicacion=None):
    """
    Variante histórica sin considerar fechas para desempate. Útil para comparar accuracy.
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

    # 3. Consulta a IA sin señales temporales
    return _consulta_ollama_tema(texto, lista_temas)

def _consulta_ollama_tema(texto, lista_temas, fecha_noticia=None, tema_a_fecha=None):
    """
    Consulta a Ollama para clasificar el tema usando estrategia de eliminación + contexto temporal opcional.
    - fecha_noticia: str o datetime con formato ISO 'YYYY-MM-DD' cuando esté disponible
    - tema_a_fecha: dict opcional {tema: 'YYYY-MM-DD'} con fecha de carga del tema
    """
    # Normalizar fecha noticia
    noticia_dt = None
    if fecha_noticia:
        try:
            noticia_dt = fecha_noticia if isinstance(fecha_noticia, datetime) else datetime.fromisoformat(str(fecha_noticia))
        except Exception:
            noticia_dt = None

    # Construir lista textual completa de temas (lista cerrada de elegibles)
    temas_str = "\n".join([f"- {t}" for t in lista_temas])

    # Calcular top-k cercanos por fecha (contexto no restrictivo)
    contexto_temporal = []
    if tema_a_fecha and noticia_dt:
        def distancia_dias(tema):
            try:
                f = tema_a_fecha.get(tema)
                if not f:
                    return 999999
                dt = f if isinstance(f, datetime) else datetime.fromisoformat(str(f))
                return abs((dt - noticia_dt).days)
            except Exception:
                return 999999

        candidatos_ordenados = sorted(lista_temas, key=distancia_dias)
        # Tomar solo aquellos con fecha válida
        top_con_fecha = [t for t in candidatos_ordenados if tema_a_fecha.get(t)]
        for t in top_con_fecha[:7]:
            contexto_temporal.append(f"- {t} (fecha_carga: {tema_a_fecha[t]})")

    contexto_str = "\n".join(contexto_temporal) if contexto_temporal else "(sin datos temporales relevantes)"

    # Armar prompt con contexto temporal no restrictivo
    prompt = (
        f"Asigná UNO y solo UNO de los siguientes temas a la noticia (lista cerrada):\n{temas_str}\n\n"
        "REGLAS DE DECISIÓN (aplicá en este orden):\n"
        "A) Coincidencia literal: si el nombre de un tema de la lista aparece en el TÍTULO o CUERPO (sin sensibilidad a mayúsculas/acentos y tolerando signos como °), elegí ese tema.\n"
        "B) Múltiples coincidencias: elegí el MÁS ESPECÍFICO (el texto más largo) o el que aparezca en el TÍTULO.\n"
        "C) Sin coincidencia literal: podés elegir un tema por PARÁFRASIS solo si la evidencia es inequívoca (mismo evento/proyecto reconocido). Si hay dudas, NO arriesgues.\n"
        "D) Contexto temporal NO RESTRICTIVO (abajo): si estás entre 2-3 opciones y ninguna tiene evidencia textual clara, PREFERÍ uno de los temas listados en el contexto temporal (por ser recientes). Si hay coincidencia literal, ignorá esta preferencia.\n"
        "E) Fallback: si no hay evidencia clara de un tema concreto, asigná 'Actividades programadas - FB'.\n"
        "F) Nunca inventes ni modifiques nombres: la respuesta debe ser exactamente uno de los provistos.\n\n"
        f"Contexto temporal (no restrictivo, top recientes):\n{contexto_str}\n\n"
        "SALIDA:\n"
        "- Respondé ÚNICAMENTE con el nombre exacto de un tema de la lista.\n"
        "- Sin comentarios ni explicaciones.\n\n"
        f"TEXTO A ANALIZAR:\n{texto}\n"
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
            return "Actividades programadas - FB"  # Fallback
            
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

