#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test comparativo: Ollama vs GPT - Factor Político
Compara detección de factor político entre ambos modelos
"""

import sys
sys.path.append('/home/lauti/proyecto_final/Modulo_IA_Prensai')

import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt
import Z_Utils as Z

# URLs de las últimas 10 noticias (de las 20 que pasaste)
urls_test = [
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89317383",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89311718",
    "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84985229",
    "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84990078",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19619285",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=15613613",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24338399",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24262318",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
    "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208"
]

print("🧪 TEST COMPARATIVO: OLLAMA vs GPT - FACTOR POLÍTICO")
print("=" * 80)
print(f"📊 URLs a procesar: {len(urls_test)}")
print("=" * 80)
print()

resultados = []

for i, url in enumerate(urls_test, 1):
    print(f"\n{'='*80}")
    print(f"🔍 NOTICIA {i}/{len(urls_test)}")
    print(f"🔗 URL: {url}")
    print(f"{'='*80}")
    
    # 1. Scrapear la noticia
    print("📥 Scrapeando...")
    html_obj = Z.get_html_object_from_link(url)
    
    if not html_obj:
        print("❌ Error scrapeando URL")
        continue
    
    # 2. Extraer datos básicos
    titulo = Z.get_titulo_from_html_obj(html_obj)
    texto_plano = Z.get_texto_plano_from_link(url)
    
    print(f"📰 TÍTULO: {titulo[:80]}...")
    print()
    
    # 3. Detectar con OLLAMA
    print("🤖 Probando con OLLAMA...")
    resultado_ollama = Oll.detectar_factor_politico_con_ollama(texto_plano)
    print(f"   ✅ Ollama → {resultado_ollama}")
    
    # 4. Detectar con GPT
    print("🧠 Probando con GPT-3.5...")
    resultado_gpt = Gpt.detectar_factor_politico_con_gpt(texto_plano, gpt_active=True)
    print(f"   ✅ GPT-3.5 → {resultado_gpt}")
    
    # 5. Comparar resultados
    if resultado_ollama == resultado_gpt:
        print(f"   ✅ ¡COINCIDEN! Ambos: {resultado_ollama}")
        coincide = "✅ SÍ"
    else:
        print(f"   ⚠️ DIFIEREN - Ollama: {resultado_ollama} | GPT: {resultado_gpt}")
        coincide = "❌ NO"
    
    # Guardar resultado
    resultados.append({
        'url': url,
        'titulo': titulo,
        'ollama': resultado_ollama,
        'gpt': resultado_gpt,
        'coincide': coincide
    })

# RESUMEN FINAL
print("\n" + "="*80)
print("📊 RESUMEN COMPARATIVO")
print("="*80)

total = len(resultados)
coincidencias = sum(1 for r in resultados if r['coincide'] == "✅ SÍ")
diferencias = total - coincidencias

print(f"\n📈 Estadísticas:")
print(f"   Total procesadas: {total}")
print(f"   Coincidencias: {coincidencias} ({coincidencias/total*100:.1f}%)")
print(f"   Diferencias: {diferencias} ({diferencias/total*100:.1f}%)")

# Detectadas como políticas
ollama_si = sum(1 for r in resultados if r['ollama'] == 'SI')
gpt_si = sum(1 for r in resultados if r['gpt'] == 'SI')

print(f"\n🔍 Detección de factor político:")
print(f"   Ollama detectó: {ollama_si}/{total} como POLÍTICO")
print(f"   GPT detectó: {gpt_si}/{total} como POLÍTICO")

# Detalles de diferencias
if diferencias > 0:
    print(f"\n⚠️ Noticias con resultados diferentes:")
    for r in resultados:
        if r['coincide'] == "❌ NO":
            print(f"\n   📰 {r['titulo'][:60]}...")
            print(f"      Ollama: {r['ollama']} | GPT: {r['gpt']}")

print("\n" + "="*80)
print("✅ Test completado")
print("="*80)

