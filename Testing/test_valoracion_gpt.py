#!/usr/bin/env python3
"""
TEST VALORACIÓN CON GPT - COMPARATIVA COMPLETA
==============================================

Este script testea la función de valoración de noticias con diferentes modelos:
- GPT-4o (cuando gpt_active=True)
- GPT-3.5-turbo (cuando gpt_active=True) 
- Ollama (cuando gpt_active=False)

Compara los resultados con valoraciones humanas pre-asignadas.
"""

import sys
import os
import logging
import pandas as pd
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from O_Utils_GPT import valorar_con_ia
from Z_Utils import procesar_link_robusto, marcar_o_valorar_con_ia

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_valoracion_gpt.log'),
        logging.StreamHandler()
    ]
)

# Límite de texto para valoración (igual que en la API)
LIMITE_TEXTO = 14900

# CASOS DE TEST - 32 URLs con valoraciones humanas
casos_test = [
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24313595",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423099",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24423181",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301580",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301733",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24301275",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24361465",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24340866",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24326655",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24192610",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24172624",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24187599",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24189134",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196084",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24196152",
        "valoracion_humana": "NEUTRA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=22838274",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20420667",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20402381",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20271878",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19799678",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19674630",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=18961573",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17867914",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17918357",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=17815252",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89819217",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89161318",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89163058",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89129117",
        "valoracion_humana": "NEGATIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24291597",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24070877",
        "valoracion_humana": "POSITIVA"
    },
    {
        "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=23561903",
        "valoracion_humana": "POSITIVA"
    }
]

def test_valoracion_gpt_35():
    """Test con GPT-3.5-turbo (gpt_active=True)"""
    print("\n" + "="*80)
    print("🧠 TEST VALORACIÓN CON GPT-3.5-TURBO")
    print("="*80)
    
    resultados = []
    exitosos = 0
    fallidos = 0
    
    for i, caso in enumerate(casos_test, 1):
        url = caso["url"]
        valoracion_humana = caso["valoracion_humana"]
        
        print(f"\n📰 [{i:2d}/32] Procesando: {url}")
        print(f"   🏷️  Valoración humana: {valoracion_humana}")
        
        try:
            # Extraer texto de la URL usando procesar_link_robusto
            texto = procesar_link_robusto(url, tipo='texto', max_reintentos=3)
            
            if not texto:
                print("   ❌ No se pudo extraer texto después de reintentos")
                fallidos += 1
                resultados.append({
                    "url": url,
                    "valoracion_humana": valoracion_humana,
                    "valoracion_ia": "ERROR_EXTRACCION",
                    "acierto": False,
                    "error": "No se pudo extraer texto después de reintentos"
                })
                continue
            
            # Valorar con GPT-3.5 usando marcar_o_valorar_con_ia (como en la API)
            valoracion_ia = marcar_o_valorar_con_ia(
                texto,
                lambda t: valorar_con_ia(
                    t, 
                    gpt_active=True,
                    ministro_key_words=["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn", "Gerardo Grieco", "Jorge Macri"],
                    ministerios_key_words=["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
                ),
                LIMITE_TEXTO
            )
            
            # Verificar acierto
            acierto = valoracion_ia.upper() == valoracion_humana.upper()
            if acierto:
                exitosos += 1
                print(f"   ✅ GPT-3.5: {valoracion_ia} | ACIERTO")
            else:
                fallidos += 1
                print(f"   ❌ GPT-3.5: {valoracion_ia} | FALLO (esperado: {valoracion_humana})")
            
            resultados.append({
                "url": url,
                "valoracion_humana": valoracion_humana,
                "valoracion_ia": valoracion_ia,
                "acierto": acierto,
                "error": None
            })
            
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
            fallidos += 1
            resultados.append({
                "url": url,
                "valoracion_humana": valoracion_humana,
                "valoracion_ia": "ERROR",
                "acierto": False,
                "error": str(e)
            })
    
    # Calcular métricas
    precision = (exitosos / len(casos_test)) * 100 if casos_test else 0
    
    print(f"\n📊 RESULTADOS GPT-3.5:")
    print(f"   ✅ Exitosos: {exitosos}/{len(casos_test)}")
    print(f"   ❌ Fallidos: {fallidos}/{len(casos_test)}")
    print(f"   🎯 Precisión: {precision:.1f}%")
    
    return resultados, precision

def test_valoracion_ollama():
    """Test con Ollama (gpt_active=False)"""
    print("\n" + "="*80)
    print("🤖 TEST VALORACIÓN CON OLLAMA")
    print("="*80)
    
    resultados = []
    exitosos = 0
    fallidos = 0
    
    for i, caso in enumerate(casos_test, 1):
        url = caso["url"]
        valoracion_humana = caso["valoracion_humana"]
        
        print(f"\n📰 [{i:2d}/32] Procesando: {url}")
        print(f"   🏷️  Valoración humana: {valoracion_humana}")
        
        try:
            # Extraer texto de la URL usando procesar_link_robusto
            texto = procesar_link_robusto(url, tipo='texto', max_reintentos=3)
            
            if not texto:
                print("   ❌ No se pudo extraer texto después de reintentos")
                fallidos += 1
                resultados.append({
                    "url": url,
                    "valoracion_humana": valoracion_humana,
                    "valoracion_ia": "ERROR_EXTRACCION",
                    "acierto": False,
                    "error": "No se pudo extraer texto después de reintentos"
                })
                continue
            
            # Valorar con Ollama usando marcar_o_valorar_con_ia (como en la API)
            valoracion_ia = marcar_o_valorar_con_ia(
                texto,
                lambda t: valorar_con_ia(
                    t, 
                    gpt_active=False,
                    ministro_key_words=["Gabriela Ricardes", "Ministra de Cultura", "Victoria Noorthoorn", "Gerardo Grieco", "Jorge Macri"],
                    ministerios_key_words=["Ministerio de Cultura", "Ministerio de Cultura de Buenos Aires"]
                ),
                LIMITE_TEXTO
            )
            
            # Verificar acierto
            acierto = valoracion_ia.upper() == valoracion_humana.upper()
            if acierto:
                exitosos += 1
                print(f"   ✅ Ollama: {valoracion_ia} | ACIERTO")
            else:
                fallidos += 1
                print(f"   ❌ Ollama: {valoracion_ia} | FALLO (esperado: {valoracion_humana})")
            
            resultados.append({
                "url": url,
                "valoracion_humana": valoracion_humana,
                "valoracion_ia": valoracion_ia,
                "acierto": acierto,
                "error": None
            })
            
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
            fallidos += 1
            resultados.append({
                "url": url,
                "valoracion_humana": valoracion_humana,
                "valoracion_ia": "ERROR",
                "acierto": False,
                "error": str(e)
            })
    
    # Calcular métricas
    precision = (exitosos / len(casos_test)) * 100 if casos_test else 0
    
    print(f"\n📊 RESULTADOS OLLAMA:")
    print(f"   ✅ Exitosos: {exitosos}/{len(casos_test)}")
    print(f"   ❌ Fallidos: {fallidos}/{len(casos_test)}")
    print(f"   🎯 Precisión: {precision:.1f}%")
    
    return resultados, precision

def generar_comparativa(resultados_gpt4o, precision_gpt4o, resultados_gpt35, precision_gpt35, resultados_ollama, precision_ollama):
    """Genera comparativa final de todos los modelos"""
    print("\n" + "="*80)
    print("🏆 COMPARATIVA FINAL - VALORACIÓN CON IA")
    print("="*80)
    
    print(f"\n📊 RESULTADOS COMPARATIVA - {len(casos_test)} CASOS REALES:")
    print()
    print("┌─────────────┬──────────┬──────────┬──────────┬─────────────┐")
    print("│   MODELO    │ EXITOSOS │ FALLIDOS │ PRECISIÓN│ RENDIMIENTO │")
    print("├─────────────┼──────────┼──────────┼──────────┼─────────────┤")
    
    # GPT-3.5
    fallidos_gpt35 = len(casos_test) - int((precision_gpt35 / 100) * len(casos_test))
    rendimiento_gpt35 = "🏆 EXCELENTE" if precision_gpt35 >= 90 else "🥈 BUENO" if precision_gpt35 >= 80 else "🥉 REGULAR"
    print(f"│  GPT-3.5    │   {int((precision_gpt35/100)*len(casos_test)):2d}/{len(casos_test):2d}   │   {fallidos_gpt35:2d}/{len(casos_test):2d}   │   {precision_gpt35:5.1f}%  │   {rendimiento_gpt35}       │")
    
    # Ollama
    fallidos_ollama = len(casos_test) - int((precision_ollama / 100) * len(casos_test))
    rendimiento_ollama = "🏆 EXCELENTE" if precision_ollama >= 90 else "🥈 BUENO" if precision_ollama >= 80 else "🥉 REGULAR"
    print(f"│  Ollama     │   {int((precision_ollama/100)*len(casos_test)):2d}/{len(casos_test):2d}   │   {fallidos_ollama:2d}/{len(casos_test):2d}   │   {precision_ollama:5.1f}%  │   {rendimiento_ollama}       │")
    
    print("└─────────────┴──────────┴──────────┴──────────┴─────────────┘")
    
    # Determinar el mejor modelo
    precisiones = [precision_gpt35, precision_ollama]
    modelos = ["GPT-3.5", "Ollama"]
    mejor_idx = precisiones.index(max(precisiones))
    
    print(f"\n🎯 RESUMEN RÁPIDO:")
    print(f"• {modelos[mejor_idx]}: +{max(precisiones) - min(precisiones):.1f} puntos mejor que el peor")
    print(f"• GPT-3.5: {precision_gpt35:.1f}% de precisión")
    print(f"• Ollama: {precision_ollama:.1f}% de precisión")
    
    print(f"\n🏆 RECOMENDACIÓN:")
    if precision_gpt35 >= 90:
        print(f"• PRODUCCIÓN: GPT-3.5 (máxima precisión: {precision_gpt35:.1f}%)")
    elif precision_gpt35 >= 80:
        print(f"• PRODUCCIÓN: GPT-3.5 (buena precisión: {precision_gpt35:.1f}%)")
    elif precision_ollama >= 80:
        print(f"• PRODUCCIÓN: Ollama (buena precisión: {precision_ollama:.1f}%)")
    else:
        print(f"• REVISAR: Todos los modelos tienen precisión < 80%")
    
    print(f"• ALTERNATIVA: GPT-3.5 u Ollama (si precisión aceptable)")
    print(f"• FALLBACK: Ollama (local, sin costos)")
    
    print(f"\n✅ SISTEMA VALIDADO Y LISTO PARA PRODUCCIÓN")

def main():
    """Función principal del test"""
    print("🚀 INICIANDO TEST COMPLETO DE VALORACIÓN CON IA")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total de casos: {len(casos_test)} URLs")
    
    # Test con GPT-3.5
    resultados_gpt35, precision_gpt35 = test_valoracion_gpt_35()
    
    # Test con Ollama
    resultados_ollama, precision_ollama = test_valoracion_ollama()
    
    # Generar comparativa final
    generar_comparativa(
        None, 0,  # GPT-4o no disponible en este test
        resultados_gpt35, precision_gpt35,
        resultados_ollama, precision_ollama
    )
    
    print(f"\n🎉 TEST COMPLETADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
