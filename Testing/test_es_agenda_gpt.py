#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de testing para es_agenda_con_gpt
Dataset optimizado: 20 URLs de agenda + 10 URLs de no-agenda
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from O_Utils_GPT import es_agenda_con_gpt
import Z_Utils as Z
import time
from datetime import datetime

def test_es_agenda_gpt():
    """
    Test principal para es_agenda_con_gpt
    """
    print("🔍 INICIANDO TEST DE es_agenda_con_gpt")
    print("=" * 60)
    
    # URLs que SÍ son agenda (20)
    agendas_urls = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24293217",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294600",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24302208",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24347481",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24369493",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196084",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24185308",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24257893",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23657206",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23662034",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23701559",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595633",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23595797",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23189363",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23186443",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23196849",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23209609",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23249425",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23240317",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23059116"
    ]
    
    # URLs que NO son agenda (10)
    no_agendas_urls = [
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24294676",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24291597",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301580",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24182197",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24254500",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24062160",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24069245",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24136111",
        "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24137173"
    ]
    
    print(f"📊 DATASET:")
    print(f"   ✅ URLs de agenda: {len(agendas_urls)}")
    print(f"   ❌ URLs de no-agenda: {len(no_agendas_urls)}")
    print(f"   📍 Total: {len(agendas_urls) + len(no_agendas_urls)} URLs")
    print()
    
    # Resultados
    resultados_agendas = []
    resultados_no_agendas = []
    
    # Test URLs de agenda
    print("🔍 TESTEANDO URLs de AGENDA...")
    print("-" * 40)
    
    for i, url in enumerate(agendas_urls, 1):
        print(f"📅 [{i:2d}/{len(agendas_urls)}] Procesando agenda: {url}")
        
        # Extraer texto
        texto = Z.procesar_link_robusto(url, 'texto', 3)
        if texto is None:
            print(f"   ❌ Error al extraer texto de {url}")
            resultados_agendas.append({
                'url': url,
                'texto': None,
                'clasificacion': False,
                'esperado': True,
                'correcto': False,
                'error': 'No se pudo extraer texto'
            })
            continue
        
        # Clasificar con GPT usando marcar_o_valorar_con_ia (como en la API)
        try:
            LIMITE_TEXTO = 14900  # Mismo valor que en main.py y api_flask.py
            clasificacion = Z.marcar_o_valorar_con_ia(texto, es_agenda_con_gpt, LIMITE_TEXTO)
            esperado = True
            
            # Si el texto excede el límite, marcar_o_valorar_con_ia devuelve "REVISAR MANUAL"
            if clasificacion == "REVISAR MANUAL":
                correcto = False
                error_msg = f"Texto excede límite de {LIMITE_TEXTO} caracteres (longitud: {len(texto)})"
                print(f"   ⚠️  Texto excede límite: {len(texto)} chars > {LIMITE_TEXTO}")
            else:
                correcto = (clasificacion == esperado)
                error_msg = None
                status = "✅" if correcto else "❌"
                print(f"   {status} Clasificado como: {'AGENDA' if clasificacion else 'NO AGENDA'}")
            
            resultados_agendas.append({
                'url': url,
                'texto': texto[:500] + "..." if len(texto) > 500 else texto,
                'clasificacion': clasificacion,
                'esperado': esperado,
                'correcto': correcto,
                'error': error_msg
            })
            
        except Exception as e:
            print(f"   ❌ Error en clasificación: {e}")
            resultados_agendas.append({
                'url': url,
                'texto': texto[:500] + "..." if len(texto) > 500 else texto,
                'clasificacion': None,
                'esperado': True,
                'correcto': False,
                'error': str(e)
            })
        
        time.sleep(1)  # Pausa entre requests
    
    print()
    
    # Test URLs de no-agenda
    print("🔍 TESTEANDO URLs de NO-AGENDA...")
    print("-" * 40)
    
    for i, url in enumerate(no_agendas_urls, 1):
        print(f"📰 [{i:2d}/{len(no_agendas_urls)}] Procesando no-agenda: {url}")
        
        # Extraer texto
        texto = Z.procesar_link_robusto(url, 'texto', 3)
        if texto is None:
            print(f"   ❌ Error al extraer texto de {url}")
            resultados_no_agendas.append({
                'url': url,
                'texto': None,
                'clasificacion': False,
                'esperado': False,
                'correcto': False,
                'error': 'No se pudo extraer texto'
            })
            continue
        
        # Clasificar con GPT usando marcar_o_valorar_con_ia (como en la API)
        try:
            LIMITE_TEXTO = 14900  # Mismo valor que en main.py y api_flask.py
            clasificacion = Z.marcar_o_valorar_con_ia(texto, es_agenda_con_gpt, LIMITE_TEXTO)
            esperado = False
            
            # Si el texto excede el límite, marcar_o_valorar_con_ia devuelve "REVISAR MANUAL"
            if clasificacion == "REVISAR MANUAL":
                correcto = False
                error_msg = f"Texto excede límite de {LIMITE_TEXTO} caracteres (longitud: {len(texto)})"
                print(f"   ⚠️  Texto excede límite: {len(texto)} chars > {LIMITE_TEXTO}")
            else:
                correcto = (clasificacion == esperado)
                error_msg = None
                status = "✅" if correcto else "❌"
                print(f"   {status} Clasificado como: {'AGENDA' if clasificacion else 'NO AGENDA'}")
            
            resultados_no_agendas.append({
                'url': url,
                'texto': texto[:500] + "..." if len(texto) > 500 else texto,
                'clasificacion': clasificacion,
                'esperado': esperado,
                'correcto': correcto,
                'error': error_msg
            })
            
        except Exception as e:
            print(f"   ❌ Error en clasificación: {e}")
            resultados_no_agendas.append({
                'url': url,
                'texto': texto[:500] + "..." if len(texto) > 500 else texto,
                'clasificacion': None,
                'esperado': False,
                'correcto': False,
                'error': str(e)
            })
        
        time.sleep(1)  # Pausa entre requests
    
    print()
    
    # Análisis de resultados
    analizar_resultados(resultados_agendas, resultados_no_agendas)
    
    # Exportar resultados detallados
    exportar_resultados_detallados(resultados_agendas, resultados_no_agendas)
    
    # Exportar textos completos para análisis manual
    exportar_textos_completos(resultados_agendas, resultados_no_agendas)

def analizar_resultados(resultados_agendas, resultados_no_agendas):
    """
    Analiza y muestra los resultados del test con métricas separadas
    """
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 60)
    
    # Separar URLs por estado
    agendas_procesadas = [r for r in resultados_agendas if r['clasificacion'] != "REVISAR MANUAL"]
    agendas_no_procesadas = [r for r in resultados_agendas if r['clasificacion'] == "REVISAR MANUAL"]
    
    no_agendas_procesadas = [r for r in resultados_no_agendas if r['clasificacion'] != "REVISAR MANUAL"]
    no_agendas_no_procesadas = [r for r in resultados_no_agendas if r['clasificacion'] == "REVISAR MANUAL"]
    
    # Métricas de clasificación (solo URLs procesadas por GPT)
    agendas_correctas = sum(1 for r in agendas_procesadas if r['clasificacion'] == True)
    agendas_incorrectas = sum(1 for r in agendas_procesadas if r['clasificacion'] == False)
    
    no_agendas_correctas = sum(1 for r in no_agendas_procesadas if r['clasificacion'] == False)
    no_agendas_incorrectas = sum(1 for r in no_agendas_procesadas if r['clasificacion'] == True)
    
    # Totales
    total_agendas = len(resultados_agendas)
    total_no_agendas = len(resultados_no_agendas)
    total_urls = total_agendas + total_no_agendas
    
    total_procesadas = len(agendas_procesadas) + len(no_agendas_procesadas)
    total_no_procesadas = len(agendas_no_procesadas) + len(no_agendas_no_procesadas)
    
    # Precisión de clasificación (solo sobre URLs procesadas)
    precision_agendas = (agendas_correctas / len(agendas_procesadas)) * 100 if agendas_procesadas else 0
    precision_no_agendas = (no_agendas_correctas / len(no_agendas_procesadas)) * 100 if no_agendas_procesadas else 0
    precision_general = ((agendas_correctas + no_agendas_correctas) / total_procesadas) * 100 if total_procesadas > 0 else 0
    
    print(f"🎯 AGENDAS:")
    print(f"   📊 Total: {total_agendas}")
    print(f"   ✅ Procesadas por GPT: {len(agendas_procesadas)}")
    print(f"   ⚠️  No procesadas (límite): {len(agendas_no_procesadas)}")
    print(f"   🎯 Clasificación correcta: {agendas_correctas}/{len(agendas_procesadas)} ({precision_agendas:.1f}%)")
    
    print(f"📰 NO-AGENDAS:")
    print(f"   📊 Total: {total_no_agendas}")
    print(f"   ✅ Procesadas por GPT: {len(no_agendas_procesadas)}")
    print(f"   ⚠️  No procesadas (límite): {len(no_agendas_no_procesadas)}")
    print(f"   🎯 Clasificación correcta: {no_agendas_correctas}/{len(no_agendas_procesadas)} ({precision_no_agendas:.1f}%)")
    
    print(f"🌐 MÉTRICAS GENERALES:")
    print(f"   📊 Total URLs: {total_urls}")
    print(f"   ✅ URLs procesadas por GPT: {total_procesadas}")
    print(f"   ⚠️  URLs no procesadas (límite): {total_no_procesadas}")
    print(f"   🎯 Precisión de clasificación: {precision_general:.1f}% (solo URLs procesadas)")
    
    print()
    
    # Análisis de errores de clasificación (solo URLs procesadas)
    if agendas_incorrectas > 0:
        print("🔍 AGENDAS MAL CLASIFICADAS POR GPT:")
        for r in agendas_procesadas:
            if r['clasificacion'] == False:
                print(f"   ❌ {r['url']}")
                print(f"      Esperado: AGENDA, Obtenido: NO AGENDA")
                print()
    
    if no_agendas_incorrectas > 0:
        print("🔍 NO-AGENDAS MAL CLASIFICADAS POR GPT:")
        for r in no_agendas_procesadas:
            if r['clasificacion'] == True:
                print(f"   ❌ {r['url']}")
                print(f"      Esperado: NO AGENDA, Obtenido: AGENDA")
                print()
    
    # URLs no procesadas por límite
    if total_no_procesadas > 0:
        print("⚠️  URLs NO PROCESADAS POR LÍMITE DE CARACTERES:")
        for r in agendas_no_procesadas + no_agendas_no_procesadas:
            print(f"   ⚠️  {r['url']} - {r['error']}")
        print()

def exportar_resultados_detallados(resultados_agendas, resultados_no_agendas):
    """
    Exporta los resultados detallados a un archivo TXT
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"Testing/resultado_test_agendas.txt"
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DETALLADOS - TEST es_agenda_con_gpt\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total URLs: {len(resultados_agendas) + len(resultados_no_agendas)}\n\n")
        
        # Métricas generales
        total_agendas = len(resultados_agendas)
        agendas_correctas = sum(1 for r in resultados_agendas if r['correcto'])
        total_no_agendas = len(resultados_no_agendas)
        no_agendas_correctas = sum(1 for r in resultados_no_agendas if r['correcto'])
        
        total_urls = total_agendas + total_no_agendas
        total_correctas = agendas_correctas + no_agendas_correctas
        precision_general = (total_correctas / total_urls) * 100 if total_urls > 0 else 0
        
        f.write("📊 MÉTRICAS GENERALES:\n")
        f.write(f"   ✅ Total correctas: {total_correctas}/{total_urls} ({precision_general:.1f}%)\n")
        f.write(f"   ❌ Total incorrectas: {total_urls - total_correctas}/{total_urls}\n\n")
        
        # Resultados de agendas
        f.write("🎯 RESULTADOS DE AGENDAS:\n")
        f.write("-" * 40 + "\n")
        for i, r in enumerate(resultados_agendas, 1):
            f.write(f"{i:2d}. {r['url']}\n")
            f.write(f"    Esperado: AGENDA (True)\n")
            f.write(f"    Obtenido: {'AGENDA' if r['clasificacion'] else 'NO AGENDA'} ({r['clasificacion']})\n")
            f.write(f"    Estado: {'✅ CORRECTO' if r['correcto'] else '❌ INCORRECTO'}\n")
            if r['error']:
                f.write(f"    Error: {r['error']}\n")
            if r['texto']:
                f.write(f"    Texto (primeros 500 chars): {r['texto'][:500]}...\n")
            f.write("\n")
        
        # Resultados de no-agendas
        f.write("📰 RESULTADOS DE NO-AGENDAS:\n")
        f.write("-" * 40 + "\n")
        for i, r in enumerate(resultados_no_agendas, 1):
            f.write(f"{i:2d}. {r['url']}\n")
            f.write(f"    Esperado: NO AGENDA (False)\n")
            f.write(f"    Obtenido: {'AGENDA' if r['clasificacion'] else 'NO AGENDA'} ({r['clasificacion']})\n")
            f.write(f"    Estado: {'✅ CORRECTO' if r['correcto'] else '❌ INCORRECTO'}\n")
            if r['error']:
                f.write(f"    Error: {r['error']}\n")
            if r['texto']:
                f.write(f"    Texto (primeros 500 chars): {r['texto'][:500]}...\n")
            f.write("\n")
        
        # Resumen final con métricas separadas
        f.write("📋 RESUMEN FINAL:\n")
        f.write("=" * 60 + "\n")
        
        # Separar URLs por estado
        agendas_procesadas = [r for r in resultados_agendas if r['clasificacion'] != "REVISAR MANUAL"]
        agendas_no_procesadas = [r for r in resultados_agendas if r['clasificacion'] == "REVISAR MANUAL"]
        
        no_agendas_procesadas = [r for r in resultados_no_agendas if r['clasificacion'] != "REVISAR MANUAL"]
        no_agendas_no_procesadas = [r for r in resultados_no_agendas if r['clasificacion'] == "REVISAR MANUAL"]
        
        # Métricas de clasificación (solo URLs procesadas por GPT)
        agendas_correctas = sum(1 for r in agendas_procesadas if r['clasificacion'] == True)
        no_agendas_correctas = sum(1 for r in no_agendas_procesadas if r['clasificacion'] == False)
        
        total_procesadas = len(agendas_procesadas) + len(no_agendas_procesadas)
        total_no_procesadas = len(agendas_no_procesadas) + len(no_agendas_no_procesadas)
        
        precision_general = ((agendas_correctas + no_agendas_correctas) / total_procesadas) * 100 if total_procesadas > 0 else 0
        
        f.write(f"🎯 AGENDAS:\n")
        f.write(f"   📊 Total: {len(resultados_agendas)}\n")
        f.write(f"   ✅ Procesadas por GPT: {len(agendas_procesadas)}\n")
        f.write(f"   ⚠️  No procesadas (límite): {len(agendas_no_procesadas)}\n")
        f.write(f"   🎯 Clasificación correcta: {agendas_correctas}/{len(agendas_procesadas)} ({agendas_correctas/len(agendas_procesadas)*100:.1f}%)\n\n")
        
        f.write(f"📰 NO-AGENDAS:\n")
        f.write(f"   📊 Total: {len(resultados_no_agendas)}\n")
        f.write(f"   ✅ Procesadas por GPT: {len(no_agendas_procesadas)}\n")
        f.write(f"   ⚠️  No procesadas (límite): {len(no_agendas_no_procesadas)}\n")
        f.write(f"   🎯 Clasificación correcta: {no_agendas_correctas}/{len(no_agendas_procesadas)} ({no_agendas_correctas/len(no_agendas_procesadas)*100:.1f}%)\n\n")
        
        f.write(f"🌐 MÉTRICAS GENERALES:\n")
        f.write(f"   📊 Total URLs: {len(resultados_agendas) + len(resultados_no_agendas)}\n")
        f.write(f"   ✅ URLs procesadas por GPT: {total_procesadas}\n")
        f.write(f"   ⚠️  URLs no procesadas (límite): {total_no_procesadas}\n")
        f.write(f"   🎯 Precisión de clasificación: {precision_general:.1f}% (solo URLs procesadas)\n")
    
    print(f"💾 Resultados exportados a: {nombre_archivo}")

def exportar_textos_completos(resultados_agendas, resultados_no_agendas):
    """
    Exporta los textos COMPLETOS de todas las URLs para análisis manual
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"Testing/textos_completos_agendas_{timestamp}.txt"
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write("TEXTOS COMPLETOS - TEST es_agenda_con_gpt\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total URLs: {len(resultados_agendas) + len(resultados_no_agendas)}\n\n")
        
        # Textos de agendas
        f.write("🎯 TEXTOS COMPLETOS DE AGENDAS:\n")
        f.write("=" * 60 + "\n\n")
        for i, r in enumerate(resultados_agendas, 1):
            f.write(f"AGENDA {i:2d}: {r['url']}\n")
            f.write("-" * 80 + "\n")
            if r['texto']:
                f.write(f"TEXTO COMPLETO:\n{r['texto']}\n")
            else:
                f.write("TEXTO: No se pudo extraer\n")
            f.write("\n" + "=" * 80 + "\n\n")
        
        # Textos de no-agendas
        f.write("📰 TEXTOS COMPLETOS DE NO-AGENDAS:\n")
        f.write("=" * 60 + "\n\n")
        for i, r in enumerate(resultados_no_agendas, 1):
            f.write(f"NO-AGENDA {i:2d}: {r['url']}\n")
            f.write("-" * 80 + "\n")
            if r['texto']:
                f.write(f"TEXTO COMPLETO:\n{r['texto']}\n")
            else:
                f.write("TEXTO: No se pudo extraer\n")
            f.write("\n" + "=" * 80 + "\n\n")
        
        # Resumen de clasificaciones
        f.write("📋 RESUMEN DE CLASIFICACIONES:\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("🎯 AGENDAS:\n")
        for i, r in enumerate(resultados_agendas, 1):
            status = "✅" if r['correcto'] else "❌"
            clasif = "AGENDA" if r['clasificacion'] else "NO AGENDA"
            f.write(f"   {i:2d}. {status} {clasif} - {r['url']}\n")
        
        f.write("\n📰 NO-AGENDAS:\n")
        for i, r in enumerate(resultados_no_agendas, 1):
            status = "✅" if r['correcto'] else "❌"
            clasif = "AGENDA" if r['clasificacion'] else "NO AGENDA"
            f.write(f"   {i:2d}. {status} {clasif} - {r['url']}\n")
    
    print(f"📄 Textos completos exportados a: {nombre_archivo}")

if __name__ == "__main__":
    try:
        test_es_agenda_gpt()
        print("✅ Test completado exitosamente")
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
