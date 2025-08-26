#!/usr/bin/env python3
"""
Script para extraer texto plano de URLs de agenda (SÍ y NO) para análisis comparativo
"""

import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Z_Utils import get_texto_plano_from_link

def extraer_textos_agenda():
    """Extrae texto plano de todas las URLs de agenda para análisis comparativo"""
    
    # URLs que SÍ son agenda
    urls_si_agenda = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24347481",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196084",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24185308",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24257893",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23662034",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595633",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595797"
    ]
    
    # URLs que NO son agenda
    urls_no_agenda = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24069245",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24136111",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24049682",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23932884",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23370658",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23432671"
    ]
    
    # Archivo de salida
    output_file = "textos_agenda_comparativo.txt"
    
    print("🚀 Iniciando extracción de textos para análisis comparativo de agenda...")
    print(f"📊 URLs que SÍ son agenda: {len(urls_si_agenda)}")
    print(f"📊 URLs que NO son agenda: {len(urls_no_agenda)}")
    print("=" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Escribir encabezado
        f.write("TEXTOS COMPARATIVOS PARA ANÁLISIS DE AGENDA\n")
        f.write("=" * 80 + "\n\n")
        
        # Procesar URLs que SÍ son agenda
        f.write("🔵 SECCIÓN 1: URLs que SÍ son agenda\n")
        f.write("=" * 50 + "\n\n")
        
        for i, url in enumerate(urls_si_agenda, 1):
            print(f"📰 Procesando agenda SÍ #{i}: {url}")
            
            try:
                texto = get_texto_plano_from_link(url)
                if texto:
                    f.write(f"--- AGENDA SÍ #{i} ---\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"TEXTO:\n{texto}\n")
                    f.write("-" * 80 + "\n\n")
                    print(f"✅ Texto extraído: {len(texto)} caracteres")
                else:
                    print(f"❌ No se pudo extraer texto de: {url}")
                    f.write(f"--- AGENDA SÍ #{i} ---\n")
                    f.write(f"URL: {url}\n")
                    f.write("ERROR: No se pudo extraer texto\n")
                    f.write("-" * 80 + "\n\n")
            except Exception as e:
                print(f"❌ Error procesando {url}: {e}")
                f.write(f"--- AGENDA SÍ #{i} ---\n")
                f.write(f"URL: {url}\n")
                f.write(f"ERROR: {e}\n")
                f.write("-" * 80 + "\n\n")
        
        # Separador entre secciones
        f.write("\n" + "=" * 80 + "\n\n")
        
        # Procesar URLs que NO son agenda
        f.write("🔴 SECCIÓN 2: URLs que NO son agenda\n")
        f.write("=" * 50 + "\n\n")
        
        for i, url in enumerate(urls_no_agenda, 1):
            print(f"📰 Procesando agenda NO #{i}: {url}")
            
            try:
                texto = get_texto_plano_from_link(url)
                if texto:
                    f.write(f"--- AGENDA NO #{i} ---\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"TEXTO:\n{texto}\n")
                    f.write("-" * 80 + "\n\n")
                    print(f"✅ Texto extraído: {len(texto)} caracteres")
                else:
                    print(f"❌ No se pudo extraer texto de: {url}")
                    f.write(f"--- AGENDA NO #{i} ---\n")
                    f.write(f"URL: {url}\n")
                    f.write("ERROR: No se pudo extraer texto\n")
                    f.write("-" * 80 + "\n\n")
            except Exception as e:
                print(f"❌ Error procesando {url}: {e}")
                f.write(f"--- AGENDA NO #{i} ---\n")
                f.write(f"URL: {url}\n")
                f.write(f"ERROR: {e}\n")
                f.write("-" * 80 + "\n\n")
        
        # Escribir resumen
        f.write("\n" + "=" * 80 + "\n")
        f.write("RESUMEN DEL ANÁLISIS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total URLs que SÍ son agenda: {len(urls_si_agenda)}\n")
        f.write(f"Total URLs que NO son agenda: {len(urls_no_agenda)}\n")
        f.write(f"Total URLs procesadas: {len(urls_si_agenda) + len(urls_no_agenda)}\n")
        f.write("Archivo generado para análisis comparativo del prompt de es_agenda_gpt\n")
    
    print(f"\n✅ Análisis completado!")
    print(f"📁 Archivo generado: {output_file}")
    print(f"📊 Total de URLs procesadas: {len(urls_si_agenda) + len(urls_no_agenda)}")
    print("\n🎯 Ahora puedes revisar el archivo para analizar las diferencias")
    print("   y ajustar el prompt de es_agenda_gpt según sea necesario")

if __name__ == "__main__":
    extraer_textos_agenda()
