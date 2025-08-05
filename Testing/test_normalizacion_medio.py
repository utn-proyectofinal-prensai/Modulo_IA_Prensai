import pandas as pd
import Z_Utils as Z
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_normalizacion_medio():
    """
    Script de prueba encapsulado para verificar la normalización de medios
    Solo procesa los campos necesarios: LINK, TITULO, TEXTO_PLANO, MEDIO_ORIGINAL, MEDIO
    """
    print("🧪 PROBANDO NORMALIZACIÓN DE MEDIOS (ENCAPSULADO)")
    print("=" * 60)
    
    # Configurar logger
    Z.setup_logger('test_normalizacion_medio.log')
    
    # Cargar datos reales
    try:
        df = pd.read_excel("DataCollected/Import_Links_Procesado_Completo.xlsx")
        print(f"✅ Datos cargados: {len(df)} noticias")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return
    
    # Tomar las primeras 500 noticias para prueba con más datos
    df_test = df.head(500).copy()
    
    # Procesar solo los campos necesarios
    print("\n📋 Procesando campos necesarios...")
    
    # 1. Extraer texto plano
    df_test['TEXTO_PLANO'] = df_test['LINK'].apply(Z.get_texto_plano_from_link)
    
    # 2. Procesar HTML y extraer título y medio
    df_test['HTML_OBJ'] = df_test['LINK'].apply(Z.get_html_object_from_link)
    df_test['TITULO'] = df_test['HTML_OBJ'].apply(Z.get_titulo_from_html_obj)
    df_test['MEDIO_ORIGINAL'] = df_test['HTML_OBJ'].apply(Z.get_medio_from_html_obj)
    
    # 3. Aplicar normalización
    df_test['MEDIO'] = df_test['MEDIO_ORIGINAL'].apply(Z.normalizar_medio)
    
    # Mostrar resultados
    print("\n📊 RESULTADOS DE NORMALIZACIÓN:")
    print("-" * 60)
    
    # Contar medios únicos
    medios_originales = df_test['MEDIO_ORIGINAL'].dropna().unique()
    medios_normalizados = df_test['MEDIO'].dropna().unique()
    
    print(f"📰 Medios originales únicos: {len(medios_originales)}")
    print(f"🎯 Medios normalizados únicos: {len(medios_normalizados)}")
    print(f"📈 Reducción: {len(medios_originales) - len(medios_normalizados)} medios unificados")
    
    # Mostrar ejemplos de normalización
    print("\n🔍 EJEMPLOS DE NORMALIZACIÓN:")
    print("-" * 40)
    
    cambios_detectados = 0
    for idx, row in df_test.iterrows():
        if pd.notna(row['MEDIO_ORIGINAL']) and pd.notna(row['MEDIO']):
            original = row['MEDIO_ORIGINAL']
            normalizado = row['MEDIO']
            
            if original != normalizado:
                print(f"  • '{original}' → '{normalizado}'")
                cambios_detectados += 1
    
    if cambios_detectados == 0:
        print("  • No se detectaron cambios en la normalización")
    
    # Mostrar todos los medios únicos
    print("\n📋 TODOS LOS MEDIOS ÚNICOS:")
    print("-" * 30)
    
    print("ORIGINALES:")
    for medio in sorted(medios_originales):
        print(f"  • {medio}")
    
    print("\nNORMALIZADOS:")
    for medio in sorted(medios_normalizados):
        print(f"  • {medio}")
    
    # Guardar resultados con solo los campos necesarios
    output_path = "Testing/resultados_test_normalizacion_medio.xlsx"
    df_test[['LINK', 'TITULO', 'TEXTO_PLANO', 'MEDIO_ORIGINAL', 'MEDIO']].to_excel(output_path, index=False)
    print(f"\n💾 Resultados guardados en: {output_path}")
    
    print(f"\n✅ Prueba completada! ({cambios_detectados} cambios detectados)")

if __name__ == "__main__":
    test_normalizacion_medio() 