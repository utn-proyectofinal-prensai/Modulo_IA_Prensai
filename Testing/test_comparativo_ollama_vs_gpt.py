#!/usr/bin/env python3
"""
Test comparativo: Ollama vs GPT para clasificación de entrevistas
Analiza los mismos 29 links con ambos modelos y compara resultados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from O_Utils_Ollama import es_entrevista_ollama
from O_Utils_GPT import es_entrevista_con_gpt
import Z_Utils as Z
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_comparativo_ollama_vs_gpt():
    """
    Ejecuta test comparativo entre Ollama y GPT para los mismos 29 links
    """
    
    # Lista de URLs de entrevistas (SÍ son entrevistas) - USANDO LOS MISMOS DEL TEST ANTERIOR
    entrevistas_urls = [
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
    
    # Lista de URLs que NO son entrevistas
    no_entrevistas_urls = [
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
    
    # Combinar todas las URLs
    todas_urls = entrevistas_urls + no_entrevistas_urls
    total_urls = len(todas_urls)
    
    print(f"🧪 TEST COMPARATIVO: OLLAMA vs GPT")
    print(f"📊 Total de URLs a analizar: {total_urls}")
    print(f"📰 Entrevistas esperadas: {len(entrevistas_urls)}")
    print(f"📰 No entrevistas esperadas: {len(no_entrevistas_urls)}")
    print("=" * 80)
    
    # Resultados
    resultados_ollama = []
    resultados_gpt = []
    
    # Contadores
    ollama_correctas = 0
    ollama_incorrectas = 0
    gpt_correctas = 0
    gpt_incorrectas = 0
    
    # Procesar cada URL
    for i, url in enumerate(todas_urls, 1):
        print(f"\n🔍 Procesando {i}/{total_urls}: {url}")
        
        # Determinar si debería ser entrevista
        deberia_ser_entrevista = url in entrevistas_urls
        
        try:
            # Extraer texto de la URL primero
            print("  📄 Extrayendo texto...")
            texto = Z.procesar_link_robusto(url, 'texto', 3)
            
            if not texto:
                print(f"  ❌ No se pudo extraer texto de {url}")
                continue
            
            # Test con Ollama
            print("  📱 Probando con Ollama...")
            resultado_ollama = es_entrevista_ollama(texto)
            
            # Test con GPT
            print("  🤖 Probando con GPT...")
            resultado_gpt = es_entrevista_con_gpt(texto)
            
            # Evaluar resultados
            ollama_correcto = (resultado_ollama == deberia_ser_entrevista)
            gpt_correcto = (resultado_gpt == deberia_ser_entrevista)
            
            if ollama_correcto:
                ollama_correctas += 1
            else:
                ollama_incorrectas += 1
                
            if gpt_correcto:
                gpt_correctas += 1
            else:
                gpt_incorrectas += 1
            
            # Guardar resultados
            resultados_ollama.append({
                'url': url,
                'esperado': deberia_ser_entrevista,
                'obtenido': resultado_ollama,
                'correcto': ollama_correcto
            })
            
            resultados_gpt.append({
                'url': url,
                'esperado': deberia_ser_entrevista,
                'obtenido': resultado_gpt,
                'correcto': gpt_correcto
            })
            
            # Mostrar resultado
            tipo = "ENTREVISTA" if deberia_ser_entrevista else "NO ENTREVISTA"
            print(f"  ✅ Esperado: {tipo}")
            print(f"  📱 Ollama: {resultado_ollama} {'✅' if ollama_correcto else '❌'}")
            print(f"  🤖 GPT: {resultado_gpt} {'✅' if gpt_correcto else '❌'}")
            
            # Pausa entre requests para no sobrecargar las APIs
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error procesando {url}: {e}")
            continue
    
    # Calcular métricas
    print("\n" + "=" * 80)
    print("📊 RESULTADOS COMPARATIVOS")
    print("=" * 80)
    
    # Métricas Ollama
    precision_ollama = (ollama_correctas / total_urls) * 100 if total_urls > 0 else 0
    print(f"\n📱 OLLAMA:")
    print(f"   ✅ Correctas: {ollama_correctas}/{total_urls}")
    print(f"   ❌ Incorrectas: {ollama_incorrectas}/{total_urls}")
    print(f"   📊 Precisión: {precision_ollama:.1f}%")
    
    # Métricas GPT
    precision_gpt = (gpt_correctas / total_urls) * 100 if total_urls > 0 else 0
    print(f"\n🤖 GPT:")
    print(f"   ✅ Correctas: {gpt_correctas}/{total_urls}")
    print(f"   ❌ Incorrectas: {gpt_incorrectas}/{total_urls}")
    print(f"   📊 Precisión: {precision_gpt:.1f}%")
    
    # Comparación
    print(f"\n🔍 COMPARACIÓN:")
    diferencia = precision_gpt - precision_ollama
    if diferencia > 0:
        print(f"   🏆 GPT es {diferencia:.1f}% más preciso que Ollama")
    elif diferencia < 0:
        print(f"   🏆 Ollama es {abs(diferencia):.1f}% más preciso que GPT")
    else:
        print(f"   🤝 Ambos modelos tienen la misma precisión")
    
    # Análisis detallado por categoría
    print(f"\n📋 ANÁLISIS DETALLADO:")
    
    # Entrevistas
    ollama_entrevistas_correctas = sum(1 for r in resultados_ollama[:len(entrevistas_urls)] if r['correcto'])
    gpt_entrevistas_correctas = sum(1 for r in resultados_gpt[:len(entrevistas_urls)] if r['correcto'])
    
    print(f"   📰 Entrevistas (esperadas: {len(entrevistas_urls)}):")
    print(f"      📱 Ollama: {ollama_entrevistas_correctas}/{len(entrevistas_urls)} = {(ollama_entrevistas_correctas/len(entrevistas_urls)*100):.1f}%")
    print(f"      🤖 GPT: {gpt_entrevistas_correctas}/{len(entrevistas_urls)} = {(gpt_entrevistas_correctas/len(entrevistas_urls)*100):.1f}%")
    
    # No entrevistas
    ollama_no_entrevistas_correctas = sum(1 for r in resultados_ollama[len(entrevistas_urls):] if r['correcto'])
    gpt_no_entrevistas_correctas = sum(1 for r in resultados_gpt[len(entrevistas_urls):] if r['correcto'])
    
    print(f"   📰 No Entrevistas (esperadas: {len(no_entrevistas_urls)}):")
    print(f"      📱 Ollama: {ollama_no_entrevistas_correctas}/{len(no_entrevistas_urls)} = {(ollama_no_entrevistas_correctas/len(no_entrevistas_urls)*100):.1f}%")
    print(f"      🤖 GPT: {gpt_no_entrevistas_correctas}/{len(no_entrevistas_urls)} = {(gpt_no_entrevistas_correctas/len(no_entrevistas_urls)*100):.1f}%")
    
    # Exportar resultados detallados
    exportar_resultados_detallados(resultados_ollama, resultados_gpt, entrevistas_urls, no_entrevistas_urls)
    
    print(f"\n💾 Resultados detallados exportados a: Testing/resultado_comparativo_ollama_vs_gpt.txt")
    print("=" * 80)

def exportar_resultados_detallados(resultados_ollama, resultados_gpt, entrevistas_urls, no_entrevistas_urls):
    """
    Exporta resultados detallados a archivo de texto
    """
    with open("Testing/resultado_comparativo_ollama_vs_gpt.txt", "w", encoding="utf-8") as f:
        f.write("🧪 TEST COMPARATIVO: OLLAMA vs GPT - RESULTADOS DETALLADOS\n")
        f.write("=" * 80 + "\n\n")
        
        # Entrevistas
        f.write("📰 ENTREVISTAS (deberían ser True):\n")
        f.write("-" * 50 + "\n")
        for i, url in enumerate(entrevistas_urls):
            resultado_ollama = resultados_ollama[i]
            resultado_gpt = resultados_gpt[i]
            
            f.write(f"Entrevista #{i+1}:\n")
            f.write(f"URL: {url}\n")
            f.write(f"Esperado: True\n")
            f.write(f"📱 Ollama: {resultado_ollama['obtenido']} {'✅' if resultado_ollama['correcto'] else '❌'}\n")
            f.write(f"🤖 GPT: {resultado_gpt['obtenido']} {'✅' if resultado_gpt['correcto'] else '❌'}\n")
            f.write("\n")
        
        # No entrevistas
        f.write("📰 NO ENTREVISTAS (deberían ser False):\n")
        f.write("-" * 50 + "\n")
        for i, url in enumerate(no_entrevistas_urls):
            # Los no-entrevistas están después de las entrevistas en la lista
            idx = len(entrevistas_urls) + i
            if idx < len(resultados_ollama) and idx < len(resultados_gpt):
                resultado_ollama = resultados_ollama[idx]
                resultado_gpt = resultados_gpt[idx]
                
                f.write(f"No Entrevista #{i+1}:\n")
                f.write(f"URL: {url}\n")
                f.write(f"Esperado: False\n")
                f.write(f"📱 Ollama: {resultado_ollama['obtenido']} {'✅' if resultado_ollama['correcto'] else '❌'}\n")
                f.write(f"🤖 GPT: {resultado_gpt['obtenido']} {'✅' if resultado_gpt['correcto'] else '❌'}\n")
                f.write("\n")
            else:
                f.write(f"No Entrevista #{i+1}:\n")
                f.write(f"URL: {url}\n")
                f.write(f"❌ Error: Índice fuera de rango ({idx})\n\n")
        
        # Resumen
        f.write("📊 RESUMEN COMPARATIVO\n")
        f.write("=" * 50 + "\n")
        
        # Contar correctas por modelo
        ollama_correctas = sum(1 for r in resultados_ollama if r['correcto'])
        gpt_correctas = sum(1 for r in resultados_gpt if r['correcto'])
        total = len(resultados_ollama)
        
        f.write(f"📱 OLLAMA: {ollama_correctas}/{total} = {(ollama_correctas/total*100):.1f}%\n")
        f.write(f"🤖 GPT: {gpt_correctas}/{total} = {(gpt_correctas/total*100):.1f}%\n")
        
        diferencia = (gpt_correctas/total*100) - (ollama_correctas/total*100)
        if diferencia > 0:
            f.write(f"🏆 GPT es {diferencia:.1f}% más preciso que Ollama\n")
        elif diferencia < 0:
            f.write(f"🏆 Ollama es {abs(diferencia):.1f}% más preciso que GPT\n")
        else:
            f.write(f"🤝 Ambos modelos tienen la misma precisión\n")

if __name__ == "__main__":
    print("🚀 Iniciando test comparativo Ollama vs GPT...")
    test_comparativo_ollama_vs_gpt()
    print("✅ Test comparativo completado!")
