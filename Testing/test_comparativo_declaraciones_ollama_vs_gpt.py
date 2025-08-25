#!/usr/bin/env python3
"""
Test comparativo: Ollama vs GPT para clasificación de declaraciones
Analiza URLs que SÍ son declaraciones vs URLs que NO son declaraciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from O_Utils_Ollama import es_declaracion_ollama
from O_Utils_GPT import es_declaracion_con_gpt
import Z_Utils as Z
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_comparativo_declaraciones_ollama_vs_gpt():
    """
    Ejecuta test comparativo entre Ollama y GPT para clasificación de declaraciones
    """
    
    # Lista de URLs que SÍ son declaraciones
    declaraciones_urls = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24291597",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24069245",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24136111",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24049682",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23932884",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23432671",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23231721",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23223310",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23233695",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22704241"
    ]
    
    # Lista de URLs que NO son declaraciones
    no_declaraciones_urls = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23370658",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23070737",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294676",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301580",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24182197",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24347481"
    ]
    
    # Combinar todas las URLs
    todas_urls = declaraciones_urls + no_declaraciones_urls
    total_urls = len(todas_urls)
    
    print(f"🧪 TEST COMPARATIVO: OLLAMA vs GPT - DECLARACIONES")
    print(f"📊 Total de URLs a analizar: {total_urls}")
    print(f"📢 Declaraciones esperadas: {len(declaraciones_urls)}")
    print(f"📰 No declaraciones esperadas: {len(no_declaraciones_urls)}")
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
        
        # Determinar si debería ser declaración
        deberia_ser_declaracion = url in declaraciones_urls
        
        try:
            # Extraer texto de la URL primero
            print("  📄 Extrayendo texto...")
            texto = Z.procesar_link_robusto(url, 'texto', 3)
            
            if not texto:
                print(f"  ❌ No se pudo extraer texto de {url}")
                continue
            
            # Test con Ollama
            print("  📱 Probando con Ollama...")
            resultado_ollama = es_declaracion_ollama(texto, ["Gerardo Grieco", "Victoria Noorthoorn", "Jorge Macri", "Gabriela Ricardes"], ["ministerio de cultura", "ministerio de cultura de buenos aires"])
            
            # Test con GPT
            print("  🤖 Probando con GPT...")
            resultado_gpt = es_declaracion_con_gpt(texto, ["Gerardo Grieco", "Victoria Noorthoorn", "Jorge Macri", "Gabriela Ricardes"], ["ministerio de cultura", "ministerio de cultura de buenos aires"])
            
            # Evaluar resultados
            ollama_correcto = (resultado_ollama == deberia_ser_declaracion)
            gpt_correcto = (resultado_gpt == deberia_ser_declaracion)
            
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
                'esperado': deberia_ser_declaracion,
                'obtenido': resultado_ollama,
                'correcto': ollama_correcto
            })
            
            resultados_gpt.append({
                'url': url,
                'esperado': deberia_ser_declaracion,
                'obtenido': resultado_gpt,
                'correcto': gpt_correcto
            })
            
            # Mostrar resultado
            tipo = "DECLARACION" if deberia_ser_declaracion else "NO DECLARACION"
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
    print("📊 RESULTADOS COMPARATIVOS - DECLARACIONES")
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
    
    # Declaraciones
    ollama_declaraciones_correctas = sum(1 for r in resultados_ollama[:len(declaraciones_urls)] if r['correcto'])
    gpt_declaraciones_correctas = sum(1 for r in resultados_gpt[:len(declaraciones_urls)] if r['correcto'])
    
    print(f"   📢 Declaraciones (esperadas: {len(declaraciones_urls)}):")
    print(f"      📱 Ollama: {ollama_declaraciones_correctas}/{len(declaraciones_urls)} = {(ollama_declaraciones_correctas/len(declaraciones_urls)*100):.1f}%")
    print(f"      🤖 GPT: {gpt_declaraciones_correctas}/{len(declaraciones_urls)} = {(gpt_declaraciones_correctas/len(declaraciones_urls)*100):.1f}%")
    
    # No declaraciones
    ollama_no_declaraciones_correctas = sum(1 for r in resultados_ollama[len(declaraciones_urls):] if r['correcto'])
    gpt_no_declaraciones_correctas = sum(1 for r in resultados_gpt[len(declaraciones_urls):] if r['correcto'])
    
    print(f"   📰 No Declaraciones (esperadas: {len(no_declaraciones_urls)}):")
    print(f"      📱 Ollama: {ollama_no_declaraciones_correctas}/{len(no_declaraciones_urls)} = {(ollama_no_declaraciones_correctas/len(no_declaraciones_urls)*100):.1f}%")
    print(f"      🤖 GPT: {gpt_no_declaraciones_correctas}/{len(no_declaraciones_urls)} = {(gpt_no_declaraciones_correctas/len(no_declaraciones_urls)*100):.1f}%")
    
    # Exportar resultados detallados
    exportar_resultados_detallados(resultados_ollama, resultados_gpt, declaraciones_urls, no_declaraciones_urls)
    
    print(f"\n💾 Resultados detallados exportados a: Testing/resultado_comparativo_declaraciones_ollama_vs_gpt.txt")
    print("=" * 80)

def exportar_resultados_detallados(resultados_ollama, resultados_gpt, declaraciones_urls, no_declaraciones_urls):
    """
    Exporta resultados detallados a archivo de texto
    """
    with open("resultado_comparativo_declaraciones_ollama_vs_gpt.txt", "w", encoding="utf-8") as f:
        f.write("🧪 TEST COMPARATIVO: OLLAMA vs GPT - DECLARACIONES - RESULTADOS DETALLADOS\n")
        f.write("=" * 80 + "\n\n")
        
        # Declaraciones
        f.write("📢 DECLARACIONES (deberían ser True):\n")
        f.write("-" * 50 + "\n")
        for i, url in enumerate(declaraciones_urls):
            resultado_ollama = resultados_ollama[i]
            resultado_gpt = resultados_gpt[i]
            
            f.write(f"Declaración #{i+1}:\n")
            f.write(f"URL: {url}\n")
            f.write(f"Esperado: True\n")
            f.write(f"📱 Ollama: {resultado_ollama['obtenido']} {'✅' if resultado_ollama['correcto'] else '❌'}\n")
            f.write(f"🤖 GPT: {resultado_gpt['obtenido']} {'✅' if resultado_gpt['correcto'] else '❌'}\n")
            f.write("\n")
        
        # No declaraciones
        f.write("📰 NO DECLARACIONES (deberían ser False):\n")
        f.write("-" * 50 + "\n")
        for i, url in enumerate(no_declaraciones_urls):
            # Los no-declaraciones están después de las declaraciones en la lista
            idx = len(declaraciones_urls) + i
            if idx < len(resultados_ollama) and idx < len(resultados_gpt):
                resultado_ollama = resultados_ollama[idx]
                resultado_gpt = resultados_gpt[idx]
                
                f.write(f"No Declaración #{i+1}:\n")
                f.write(f"URL: {url}\n")
                f.write(f"Esperado: False\n")
                f.write(f"📱 Ollama: {resultado_ollama['obtenido']} {'✅' if resultado_ollama['correcto'] else '❌'}\n")
                f.write(f"🤖 GPT: {resultado_gpt['obtenido']} {'✅' if resultado_gpt['correcto'] else '❌'}\n")
                f.write("\n")
            else:
                f.write(f"No Declaración #{i+1}:\n")
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
    print("🚀 Iniciando test comparativo Ollama vs GPT para declaraciones...")
    test_comparativo_declaraciones_ollama_vs_gpt()
    print("✅ Test comparativo de declaraciones completado!")
