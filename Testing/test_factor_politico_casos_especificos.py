#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico: Análisis de 2 noticias para factor político
"""

import sys
sys.path.append('/home/lauti/proyecto_final/Modulo_IA_Prensai')

import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import Z_Utils as Z

# URLs específicas para analizar
urls_test = [
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=71385317",
        "descripcion": "Cierre de gestión Rodríguez Larreta - Balance 8 años"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23188092",
        "descripcion": "Cierre de campaña PRO con Macri - Elecciones"
    }
]

print("🧪 TEST ESPECÍFICO: FACTOR POLÍTICO - CASOS DE ANÁLISIS")
print("=" * 80)
print()

for i, caso in enumerate(urls_test, 1):
    url = caso['url']
    descripcion = caso['descripcion']
    
    print(f"\n{'='*80}")
    print(f"📰 CASO {i}: {descripcion}")
    print(f"🔗 URL: {url}")
    print(f"{'='*80}\n")
    
    # 1. Scrapear
    print("📥 Scrapeando...")
    html_obj = Z.get_html_object_from_link(url)
    
    if not html_obj:
        print("❌ Error scrapeando URL")
        continue
    
    # 2. Extraer datos
    titulo = Z.get_titulo_from_html_obj(html_obj)
    texto_plano = Z.get_texto_plano_from_link(url)
    
    print(f"📋 TÍTULO COMPLETO:")
    print(f"   {titulo}\n")
    
    # Mostrar extracto del texto
    extracto = texto_plano[:500] if len(texto_plano) > 500 else texto_plano
    print(f"📄 EXTRACTO DEL TEXTO ({len(texto_plano)} caracteres totales):")
    print(f"   {extracto}...\n")
    
    # 3. Detectar con OLLAMA
    print("🤖 OLLAMA (prompt original):")
    resultado_ollama = Oll.detectar_factor_politico_con_ollama(texto_plano)
    print(f"   Resultado: {resultado_ollama}")
    
    # 4. Detectar con GPT
    print("\n🧠 GPT-3.5 (prompt ultra-estricto):")
    resultado_gpt = Gpt.detectar_factor_politico_con_gpt(texto_plano, gpt_active=True)
    print(f"   Resultado: {resultado_gpt}")
    
    # 5. Análisis
    print(f"\n📊 COMPARACIÓN:")
    if resultado_ollama == resultado_gpt:
        print(f"   ✅ COINCIDEN: Ambos marcaron {resultado_ollama}")
    else:
        print(f"   ⚠️ DIFIEREN:")
        print(f"      Ollama: {resultado_ollama}")
        print(f"      GPT-3.5: {resultado_gpt}")
    
    # 6. Análisis manual esperado
    print(f"\n🎯 ANÁLISIS ESPERADO:")
    if "campaña" in descripcion.lower() or "elecciones" in descripcion.lower():
        print(f"   ✅ Esta noticia DEBERÍA ser POLÍTICA (menciona {descripcion})")
        esperado = "SI"
    else:
        print(f"   ❌ Esta noticia NO DEBERÍA ser POLÍTICA (es {descripcion})")
        esperado = "NO"
    
    print(f"\n🔍 VERIFICACIÓN:")
    print(f"   Resultado esperado: {esperado}")
    print(f"   Ollama acertó: {'✅ SÍ' if resultado_ollama == esperado else '❌ NO'}")
    print(f"   GPT acertó: {'✅ SÍ' if resultado_gpt == esperado else '❌ NO'}")

print("\n" + "="*80)
print("✅ Test completado")
print("="*80)

