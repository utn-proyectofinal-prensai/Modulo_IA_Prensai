#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer textos planos de noticias que SÍ son entrevistas
para análisis manual de patrones por GPT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z

def analizar_patrones_entrevistas():
    """
    Extrae textos planos de URLs que SÍ son entrevistas y NO son entrevistas
    para análisis manual de patrones por GPT
    """
    
    # URLs que SÍ son entrevistas (confirmadas) - 20 URLs
    urls_entrevistas = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294676",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301580",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24182197",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24254500",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24137173",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23973943",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24060116",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23508102",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23282010",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22452829",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22286981",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21847212",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21865089",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=21449212",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19799678",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19662056",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19674630",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19401526",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19214812",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19307300"
    ]
    
    # URLs que NO son entrevistas (confirmadas) - 9 URLs
    urls_no_entrevistas = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24062160",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23990873",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23998611",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23994312",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24046933",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23109767",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19630894",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19306459",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19190441"
    ]
    
    print("🔍 ANALIZANDO PATRONES DE ENTREVISTAS Y NO ENTREVISTAS")
    print("=" * 80)
    print(f"Total de URLs a analizar: {len(urls_entrevistas) + len(urls_no_entrevistas)}")
    print(f"- Entrevistas: {len(urls_entrevistas)}")
    print(f"- No entrevistas: {len(urls_no_entrevistas)}")
    print("=" * 80)
    
    # Archivo de salida
    output_file = "Testing/analisis_completo_patrones.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🔍 ANÁLISIS COMPLETO DE PATRONES - ENTREVISTAS vs NO ENTREVISTAS\n")
        f.write("=" * 80 + "\n\n")
        
        # Procesar ENTREVISTAS
        f.write("📰 ENTREVISTAS CONFIRMADAS (deberían clasificar como True)\n")
        f.write("-" * 60 + "\n\n")
        
        for i, url in enumerate(urls_entrevistas, 1):
            try:
                print(f"📰 Procesando ENTREVISTA #{i}/{len(urls_entrevistas)}")
                
                # Extraer texto plano
                texto = Z.get_texto_plano_from_link(url)
                
                if texto:
                    f.write(f"ENTREVISTA #{i}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"TEXTO COMPLETO:\n{texto}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Mostrar progreso en consola
                    print(f"  ✅ Texto extraído: {len(texto)} caracteres")
                else:
                    f.write(f"ENTREVISTA #{i}\n")
                    f.write(f"URL: {url}\n")
                    f.write("❌ No se pudo extraer texto\n")
                    f.write("=" * 80 + "\n\n")
                    print(f"  ❌ No se pudo extraer texto")
                    
            except Exception as e:
                f.write(f"ENTREVISTA #{i}\n")
                f.write(f"URL: {url}\n")
                f.write(f"❌ Error: {e}\n")
                f.write("=" * 80 + "\n\n")
                print(f"  ❌ Error: {e}")
        
        # Procesar NO ENTREVISTAS
        f.write("📰 NO ENTREVISTAS (deberían clasificar como False)\n")
        f.write("-" * 60 + "\n\n")
        
        for i, url in enumerate(urls_no_entrevistas, 1):
            try:
                print(f"📰 Procesando NO ENTREVISTA #{i}/{len(urls_no_entrevistas)}")
                
                # Extraer texto plano
                texto = Z.get_texto_plano_from_link(url)
                
                if texto:
                    f.write(f"NO ENTREVISTA #{i}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"TEXTO COMPLETO:\n{texto}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Mostrar progreso en consola
                    print(f"  ✅ Texto extraído: {len(texto)} caracteres")
                else:
                    f.write(f"NO ENTREVISTA #{i}\n")
                    f.write(f"URL: {url}\n")
                    f.write("❌ No se pudo extraer texto\n")
                    f.write("=" * 80 + "\n\n")
                    print(f"  ❌ No se pudo extraer texto")
                    
            except Exception as e:
                f.write(f"NO ENTREVISTA #{i}\n")
                f.write(f"URL: {url}\n")
                f.write(f"❌ Error: {e}\n")
                f.write("=" * 80 + "\n\n")
                print(f"  ❌ Error: {e}")
    
    print(f"\n✅ Análisis completado y exportado a: {output_file}")
    print("🤖 Ahora GPT puede analizar los patrones completos en ambas categorías")

if __name__ == "__main__":
    analizar_patrones_entrevistas()
