import pandas as pd
import Z_Utils as Z
import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import time
from datetime import timedelta

#CONFIG
CAMPOS_FIJOS = [
    'TITULO', 'TIPO PUBLICACION', 'FECHA', 'SOPORTE', 'MEDIO','SECCION',
    'AUTOR', 'ENTREVISTADO', 'TEMA', 'LINK', 'HTML_OBJ', 'ALCANCE', 'COTIZACION', 'VALORACION',
    'FACTOR POLITICO','GESTION','TEXTO_PLANO', 'CRISIS', 'MENCION_1','MENCION_2','MENCION_3','MENCION_4','MENCION_5',
    'USR_CREADOR', 'USR_REVISOR'
]

EXCEL_URL_PATH = "DataCollected/Import_Links_Procesado_Completo.xlsx"
EXPORT_PATH = "Data_Results/Batch_URLS_Procesadas.xlsx"
HISTORICO_PATH = "DataCollected/noticias_historicas.xlsx"  # Archivo histórico para crisis
OLLAMA_URL = "http://localhost:11434/api/generate"




#TODO todo esto ahora HardCodeado luego deberá ser posible configurar en tiempo ejecución
MINISTRO = "Gabriela Ricardes"
MINISTERIO = "Ministerio de Cultura"
LISTA_MENCIONES = [MINISTERIO,"Ministra de Cultura", MINISTRO,"Jorge Macri"]
MAX_MENCIONES = 5
USUARIO_CREADOR = 'LUNA'
USUARIO_REVISOR = 'SOL'

GPT_ACTIVE = False   #ACTIVAR O NO EL GPT (Fallback en su defecto)
 

TEMAS_FIJOS = ["Actividades programadas"]
LISTA_TEMAS = TEMAS_FIJOS + [
    "¡URGENTE!",
    "Recorrido por eventos y estrenos",
    "Campaña Solidaria",
    "Apertura Temporada del Ballet 2025",
    "Mecenazgo",
    "Jubilaciones bailarines del Teatro Colón",
    "Homenaje a Sara Facio",
    "Gestión cultural del GCBA",
    "Homenaje a Esperando la Carroza",
    "Casa Oliverio Girondo",
    "Anuncio de obras CCGSM"
]

## 
LIMITE_TEXTO = 14900 #Mas de este valor, parece volverse loca la IA - Ollama. (Caracteres)





#Medición tiempo de ejecución
t0 = time.time()

# 0. Levantar Logger
Z.setup_logger('Procesamiento_Noticias.log')

print(f"Procesando Noticias")

# 1. Configurar df
df = pd.DataFrame(columns=CAMPOS_FIJOS)
df['LINK'] = Z.obtener_links_del_usuario_desde_excel(EXCEL_URL_PATH)

# 2. EXTRAER TEXTO PLANO PARA CADA LINK SUBIDO POR EL USER.
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

# ============================================================================
# 4 Inferencias con el módulo de IA (OLLAMA/GPT)
# ============================================================================

# Clasificación unificada de tipo de publicación con orden de prioridad
df['TIPO PUBLICACION'] = df['TEXTO_PLANO'].apply(lambda x: Z.marcar_o_valorar_con_ia(x, lambda t: Oll.clasificar_tipo_publicacion_unificado(t, MINISTRO), LIMITE_TEXTO))

# FACTOR POLITICO - Detectar si la noticia tiene contenido político (elecciones, campaña, candidatos)
df['FACTOR POLITICO'] = df['TEXTO_PLANO'].apply(lambda x: Z.marcar_o_valorar_con_ia(x, Oll.detectar_factor_politico_con_ollama, LIMITE_TEXTO))

# 5. Inferencias con IA unificada - VALORACION (GPT + Ollama + Heurística según GPT_ACTIVE)
df['VALORACION'] = df['TEXTO_PLANO'].apply(lambda x: Z.marcar_o_valorar_con_ia(x, lambda t: Gpt.valorar_con_ia(t, ministro=MINISTRO, ministerio=MINISTERIO, gpt_active=GPT_ACTIVE), LIMITE_TEXTO))

# Clasificación de temas: heurísticas + IA + fallback por tipo publicación (Agenda → Actividades programadas)
df['TEMA'] = df.apply(lambda row: Oll.matchear_tema_con_fallback(row['TEXTO_PLANO'], LISTA_TEMAS, row['TIPO PUBLICACION']), axis=1)

# 6. Extraer ENTREVISTADO usando IA (solo para TIPO PUBLICACION = "Entrevista")
df['ENTREVISTADO'] = df.apply(lambda row: Oll.extraer_entrevistado_con_ollama(row['TEXTO_PLANO']) if row['TIPO PUBLICACION'] == 'Entrevista' else None, axis=1)

# 7. Detectar CRISIS basándose en 5+ noticias del mismo tema con valoración NEGATIVA
df = Z.procesar_crisis_con_historico(df, HISTORICO_PATH, TEMAS_FIJOS)

# 8. Detectar MENCIONES de palabras clave HOY EN DIA, HASTA 5 CAMPOS. 
df = Z.buscar_menciones(df, LISTA_MENCIONES, MAX_MENCIONES)

# 9. Asignar USUARIO_CREADOR y USUARIO_REVISOR (en el futuro vendrán de la sesión)
df['USUARIO_CREADOR'] = USUARIO_CREADOR
df['USUARIO_REVISOR'] = USUARIO_REVISOR

## Export Final a excel (Luego será a BD, o lo que se necesite)
# Descarto la columna HTML_OBJ, ya no tiene uso para el usuario final.
df.drop(columns=['HTML_OBJ'], inplace=True)
Z.exportar_df_a_excel(df, EXPORT_PATH)

#Medición del tiempo de ejecución final
t1 = time.time()
tiempo_total = str(timedelta(seconds=int(t1 - t0)))
print(f"Tiempo total de ejecución: {tiempo_total}")

#TODO campos faltantes a MEJORAR:  "TIPO PUBLICACION", 'TEMA',
#TODO campos que VUELEN probablemente: 'ETIQUETA_1','ETIQUETA_2','TAPA','AREA',''CONDUCTOR','EJE COMUNICACIONAL',
#TODO campos a AGREGAR: """Campo(s)Custom""" 
#TODO campos a TESTEAR correctamente: "VALORACION", "Seccion", 'CRISIS','AUTOR',FACTOR POLITICO

#TODO AGENDA: puede haber algo... cuando es Agenda (suelen ser muy largas a veces, es Neutra o POS, nunca NEG)
#TODO CRISIS: bien parece, pero recordar en el futuro integrar con BD para recuperar el HISTORICO DE NOTICIAS

