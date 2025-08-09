"""
Test de clasificación de TEMA leyendo directamente el Excel base (EXCEL_URL_PATH).

Supuestos del Excel:
- Columna A: LINK (a procesar)
- Columna B: TEMA_HUMANO (etiqueta humana)
- Resto de columnas: ignoradas

Flujo:
- Lee los links y descarga texto plano usando Z.get_texto_plano_from_link
- Carga lista de temas desde Testing/temas_app.txt
- Ejecuta Oll.matchear_tema_con_fallback(texto, lista_temas, tipo_publicacion)
  Para este test, el tipo_publicacion se deja en None (sin forzar Agenda)
- Compara contra TEMA_HUMANO
- Exporta resultados y métricas a Data_Results/Test_Tema_Excel_Resultados.xlsx
"""

import os
import sys
from datetime import timedelta, datetime
import re
import time
import pandas as pd

# Importar módulos del proyecto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

import Z_Utils as Z
import O_Utils_Ollama as Oll
import O_Utils_GPT as Gpt

# Ruta del Excel base (la misma que usa main)
EXCEL_URL_PATH = os.path.join(ROOT, "DataCollected/Import_Links_Procesado_Completo.xlsx")
TEMAS_PATH = os.path.join(ROOT, "Testing/temas_app.txt")
OUTPUT_PATH = os.path.join(ROOT, "Data_Results/Test_Tema_Excel_Resultados.xlsx")


def _normalizar_fecha_str(fecha_raw: str) -> str | None:
    """Convierte 'd/m/yyyy' o 'dd/mm/yyyy' (también con '-' o '.') en 'YYYY-MM-DD'.
    Acepta años de 2 o 4 dígitos; para 2 dígitos, asume 20xx si <=30, si no 19xx.
    Devuelve None si no parsea.
    """
    if not fecha_raw:
        return None
    fecha_raw = fecha_raw.strip().replace(" ", "")
    # Reemplazar separadores comunes por '/'
    fecha_raw = re.sub(r"[\-.]", "/", fecha_raw)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})", fecha_raw)
    if not m:
        # Intento ISO directo
        try:
            datetime.fromisoformat(fecha_raw)
            return fecha_raw
        except Exception:
            return None
    d, mth, y = m.groups()
    if len(y) == 2:
        yi = int(y)
        y = f"20{y}" if yi <= 30 else f"19{y}"
    return f"{y}-{mth.zfill(2)}-{d.zfill(2)}"


def cargar_lista_temas(path: str) -> tuple[list, dict]:
    """Lee temas desde txt. Soporta líneas 'Tema;Fecha'.
    Retorna (lista_temas, tema_a_fecha_iso).
    """
    temas: list[str] = []
    tema_a_fecha: dict[str, str] = {}
    try:
        # Regex robusto: capta tema y fecha al final opcional (dd/mm/yyyy o variantes)
        # Ejemplos válidos: "Tema;29/4/2025", "Tema  -  05-07-2024", "Tema 05.07.2024"
        pat = re.compile(r"^(?P<tema>.+?)[\s;:|\t\-—–]*?(?P<fecha>\d{1,2}[\/.\-]\d{1,2}[\/.\-]\d{2,4})?\s*$")

        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                m = pat.match(line)
                if not m:
                    continue
                nombre = m.group("tema").strip()
                fecha = m.group("fecha")

                if nombre and nombre not in temas:
                    temas.append(nombre)
                if fecha:
                    iso = _normalizar_fecha_str(fecha)
                    if iso:
                        tema_a_fecha[nombre] = iso
        return temas, tema_a_fecha
    except Exception as e:
        print(f"❌ Error cargando lista de temas: {e}")
        return ["Actividades programadas"], {}


def cargar_links_y_tema_original(path_excel: str) -> pd.DataFrame:
    """Lee la 1ª y 2ª columna del Excel base: LINK y TEMA_ORIGINAL."""
    df = pd.read_excel(path_excel, sheet_name=0, header=0)
    if df.shape[1] < 2:
        raise ValueError("El Excel necesita al menos 2 columnas: LINK y TEMA_HUMANO")
    out = pd.DataFrame({
        "LINK": df.iloc[:, 0].astype(str).str.strip(),
        "TEMA_ORIGINAL": df.iloc[:, 1].astype(str).str.strip(),
    })
    return out


def procesar_y_clasificar(df_links: pd.DataFrame, lista_temas: list) -> pd.DataFrame:
    """
    Procedural y reutilizando funciones existentes del proyecto:
    - Z.get_texto_plano_from_link
    - Z.marcar_o_valorar_con_ia + Oll.matchear_tema_con_fallback
    """
    df = df_links.copy()
    # Reutilizamos el extractor del proyecto
    df["TEXTO_PLANO"] = df["LINK"].apply(Z.get_texto_plano_from_link)
    # Reutilizamos el clasificador de temas del proyecto (sin crear lógica nueva)
    df["TEMA"] = df["TEXTO_PLANO"].apply(
        lambda x: Z.marcar_o_valorar_con_ia(
            x,
            lambda t: Oll.matchear_tema_con_fallback(t, lista_temas, None),
            14900,
        )
    )
    return df


def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ES_CORRECTO"] = df["TEMA"].fillna("") == df["TEMA_ORIGINAL"].fillna("")
    total = len(df)
    correctos = int(df["ES_CORRECTO"].sum())
    incorrectos = total - correctos
    acc = (correctos / total * 100) if total else 0.0
    resumen = pd.DataFrame([
        {"métrica": "total", "valor": total},
        {"métrica": "correctos", "valor": correctos},
        {"métrica": "incorrectos", "valor": incorrectos},
        {"métrica": "accuracy_%", "valor": round(acc, 1)},
    ])
    return resumen


def main():
    t0 = time.time()
    print("🧪 Test TEMA sobre Excel base (EXCEL_URL_PATH)")
    print(f"Excel: {EXCEL_URL_PATH}")

    # 1. Cargar datos
    lista_temas, tema_a_fecha = cargar_lista_temas(TEMAS_PATH)
    print(f"Temas cargados: {len(lista_temas)} | con fecha: {len(tema_a_fecha)}")
    df_links = cargar_links_y_tema_original(EXCEL_URL_PATH)
    print(f"Links: {len(df_links)}")

    # 2. Obtener texto
    # Intentar anexar fecha y texto desde un Excel procesado previo para evitar scraping
    prev_path = os.path.join(ROOT, "Data_Results/Batch_URLS_Procesadas.xlsx")
    if os.path.exists(prev_path):
        try:
            prev = pd.read_excel(prev_path)
            cols = set(prev.columns)
            use_cols = ["LINK"]
            if "FECHA" in cols:
                use_cols.append("FECHA")
            if "TEXTO_PLANO" in cols:
                use_cols.append("TEXTO_PLANO")
            df_links = df_links.merge(prev[use_cols], on="LINK", how="left")
        except Exception:
            pass

    df = df_links.copy()
    # Si tenemos TEXTO_PLANO cacheado, usarlo; completar solo lo faltante
    if "TEXTO_PLANO" not in df.columns:
        df["TEXTO_PLANO"] = None
    faltante = df["TEXTO_PLANO"].isna() | (df["TEXTO_PLANO"] == "")
    if faltante.any():
        df.loc[faltante, "TEXTO_PLANO"] = df.loc[faltante, "LINK"].apply(Z.get_texto_plano_from_link)

    # Variante con fechas (desempate temporal)
    df["TEMA_CON_FECHA"] = df.apply(
        lambda row: Z.marcar_o_valorar_con_ia(
            row["TEXTO_PLANO"],
            lambda t: Oll.matchear_tema_con_fallback(
                t,
                lista_temas,
                None,
                fecha_noticia=row.get("FECHA"),
                tema_a_fecha=tema_a_fecha,
            ),
            14900,
        ),
        axis=1,
    )

    # Variante sin fechas (baseline histórica)
    df["TEMA_SIN_FECHA"] = df["TEXTO_PLANO"].apply(
        lambda t: Z.marcar_o_valorar_con_ia(
            t,
            lambda x: Oll.matchear_tema_sin_fecha(x, lista_temas, None),
            14900,
        )
    )

    # Variante GPT (con fallback interno a Ollama). Usa mismo contexto temporal que la con-fecha
    df["TEMA_GPT"] = df.apply(
        lambda row: Z.marcar_o_valorar_con_ia(
            row["TEXTO_PLANO"],
            lambda t: Gpt.clasificar_tema_con_ia(
                texto=t,
                lista_temas=lista_temas,
                tipo_publicacion=None,
                fecha_noticia=row.get("FECHA"),
                tema_a_fecha=tema_a_fecha,
                gpt_active=True,
            ),
            14900,
        ),
        axis=1,
    )

    # 4. Métricas
    # Calcular métricas comparativas
    df_comp = df.copy()
    df_comp["ES_CORRECTO_CON_FECHA"] = df_comp["TEMA_CON_FECHA"].fillna("") == df_comp["TEMA_ORIGINAL"].fillna("")
    df_comp["ES_CORRECTO_SIN_FECHA"] = df_comp["TEMA_SIN_FECHA"].fillna("") == df_comp["TEMA_ORIGINAL"].fillna("")
    df_comp["ES_CORRECTO_GPT"] = df_comp["TEMA_GPT"].fillna("") == df_comp["TEMA_ORIGINAL"].fillna("")
    total = len(df_comp)
    c1 = int(df_comp["ES_CORRECTO_CON_FECHA"].sum())
    c0 = int(df_comp["ES_CORRECTO_SIN_FECHA"].sum())
    cgpt = int(df_comp["ES_CORRECTO_GPT"].sum())
    acc1 = (c1 / total * 100) if total else 0.0
    acc0 = (c0 / total * 100) if total else 0.0
    accg = (cgpt / total * 100) if total else 0.0
    resumen = pd.DataFrame([
        {"métrica": "total", "valor": total},
        {"métrica": "correctos_con_fecha", "valor": c1},
        {"métrica": "accuracy_con_fecha_%", "valor": round(acc1, 1)},
        {"métrica": "correctos_sin_fecha", "valor": c0},
        {"métrica": "accuracy_sin_fecha_%", "valor": round(acc0, 1)},
        {"métrica": "correctos_gpt", "valor": cgpt},
        {"métrica": "accuracy_gpt_%", "valor": round(accg, 1)},
    ])

    # 5. Exportar
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as w:
        resumen.to_excel(w, index=False, sheet_name="resumen")
        df.to_excel(w, index=False, sheet_name="detalles")

    t1 = time.time()
    print(resumen.to_string(index=False))
    print(f"✅ Exportado a: {OUTPUT_PATH}")
    print(f"⏱ Tiempo: {str(timedelta(seconds=int(t1 - t0)))}")


if __name__ == "__main__":
    main()


