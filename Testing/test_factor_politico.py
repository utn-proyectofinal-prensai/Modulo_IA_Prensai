import pandas as pd
import O_Utils_Ollama as Oll
import Z_Utils as Z
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_factor_politico():
    """
    Script de prueba para verificar la funcionalidad del campo FACTOR POLITICO
    """
    print("🧪 PROBANDO CAMPO FACTOR POLITICO")
    print("=" * 50)
    
    # Configurar logger
    Z.setup_logger('test_factor_politico.log')
    
    # Cargar datos de prueba
    try:
        df = pd.read_excel("DataCollected/Import_Links_Procesado_Completo.xlsx")
        print(f"✅ Datos cargados: {len(df)} noticias")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return
    
    # Tomar solo las primeras 5 noticias para prueba rápida
    df_test = df.head(5).copy()
    
    # Procesar texto plano y extraer FACTOR POLITICO
    print("\n📋 Procesando texto plano y extrayendo FACTOR POLITICO...")
    df_test['TEXTO_PLANO'] = df_test['LINK'].apply(Z.get_texto_plano_from_link)
    df_test['FACTOR POLITICO'] = df_test['TEXTO_PLANO'].apply(Oll.detectar_factor_politico_con_ollama)
    
    # Mostrar resultados
    print("\n📊 RESULTADOS:")
    print("-" * 50)
    
    politicas = df_test[df_test['FACTOR POLITICO'] == 'SI']
    no_politicas = df_test[df_test['FACTOR POLITICO'] == 'NO']
    
    print(f"🗳️ Políticas: {len(politicas)} noticias")
    print(f"📰 No políticas: {len(no_politicas)} noticias")
    
    if len(politicas) > 0:
        print("\n🎯 NOTICIAS POLÍTICAS:")
        for idx, row in politicas.iterrows():
            print(f"  • Link: {row['LINK']}")
            print(f"    Título: {row.get('TITULO', 'N/A')}")
            print()
    
    # Mostrar ejemplos de texto para verificar
    print("\n📝 EJEMPLOS DE TEXTO:")
    print("-" * 30)
    for idx, row in df_test.iterrows():
        print(f"Noticia {idx + 1}:")
        print(f"Factor: {row['FACTOR POLITICO']}")
        print(f"Texto: {row['TEXTO_PLANO'][:200]}...")
        print("-" * 30)
    
    # Guardar resultados
    output_path = "Testing/resultados_test_factor_politico.xlsx"
    df_test[['LINK', 'TITULO', 'FACTOR POLITICO', 'TEXTO_PLANO']].to_excel(output_path, index=False)
    print(f"💾 Resultados guardados en: {output_path}")
    
    print("\n✅ Prueba completada!")

if __name__ == "__main__":
    test_factor_politico() 