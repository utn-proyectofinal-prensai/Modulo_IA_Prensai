import pandas as pd
import Z_Utils as Z
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gestion():
    """
    Script de prueba para verificar la funcionalidad del campo GESTION
    """
    print("🧪 PROBANDO CAMPO GESTION")
    print("=" * 50)
    
    # Configurar logger
    Z.setup_logger('test_gestion.log')
    
    # Cargar datos de prueba
    try:
        df = pd.read_excel("DataCollected/Import_Links_Procesado_Completo.xlsx")
        print(f"✅ Datos cargados: {len(df)} noticias")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return
    
    # Tomar solo las primeras 10 noticias para prueba rápida
    df_test = df.head(10).copy()
    
    # Procesar HTML y extraer GESTION
    print("\n📋 Procesando HTML y extrayendo GESTION...")
    df_test['HTML_OBJ'] = df_test['LINK'].apply(Z.get_html_object_from_link)
    df_test['GESTION'] = df_test['HTML_OBJ'].apply(Z.get_gestion_from_html_obj)
    
    # Mostrar resultados
    print("\n📊 RESULTADOS:")
    print("-" * 50)
    
    gestionadas = df_test[df_test['GESTION'] == 'GESTIONADA']
    no_gestionadas = df_test[df_test['GESTION'] == 'NO GESTIONADA']
    
    print(f"✅ Gestionadas: {len(gestionadas)} noticias")
    print(f"❌ No gestionadas: {len(no_gestionadas)} noticias")
    
    if len(gestionadas) > 0:
        print("\n🎯 NOTICIAS GESTIONADAS:")
        for idx, row in gestionadas.iterrows():
            print(f"  • Link: {row['LINK']}")
            print(f"    Título: {row.get('TITULO', 'N/A')}")
            print()
    
    # Guardar resultados
    output_path = "Testing/resultados_test_gestion.xlsx"
    df_test[['LINK', 'TITULO', 'GESTION']].to_excel(output_path, index=False)
    print(f"💾 Resultados guardados en: {output_path}")
    
    print("\n✅ Prueba completada!")

if __name__ == "__main__":
    test_gestion() 