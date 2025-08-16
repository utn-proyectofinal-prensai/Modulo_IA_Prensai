#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la función es_entrevista_con_gpt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Z_Utils as Z
from O_Utils_GPT import es_entrevista_con_gpt

def exportar_resultados_detallados(urls_entrevistas, urls_no_entrevistas, 
                                   entrevistas_correctas, entrevistas_incorrectas,
                                   no_entrevistas_correctas, no_entrevistas_incorrectas):
    """
    Exporta los resultados detallados del test a un archivo TXT
    """
    output_file = "Testing/resultado_test_entrevistas.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("🔍 ANÁLISIS DETALLADO - TEST es_entrevista_con_gpt\n")
        f.write("=" * 80 + "\n\n")
        
        # Analizar entrevistas
        f.write("📰 ENTREVISTAS CONFIRMADAS - ANÁLISIS DETALLADO\n")
        f.write("-" * 60 + "\n\n")
        
        for i, url in enumerate(urls_entrevistas, 1):
            try:
                texto = Z.procesar_link_robusto(url, 'texto', 3)
                if texto:
                    resultado = es_entrevista_con_gpt(texto)
                    f.write(f"Entrevista #{i}: {resultado}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Título: {texto[:300]}\n")
                    f.write(f"Texto completo:\n{texto}\n")
                    f.write("-" * 80 + "\n\n")
            except Exception as e:
                f.write(f"❌ Error en #{i}: {e}\n\n")
        
        # Analizar no entrevistas
        f.write("📰 NO ENTREVISTAS - ANÁLISIS DETALLADO\n")
        f.write("-" * 60 + "\n\n")
        
        for i, url in enumerate(urls_no_entrevistas, 1):
            try:
                texto = Z.procesar_link_robusto(url, 'texto', 3)
                if texto:
                    resultado = es_entrevista_con_gpt(texto)
                    f.write(f"No Entrevista #{i}: {resultado}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Título: {texto[:300]}\n")
                    f.write(f"Texto completo:\n{texto}\n")
                    f.write("-" * 80 + "\n\n")
            except Exception as e:
                f.write(f"❌ Error en #{i}: {e}\n\n")
        
        # Agregar el resumen final al archivo
        f.write("📊 RESUMEN FINAL DEL TEST\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"📰 ENTREVISTAS:\n")
        f.write(f"✅ Correctas: {entrevistas_correctas}/20\n")
        f.write(f"❌ Incorrectas: {entrevistas_incorrectas}/20\n")
        f.write(f"📊 Precisión: {entrevistas_correctas}/20 = {(entrevistas_correctas/20)*100:.1f}%\n\n")
        
        f.write(f"📰 NO ENTREVISTAS:\n")
        f.write(f"✅ Correctas: {no_entrevistas_correctas}/9\n")
        f.write(f"❌ Incorrectas: {no_entrevistas_incorrectas}/9\n")
        f.write(f"📊 Precisión: {no_entrevistas_correctas}/9 = {(no_entrevistas_correctas/9)*100:.1f}%\n\n")
        
        f.write(f"🎯 RESUMEN GENERAL:\n")
        f.write(f"📊 Precisión total: {entrevistas_correctas + no_entrevistas_correctas}/29 = {((entrevistas_correctas + no_entrevistas_correctas)/29)*100:.1f}%\n")
        f.write(f"📊 Precisión entrevistas: {entrevistas_correctas}/20 = {(entrevistas_correctas/20)*100:.1f}%\n")
        f.write(f"📊 Precisión no entrevistas: {no_entrevistas_correctas}/9 = {(no_entrevistas_correctas/9)*100:.1f}%\n")

def test_es_entrevista_gpt():
    """
    Prueba la función es_entrevista_con_gpt con ejemplos conocidos
    """
    
    # Ejemplos de ENTREVISTAS confirmadas (deberían dar True) - 20 URLs
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
    
    # Ejemplos que NO son entrevistas (deberían dar False) - 9 URLs
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
    
    print("🧪 TESTEANDO es_entrevista_con_gpt")
    print("=" * 60)
    
    # Probar entrevistas confirmadas
    print("\n📰 PROBANDO ENTREVISTAS CONFIRMADAS (deberían dar True):")
    print("-" * 50)
    
    entrevistas_correctas = 0
    entrevistas_incorrectas = 0
    
    for i, url in enumerate(urls_entrevistas, 1):
        try:
            texto = Z.procesar_link_robusto(url, 'texto', 3)
            if texto:
                resultado = es_entrevista_con_gpt(texto)
                print(f"Entrevista #{i}: {resultado}")
                print(f"URL: {url}")
                print(f"Texto (primeros 200 chars): {texto[:200]}...")
                
                # Si falló, mostrar más detalles para análisis
                if not resultado:
                    print("❌ FALLÓ - Analizando por qué...")
                    print(f"Título: {texto[:200]}...")
                    print(f"Primeros 500 caracteres del cuerpo: {texto[200:700]}...")
                    entrevistas_incorrectas += 1
                else:
                    entrevistas_correctas += 1
                
                print("-" * 30)
            else:
                print(f"❌ No se pudo extraer texto de {url}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 RESUMEN ENTREVISTAS:")
    print(f"✅ Correctas: {entrevistas_correctas}/20")
    print(f"❌ Incorrectas: {entrevistas_incorrectas}/20")
    
    # Probar no entrevistas
    print("\n📰 PROBANDO NO ENTREVISTAS (deberían dar False):")
    print("-" * 50)
    
    no_entrevistas_correctas = 0
    no_entrevistas_incorrectas = 0
    
    for i, url in enumerate(urls_no_entrevistas, 1):
        try:
            texto = Z.procesar_link_robusto(url, 'texto', 3)
            if texto:
                resultado = es_entrevista_con_gpt(texto)
                print(f"No Entrevista #{i}: {resultado}")
                print(f"URL: {url}")
                print(f"Texto (primeros 200 chars): {texto[:200]}...")
                
                if resultado:
                    print("❌ FALLÓ - Se clasificó como entrevista cuando NO lo es...")
                    no_entrevistas_incorrectas += 1
                else:
                    no_entrevistas_correctas += 1
                
                print("-" * 30)
            else:
                print(f"❌ No se pudo extraer texto de {url}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 RESUMEN NO ENTREVISTAS:")
    print(f"✅ Correctas: {no_entrevistas_correctas}/9")
    print(f"❌ Incorrectas: {no_entrevistas_incorrectas}/9")
    
    print(f"\n🎯 RESUMEN GENERAL:")
    print(f"📊 Precisión total: {entrevistas_correctas + no_entrevistas_correctas}/29")
    print(f"📊 Precisión entrevistas: {entrevistas_correctas}/20")
    print(f"📊 Precisión no entrevistas: {no_entrevistas_correctas}/9")
    
    # Exportar resultados detallados a TXT
    exportar_resultados_detallados(urls_entrevistas, urls_no_entrevistas,
                                   entrevistas_correctas, entrevistas_incorrectas,
                                   no_entrevistas_correctas, no_entrevistas_incorrectas)
    
    print("\n✅ Test completado")
    print("📁 Resultados exportados a: Testing/resultado_test_entrevistas.txt")

if __name__ == "__main__":
    test_es_entrevista_gpt()
