#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer textos planos de noticias que NO son entrevistas
para análisis manual de patrones por GPT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z

def analizar_patrones_no_entrevistas():
    """
    Extrae textos planos de URLs que NO son entrevistas para análisis manual
    """
    
    # URLs que NO son entrevistas (aunque parezcan)
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
    
    print("🔍 ANALIZANDO PATRONES DE NO ENTREVISTAS")
    print("=" * 60)
    print(f"Total de URLs a analizar: {len(urls_no_entrevistas)}")
    print("=" * 60)
    
    for i, url in enumerate(urls_no_entrevistas, 1):
        try:
            print(f"\n📰 NO ENTREVISTA #{i}")
            print(f"🔗 URL: {url}")
            print("-" * 50)
            
            # Extraer texto plano
            texto = Z.get_texto_plano_from_link(url)
            
            if texto:
                # Mostrar primeros 800 caracteres para análisis
                print("📝 TEXTO PLANO (primeros 800 caracteres):")
                print(texto[:800])
                if len(texto) > 800:
                    print("...")
                    print(f"[Texto completo: {len(texto)} caracteres]")
            else:
                print("❌ No se pudo extraer texto")
                
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error procesando {url}: {e}")
            print("=" * 60)
    
    print("\n✅ Análisis completado")
    print("🤖 Ahora GPT puede analizar las diferencias entre entrevistas y no entrevistas")

if __name__ == "__main__":
    analizar_patrones_no_entrevistas()
