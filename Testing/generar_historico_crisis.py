import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generar_historico_crisis():
    """
    Genera un archivo Excel con datos históricos para testing de crisis.
    Crea noticias con diferentes temas y valoraciones para probar la detección.
    """
    
    # Configuración
    temas_test = [
        "¡URGENTE!",
        "Recorrido por eventos y estrenos", 
        "Campaña Solidaria",
        "Mecenazgo",
        "Jubilaciones bailarines del Teatro Colón",
        "Homenaje a Sara Facio",
        "Gestión cultural del GCBA",
        "Homenaje a Esperando la Carroza",
        "Casa Oliverio Girondo",
        "Anuncio de obras CCGSM"
    ]
    
    # Crear datos de prueba
    datos = []
    fecha_base = datetime.now() - timedelta(days=30)
    
    # Tema 1: CRISIS (6 noticias NEGATIVAS)
    for i in range(6):
        datos.append({
            'TITULO': f'Noticia crítica {i+1} - Tema Urgente',
            'TEXTO_PLANO': f'Texto de noticia crítica número {i+1} sobre tema urgente',
            'TEMA': '¡URGENTE!',
            'VALORACION': 'NEGATIVO',
            'FECHA': fecha_base + timedelta(days=i),
            'LINK': f'https://ejemplo.com/urgente_{i+1}',
            'MEDIO': 'Test Medio',
            'SOPORTE': 'Digital'
        })
    
    # Tema 2: CRISIS (5 noticias NEGATIVAS)
    for i in range(5):
        datos.append({
            'TITULO': f'Problema Mecenazgo {i+1}',
            'TEXTO_PLANO': f'Texto sobre problemas en mecenazgo número {i+1}',
            'TEMA': 'Mecenazgo',
            'VALORACION': 'NEGATIVO',
            'FECHA': fecha_base + timedelta(days=i+10),
            'LINK': f'https://ejemplo.com/mecenazgo_{i+1}',
            'MEDIO': 'Test Medio',
            'SOPORTE': 'Digital'
        })
    
    # Tema 3: NO CRISIS (3 noticias NEGATIVAS - menos de 5)
    for i in range(3):
        datos.append({
            'TITULO': f'Problema Ballet {i+1}',
            'TEXTO_PLANO': f'Texto sobre problemas en ballet número {i+1}',
            'TEMA': 'Jubilaciones bailarines del Teatro Colón',
            'VALORACION': 'NEGATIVO',
            'FECHA': fecha_base + timedelta(days=i+20),
            'LINK': f'https://ejemplo.com/ballet_{i+1}',
            'MEDIO': 'Test Medio',
            'SOPORTE': 'Digital'
        })
    
    # Tema 4: NO CRISIS (mezcla de valoraciones)
    for i in range(6):
        valoracion = 'NEGATIVO' if i < 3 else 'NO_NEGATIVO'
        datos.append({
            'TITULO': f'Noticia Sara Facio {i+1}',
            'TEXTO_PLANO': f'Texto sobre Sara Facio número {i+1}',
            'TEMA': 'Homenaje a Sara Facio',
            'VALORACION': valoracion,
            'FECHA': fecha_base + timedelta(days=i+25),
            'LINK': f'https://ejemplo.com/sara_{i+1}',
            'MEDIO': 'Test Medio',
            'SOPORTE': 'Digital'
        })
    
    # Tema 5: Tema fijo (no debe ser crisis)
    for i in range(10):
        datos.append({
            'TITULO': f'Actividad programada {i+1}',
            'TEXTO_PLANO': f'Texto sobre actividad programada número {i+1}',
            'TEMA': 'Actividades programadas',
            'VALORACION': 'NEGATIVO',
            'FECHA': fecha_base + timedelta(days=i+30),
            'LINK': f'https://ejemplo.com/actividad_{i+1}',
            'MEDIO': 'Test Medio',
            'SOPORTE': 'Digital'
        })
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Crear directorio si no existe
    os.makedirs('DataCollected', exist_ok=True)
    
    # Guardar archivo histórico
    historico_path = 'DataCollected/noticias_historicas.xlsx'
    df.to_excel(historico_path, index=False)
    
    print(f"✅ Archivo histórico creado: {historico_path}")
    print(f"📊 Resumen de datos:")
    print(f"   - Total noticias: {len(df)}")
    print(f"   - Temas en crisis esperados: ¡URGENTE! (6 NEG), Mecenazgo (5 NEG)")
    print(f"   - Temas NO crisis: Jubilaciones (3 NEG), Sara Facio (3 NEG + 3 POS)")
    print(f"   - Tema fijo excluido: Actividades programadas (10 NEG)")
    
    return historico_path

if __name__ == "__main__":
    generar_historico_crisis() 