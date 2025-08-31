#!/usr/bin/env python3
"""
Script de testing para la función clasificar_tema_con_ia con datos reales.
Prueba la clasificación de temas usando noticias reales y temas reales de la app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from O_Utils_GPT import clasificar_tema_con_ia
from Z_Utils import get_texto_plano_from_link, get_html_object_from_link
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_clasificar_tema_ia_real():
    """
    Función principal de testing para clasificar_tema_con_ia con datos reales
    """
    print("🧪 TESTING: clasificar_tema_con_ia (DATOS REALES - GPT-4o)")
    print("=" * 80)
    
    # Lista de temas reales de la app
    lista_temas = [
        "Entre el varón alemán y el amante argentino: peripecias de una mujer liberal de los años 20",
        "Juventus Lyrica",
        "¡URGENTE!",
        "34° Fiesta Nacional del Chamamé",
        "40 años Barrio Chino",
        "40 años de Camila",
        "9 de Julio en la Feria de Mataderos",
        "Abasto Barrio Cultural",
        "BAFICI",
        "Recorrido por eventos y estrenos",
        "Actividades programadas",
        "Anuncio de obras CCGSM",
        "Centenario elencos estables",
        "Premios municipales y nacionales"
    ]
    
    # Casos de prueba con URLs y temas reales asignados por humanos
    casos_test = [
        {
            "nombre": "Caso 1: Mujer liberal años 20",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=83794060",
            "tema_esperado": "Entre el varón alemán y el amante argentino: peripecias de una mujer liberal de los años 20",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 2: Juventus Lyrica",
            "url": "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=86687392",
            "tema_esperado": "Juventus Lyrica",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 3: URGENTE",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24340866",
            "tema_esperado": "¡URGENTE!",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 4: Fiesta Nacional del Chamamé",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89356448",
            "tema_esperado": "34° Fiesta Nacional del Chamamé",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 5: Barrio Chino",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85875989",
            "tema_esperado": "40 años Barrio Chino",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 6: 40 años de Camila",
            "url": "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=87565297",
            "tema_esperado": "40 años de Camila",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 7: Feria de Mataderos",
            "url": "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=85044950",
            "tema_esperado": "9 de Julio en la Feria de Mataderos",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 8: Abasto Barrio Cultural",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=86911152",
            "tema_esperado": "Abasto Barrio Cultural",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 9: BAFICI",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=20340562",
            "tema_esperado": "BAFICI",
            "tipo_publicacion": "Nota"
        },

        {
            "nombre": "Caso 10: Actividades programadas",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19581596",
            "tema_esperado": "Actividades programadas",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 11: Anuncio de obras CCGSM",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19246424",
            "tema_esperado": "Anuncio de obras CCGSM",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 12: Centenario elencos estables",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=15633461",
            "tema_esperado": "Centenario elencos estables",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 13: Fiesta Nacional del Chamamé (2)",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89317383",
            "tema_esperado": "34° Fiesta Nacional del Chamamé",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 14: Fiesta Nacional del Chamamé (3)",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=89311718",
            "tema_esperado": "34° Fiesta Nacional del Chamamé",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 15: 9 de Julio Feria Mataderos (2)",
            "url": "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84985229",
            "tema_esperado": "9 de Julio en la Feria de Mataderos",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 16: 9 de Julio Feria Mataderos (3)",
            "url": "http://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=84990078",
            "tema_esperado": "9 de Julio en la Feria de Mataderos",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 17: BAFICI (2)",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=19619285",
            "tema_esperado": "BAFICI",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 18: Premios municipales y nacionales",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=15613613",
            "tema_esperado": "Premios municipales y nacionales",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 19: ¡URGENTE! (2)",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24338399",
            "tema_esperado": "¡URGENTE!",
            "tipo_publicacion": "Nota"
        },
        {
            "nombre": "Caso 20: ¡URGENTE! (3)",
            "url": "https://culturagcba.clientes.ejes.com/noticia_completa.cfm?id=24262318",
            "tema_esperado": "¡URGENTE!",
            "tipo_publicacion": "Nota"
        }
    ]
    
    print(f"📋 Lista de temas disponibles: {len(lista_temas)} temas")
    print(f"🔢 Total de casos a probar: {len(casos_test)}")
    print()
    
    # Contadores
    exitosos = 0
    fallidos = 0
    errores_procesamiento = 0
    
    # Probar cada caso
    for i, caso in enumerate(casos_test, 1):
        print(f"📝 CASO {i}: {caso['nombre']}")
        print(f"   URL: {caso['url']}")
        print(f"   Tema esperado: {caso['tema_esperado']}")
        print(f"   Tipo: {caso['tipo_publicacion']}")
        
        try:
            # Procesar el link para obtener el texto
            print(f"   🔍 Procesando link...")
            texto_noticia = get_texto_plano_from_link(caso['url'])
            
            if not texto_noticia or len(texto_noticia.strip()) < 50:
                print(f"   ⚠️  Texto insuficiente o vacío")
                errores_procesamiento += 1
                continue
            
            print(f"   📄 Texto obtenido: {len(texto_noticia)} caracteres")
            
            # Clasificar tema usando la función de producción (con Ollama)
            resultado = clasificar_tema_con_ia(
                texto=texto_noticia,
                lista_temas=lista_temas,
                tipo_publicacion=caso['tipo_publicacion'],
                gpt_active=True
            )
            
            print(f"   🎯 RESULTADO: {resultado}")
            
            # Validar resultado
            if resultado == caso['tema_esperado']:
                print(f"   ✅ CORRECTO")
                exitosos += 1
            else:
                print(f"   ❌ INCORRECTO")
                print(f"      Esperado: {caso['tema_esperado']}")
                print(f"      Obtenido: {resultado}")
                fallidos += 1
            
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            errores_procesamiento += 1
        
        print("-" * 80)
    
    # Resumen final
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Casos exitosos: {exitosos}")
    print(f"❌ Casos fallidos: {fallidos}")
    print(f"⚠️  Errores de procesamiento: {errores_procesamiento}")
    print(f"📈 Precisión: {(exitosos / (exitosos + fallidos)) * 100:.1f}%" if (exitosos + fallidos) > 0 else "N/A")
    
    if fallidos == 0 and errores_procesamiento == 0:
        print("🎉 ¡TODOS LOS CASOS PASARON EXITOSAMENTE!")
    elif fallidos == 0:
        print("🎯 Todos los casos procesados fueron correctos")
    else:
        print(f"⚠️  {fallidos} casos necesitan revisión")
    
    return exitosos, fallidos, errores_procesamiento

if __name__ == "__main__":
    print("🚀 INICIANDO TESTING DE CLASIFICACIÓN DE TEMAS CON DATOS REALES - GPT-4o")
    print("=" * 80)
    
    # Verificar configuración
    print("🔑 Verificando configuración de GPT...")
    
    # Ejecutar tests principales
    exitosos, fallidos, errores = test_clasificar_tema_ia_real()
    
    print("\n🏁 TESTING COMPLETADO")
    print(f"📊 Resultado final: {exitosos} exitosos, {fallidos} fallidos, {errores} errores")
