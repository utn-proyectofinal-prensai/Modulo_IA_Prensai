"""
Test específico para la función de clasificación de temas
Lee datos de la hoja "TEMA" del Excel y valida la precisión de la función matchear_tema
"""

import sys
import os
# Agregar el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import O_Utils_Ollama as Oll
import Z_Utils as Z
import time
from datetime import timedelta

# Configuración
EXCEL_URL_PATH = "Testing/datos_test_300.xlsx"

def cargar_temas_reales():
    """
    Carga los temas reales del archivo temas_300.txt
    """
    try:
        with open("Testing/temas_300.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Extraer temas (después de "EVENTO / TEMA")
        lineas = contenido.split('\n')
        temas = []
        empezar_extraccion = False
        
        for linea in lineas:
            linea = linea.strip()
            if linea == "EVENTO / TEMA":
                empezar_extraccion = True
                continue
            elif linea == "]" or linea == "LISTA = [":
                continue
            elif empezar_extraccion and linea:
                temas.append(linea)
        
        # Obtener temas únicos
        temas_unicos = list(set(temas))
        temas_unicos.sort()
        
        print(f"📋 Temas reales cargados: {len(temas_unicos)} temas únicos")
        return temas_unicos
        
    except Exception as e:
        print(f"❌ Error cargando temas reales: {e}")
        # Fallback a lista básica si hay error
        return ["Actividades programadas", "Mecenazgo", "¡URGENTE!"]

# Cargar temas reales del archivo
LISTA_TEMAS = cargar_temas_reales()

def cargar_datos_test():
    """
    Carga los datos del Excel de testing (ya procesado con texto plano)
    """
    try:
        print("Cargando datos del Excel de testing...")
        df = pd.read_excel(EXCEL_URL_PATH)
        print(f"✅ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        # Verificar que tenemos las columnas necesarias
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        
        # El texto plano ya está procesado, no necesitamos extraerlo
        print(f"✅ Texto plano ya incluido para {len(df)} noticias")
        return df
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return None

def aplicar_funcion_temas(df):
    """
    Aplica la función matchear_tema_con_fallback a cada texto
    """
    print("Aplicando función de clasificación de temas con fallback...")
    t0 = time.time()
    
    # Aplicar función a cada texto (simulando diferentes TIPO PUBLICACION para testing)
    # Para testing, asumimos que todas son "Agenda" para probar el fallback
    df['TEMA_ASIGNADO'] = df['TEXTO_PLANO'].apply(
        lambda x: Oll.matchear_tema_con_fallback(x, LISTA_TEMAS, "Agenda") if pd.notna(x) else "Revisar Manual"
    )
    
    t1 = time.time()
    tiempo_total = str(timedelta(seconds=int(t1 - t0)))
    print(f"✅ Clasificación completada en {tiempo_total}")
    
    return df

def analizar_resultados(df):
    """
    Analiza los resultados y calcula métricas
    """
    print("\n" + "="*50)
    print("ANÁLISIS DE RESULTADOS")
    print("="*50)
    
    # Métricas básicas
    total_filas = len(df)
    print(f"📊 Total de noticias: {total_filas}")
    
    # Análisis de precisión - PRIMERO crear ES_CORRECTO
    print(f"\n🎯 PRECISIÓN:")
    
    # Comparar con tema humano
    if 'EVENTO / TEMA' in df.columns:
        print("✅ Columna 'EVENTO / TEMA' encontrada - calculando precisión...")
        df['ES_CORRECTO'] = df['TEMA_ASIGNADO'].str.replace(' - H', '').str.replace(' - IA', '').str.replace(' - Fallback', '') == df['EVENTO / TEMA']
        
        correctos = df[df['ES_CORRECTO'] == True]
        incorrectos = df[df['ES_CORRECTO'] == False]
        
        print(f"   • Correctos: {len(correctos)} ({len(correctos)/total_filas*100:.1f}%)")
        print(f"   • Incorrectos: {len(incorrectos)} ({len(incorrectos)/total_filas*100:.1f}%)")
        
        # AHORA separar por tipo de clasificación (después de crear ES_CORRECTO)
        heuristicas = df[df['TEMA_ASIGNADO'].str.contains(' - H', na=False)]
        ia_clasificaciones = df[df['TEMA_ASIGNADO'].str.contains(' - IA', na=False)]
        fallback_clasificaciones = df[df['TEMA_ASIGNADO'].str.contains(' - Fallback', na=False)]
        revisar_manual = df[df['TEMA_ASIGNADO'] == 'Revisar Manual']
        
        print(f"\n🔍 CLASIFICACIONES:")
        print(f"   • Heurísticas: {len(heuristicas)} ({len(heuristicas)/total_filas*100:.1f}%)")
        print(f"   • IA: {len(ia_clasificaciones)} ({len(ia_clasificaciones)/total_filas*100:.1f}%)")
        print(f"   • Fallback: {len(fallback_clasificaciones)} ({len(fallback_clasificaciones)/total_filas*100:.1f}%)")
        print(f"   • Revisar Manual: {len(revisar_manual)} ({len(revisar_manual)/total_filas*100:.1f}%)")
        
        # ANÁLISIS ESPECÍFICO: Revisar Manual vs Actividades programadas
        print(f"\n🔍 ANÁLISIS 'REVISAR MANUAL':")
        if len(revisar_manual) > 0:
            revisar_manual_actividades = revisar_manual[revisar_manual['EVENTO / TEMA'] == 'Actividades programadas']
            print(f"   • 'Revisar Manual' que deberían ser 'Actividades programadas': {len(revisar_manual_actividades)}")
            print(f"   • Porcentaje: {len(revisar_manual_actividades)/len(revisar_manual)*100:.1f}% de 'Revisar Manual'")
        else:
            print(f"   • No hay casos de 'Revisar Manual' - ¡Excelente!")
        
        # Precisión por tipo
        if len(heuristicas) > 0:
            h_correctas = heuristicas[heuristicas['ES_CORRECTO'] == True]
            precision_h = len(h_correctas) / len(heuristicas) * 100
            print(f"   • Precisión Heurísticas: {precision_h:.1f}%")
        
        if len(ia_clasificaciones) > 0:
            ia_correctas = ia_clasificaciones[ia_clasificaciones['ES_CORRECTO'] == True]
            precision_ia = len(ia_correctas) / len(ia_clasificaciones) * 100
            print(f"   • Precisión IA: {precision_ia:.1f}%")
    else:
        print("❌ Columna 'EVENTO / TEMA' NO encontrada - no se puede calcular precisión")
        print("   Columnas disponibles:", list(df.columns))
        
        # Si no hay columna de precisión, solo mostrar clasificaciones
        heuristicas = df[df['TEMA_ASIGNADO'].str.contains(' - H', na=False)]
        ia_clasificaciones = df[df['TEMA_ASIGNADO'].str.contains(' - IA', na=False)]
        revisar_manual = df[df['TEMA_ASIGNADO'] == 'Revisar Manual']
        
        print(f"\n🔍 CLASIFICACIONES:")
        print(f"   • Heurísticas: {len(heuristicas)} ({len(heuristicas)/total_filas*100:.1f}%)")
        print(f"   • IA: {len(ia_clasificaciones)} ({len(ia_clasificaciones)/total_filas*100:.1f}%)")
        print(f"   • Revisar Manual: {len(revisar_manual)} ({len(revisar_manual)/total_filas*100:.1f}%)")
    
    # Análisis de temas más asignados
    print(f"\n📈 TEMAS MÁS ASIGNADOS:")
    temas_counts = df['TEMA_ASIGNADO'].value_counts()
    for tema, count in temas_counts.head(10).items():
        print(f"   • {tema}: {count} veces")
    
    return df

def mostrar_ejemplos(df, n_ejemplos=5):
    """
    Muestra ejemplos de clasificaciones correctas e incorrectas
    """
    print(f"\n📋 EJEMPLOS (primeros {n_ejemplos}):")
    print("-" * 80)
    
    if 'EVENTO / TEMA' in df.columns:
        for i, row in df.head(n_ejemplos).iterrows():
            texto_corto = str(row.get('TEXTO_PLANO', ''))[:100] + "..."
            tema_asignado = row.get('TEMA_ASIGNADO', 'N/A')
            tema_humano = row.get('EVENTO / TEMA', 'N/A')
            es_correcto = "✅" if row.get('ES_CORRECTO', False) else "❌"
            
            print(f"{es_correcto} Texto: {texto_corto}")
            print(f"    Asignado: {tema_asignado}")
            print(f"    Humano: {tema_humano}")
            print()

def exportar_resultados(df):
    """
    Exporta los resultados a Excel
    """
    output_path = "Data_Results/Test_Temas_Resultados.xlsx"
    try:
        df.to_excel(output_path, index=False)
        print(f"✅ Resultados exportados a: {output_path}")
    except Exception as e:
        print(f"❌ Error al exportar: {e}")

def main():
    """
    Función principal del test
    """
    print("🧪 INICIANDO TEST DE CLASIFICACIÓN DE TEMAS")
    print("="*50)
    
    # 1. Cargar datos
    df = cargar_datos_test()
    if df is None:
        return
    
    # 2. Aplicar función de temas
    df = aplicar_funcion_temas(df)
    
    # 3. Analizar resultados
    df = analizar_resultados(df)
    
    # 4. Mostrar ejemplos
    mostrar_ejemplos(df)
    
    # 5. Exportar resultados
    exportar_resultados(df)
    
    print("\n🎉 Test completado!")

if __name__ == "__main__":
    main() 