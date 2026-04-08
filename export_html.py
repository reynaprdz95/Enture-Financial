import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio


# =========================
# CONFIG
# =========================
ARCHIVO_EXCEL = "cartera.xlsx"
ARCHIVO_HTML = "reporte_cartera.html"

ENTURE_PRIMARY = "#0F766E"
ENTURE_PRIMARY_DARK = "#0B5D56"
ENTURE_ACCENT = "#14B8A6"
ENTURE_NAVY = "#0F172A"
ENTURE_GOLD = "#B89B5E"
ENTURE_BG = "#F4F7F9"
ENTURE_CARD = "#FFFFFF"
ENTURE_MUTED = "#64748B"
ENTURE_BORDER = "#D9E2EC"

PLOT_COLORS = [
    ENTURE_PRIMARY,
    ENTURE_ACCENT,
    ENTURE_GOLD,
    "#1D4ED8",
    "#7C3AED",
    "#E11D48",
]


# =========================
# HELPERS
# =========================
def limpiar_texto(texto: str) -> str:
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    for ch in [" ", "-", "/", ".", "(", ")", "%"]:
        texto = texto.replace(ch, "_")
    while "__" in texto:
        texto = texto.replace("__", "_")
    return texto.strip("_")


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [limpiar_texto(c) for c in df.columns]
    return df


def a_numero(serie: pd.Series) -> pd.Series:
    s = (
        serie.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(s, errors="coerce")


def normalizar_tasa(serie: pd.Series) -> pd.Series:
    s = a_numero(serie)
    if s.dropna().empty:
        return s
    if s.dropna().median() > 1:
        s = s / 100
    return s


def preparar_fechas(df: pd.DataFrame, columnas_fecha: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in columnas_fecha:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def weighted_avg(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = v.notna() & w.notna()
    if mask.sum() == 0 or w[mask].sum() == 0:
        return 0.0
    return float(np.average(v[mask], weights=w[mask]))


def fmt_money(x):
    if pd.isna(x):
        return "—"
    return f"${x:,.0f}"


def fmt_pct(x):
    if pd.isna(x):
        return "—"
    return f"{x:.2%}"


def fmt_days(x):
    if pd.isna(x):
        return "—"
    return f"{x:,.0f} días"


def fmt_date(x):
    if pd.isna(x):
        return "—"
    return pd.to_datetime(x).strftime("%d/%m/%Y")


def renombrar_aliases(df: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    df = df.copy()
    rename_map = {}
    for col in df.columns:
        if col in aliases and aliases[col] not in df.columns:
            rename_map[col] = aliases[col]
    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def parse_temporalidad_a_dias(valor):
    if pd.isna(valor):
        return np.nan
    texto = str(valor).strip().lower()
    if texto == "":
        return np.nan
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    numeros = re.findall(r"\d+", texto)
    n = float(numeros[0]) if numeros else np.nan

    if "dia" in texto:
        return n if not pd.isna(n) else np.nan
    if "semana" in texto:
        return n * 7 if not pd.isna(n) else 7
    if "quincena" in texto:
        return n * 15 if not pd.isna(n) else 15
    if "mes" in texto:
        return n * 30 if not pd.isna(n) else 30
    if "bimestre" in texto:
        return n * 60 if not pd.isna(n) else 60
    if "trimestre" in texto:
        return n * 90 if not pd.isna(n) else 90
    if "semestre" in texto:
        return n * 180 if not pd.isna(n) else 180
    if "ano" in texto or "año" in texto:
        return n * 360 if not pd.isna(n) else 360

    if not pd.isna(n):
        return n
    return np.nan


def dias_a_temporalidad(dias):
    if pd.isna(dias):
        return "—"
    dias = float(dias)
    if dias <= 7:
        return "Semanal"
    elif dias <= 15:
        return "Quincenal"
    elif dias <= 45:
        return "Mensual"
    elif dias <= 75:
        return "Bimestral"
    elif dias <= 120:
        return "Trimestral"
    elif dias <= 210:
        return "Semestral"
    elif dias <= 420:
        return "Anual"
    return f"{int(round(dias))} días"


def completar_plazo_dias(df, plazo_col, fecha_inicio_col, fecha_fin_col, temporalidad_col="temporalidad"):
    df = df.copy()

    if plazo_col not in df.columns:
        df[plazo_col] = np.nan

    df[plazo_col] = pd.to_numeric(df[plazo_col], errors="coerce")

    if temporalidad_col in df.columns:
        dias_temp = df[temporalidad_col].apply(parse_temporalidad_a_dias)
        mask = df[plazo_col].isna() | (df[plazo_col] <= 0)
        df.loc[mask, plazo_col] = dias_temp[mask]

    if fecha_inicio_col in df.columns and fecha_fin_col in df.columns:
        diff = (df[fecha_fin_col] - df[fecha_inicio_col]).dt.days
        mask = df[plazo_col].isna() | (df[plazo_col] <= 0)
        df.loc[mask, plazo_col] = diff[mask]

    df.loc[df[plazo_col] < 0, plazo_col] = np.nan
    return df


def completar_temporalidad(df, plazo_col="plazo_dias", temporalidad_col="temporalidad"):
    df = df.copy()
    if temporalidad_col not in df.columns:
        df[temporalidad_col] = pd.Series(pd.NA, index=df.index, dtype="object")
    else:
        df[temporalidad_col] = df[temporalidad_col].astype("object")
    if plazo_col not in df.columns:
        return df

    vacio = df[temporalidad_col].isna() | (df[temporalidad_col].astype(str).str.strip() == "")
    if vacio.any():
        df.loc[vacio, temporalidad_col] = df.loc[vacio, plazo_col].apply(dias_a_temporalidad).astype("object")
    return df


def construir_estatus_automatico(df, fecha_fin_col="fecha_vencimiento", estatus_col="estatus"):
    df = df.copy()
    if estatus_col not in df.columns:
        df[estatus_col] = np.nan

    hoy = pd.Timestamp.today().normalize()
    estatus_original = df[estatus_col].astype("string").fillna("").str.strip()
    estatus_lower = estatus_original.str.lower()

    estatus_cerrados = {
        "liquidado", "liquidada", "pagado", "pagada",
        "cerrado", "cerrada", "cancelado", "cancelada",
        "finalizado", "finalizada"
    }

    auto = np.where(
        df[fecha_fin_col].isna(),
        "Sin fecha",
        np.where(
            df[fecha_fin_col] < hoy,
            "Vencido",
            np.where(df[fecha_fin_col] == hoy, "Vence hoy", "Activo")
        )
    )

    df[estatus_col] = np.where(estatus_lower.isin(estatus_cerrados), estatus_original, auto)
    return df


def serie_vencimientos(df, fecha_col, monto_col, etiqueta):
    if df.empty or fecha_col not in df.columns or monto_col not in df.columns:
        return pd.DataFrame(columns=["mes", etiqueta])

    base = df[df[fecha_col].notna()].copy()
    if base.empty:
        return pd.DataFrame(columns=["mes", etiqueta])

    base["mes"] = base[fecha_col].dt.to_period("M").dt.to_timestamp()
    return base.groupby("mes")[monto_col].sum().reset_index().rename(columns={monto_col: etiqueta})


# =========================
# CARGA Y LIMPIEZA
# =========================
archivo = Path(ARCHIVO_EXCEL)
if not archivo.exists():
    raise FileNotFoundError(f"No encontré {ARCHIVO_EXCEL} en esta carpeta.")

hojas = pd.read_excel(archivo, sheet_name=None)
hojas = {limpiar_texto(k): normalizar_columnas(v) for k, v in hojas.items()}

if "inversionistas" not in hojas:
    raise ValueError("Falta la hoja 'inversionistas'.")
if "prestamos" not in hojas:
    raise ValueError("Falta la hoja 'prestamos'.")

inversionistas = hojas["inversionistas"].copy()
prestamos = hojas["prestamos"].copy()

aliases_inv = {
    "inversionista": "cliente_inversionista",
    "monto_inversion": "monto_invertido",
    "monto_de_inversion": "monto_invertido",
    "tasa_anual": "tasa_efectiva",
    "fecha_de_inicio": "fecha_inicio",
    "fecha_inicio": "fecha_inicio",
    "fecha_de_termino": "fecha_vencimiento",
    "fecha_termino": "fecha_vencimiento",
    "fecha_fin": "fecha_vencimiento",
}

aliases_pre = {
    "cliente": "cliente_credito",
    "prestamo": "monto_colocado",
    "monto_prestamo": "monto_colocado",
    "monto_de_prestamo": "monto_colocado",
    "tasa_anual": "tasa_colocacion",
    "fecha_de_inicio": "fecha_desembolso",
    "fecha_inicio": "fecha_desembolso",
    "fecha_de_termino": "fecha_vencimiento",
    "fecha_termino": "fecha_vencimiento",
    "fecha_fin": "fecha_vencimiento",
}

inversionistas = renombrar_aliases(inversionistas, aliases_inv)
prestamos = renombrar_aliases(prestamos, aliases_pre)

inversionistas = preparar_fechas(inversionistas, ["fecha_inicio", "fecha_vencimiento"])
prestamos = preparar_fechas(prestamos, ["fecha_desembolso", "fecha_vencimiento"])

for col in ["cliente_inversionista", "monto_invertido", "tasa_efectiva", "plazo_dias", "estatus", "temporalidad"]:
    if col not in inversionistas.columns:
        inversionistas[col] = np.nan

for col in ["cliente_credito", "monto_colocado", "tasa_colocacion", "plazo_dias", "estatus", "temporalidad"]:
    if col not in prestamos.columns:
        prestamos[col] = np.nan

inversionistas["monto_invertido"] = a_numero(inversionistas["monto_invertido"])
inversionistas["tasa_efectiva"] = normalizar_tasa(inversionistas["tasa_efectiva"])
inversionistas["plazo_dias"] = a_numero(inversionistas["plazo_dias"])

prestamos["monto_colocado"] = a_numero(prestamos["monto_colocado"])
prestamos["tasa_colocacion"] = normalizar_tasa(prestamos["tasa_colocacion"])
prestamos["plazo_dias"] = a_numero(prestamos["plazo_dias"])

inversionistas = completar_plazo_dias(inversionistas, "plazo_dias", "fecha_inicio", "fecha_vencimiento")
prestamos = completar_plazo_dias(prestamos, "plazo_dias", "fecha_desembolso", "fecha_vencimiento")

inversionistas = completar_temporalidad(inversionistas, "plazo_dias", "temporalidad")
prestamos = completar_temporalidad(prestamos, "plazo_dias", "temporalidad")

inversionistas = construir_estatus_automatico(inversionistas)
prestamos = construir_estatus_automatico(prestamos)

# =========================
# KPIS
# =========================
num_inversionistas = inversionistas["cliente_inversionista"].nunique()
total_fondeo = inversionistas["monto_invertido"].sum()
tasa_fondeo = weighted_avg(inversionistas["tasa_efectiva"], inversionistas["monto_invertido"])
plazo_fondeo = weighted_avg(inversionistas["plazo_dias"], inversionistas["monto_invertido"])

num_clientes = prestamos["cliente_credito"].nunique()
total_colocado = prestamos["monto_colocado"].sum()
tasa_colocacion = weighted_avg(prestamos["tasa_colocacion"], prestamos["monto_colocado"])
plazo_colocacion = weighted_avg(prestamos["plazo_dias"], prestamos["monto_colocado"])

spread = tasa_colocacion - tasa_fondeo
margen_estimado = (total_colocado * tasa_colocacion) - (total_fondeo * tasa_fondeo)

# =========================
# GRÁFICAS
# =========================
top_inv = (
    inversionistas.groupby("cliente_inversionista", dropna=False)["monto_invertido"]
    .sum().reset_index().sort_values("monto_invertido", ascending=False).head(10)
)

top_pre = (
    prestamos.groupby("cliente_credito", dropna=False)["monto_colocado"]
    .sum().reset_index().sort_values("monto_colocado", ascending=False).head(10)
)

timeline_inv = serie_vencimientos(inversionistas, "fecha_vencimiento", "monto_invertido", "Fondeo")
timeline_pre = serie_vencimientos(prestamos, "fecha_vencimiento", "monto_colocado", "Colocación")
timeline = pd.merge(timeline_inv, timeline_pre, on="mes", how="outer").fillna(0).sort_values("mes")

fig1 = px.bar(
    top_inv,
    x="cliente_inversionista",
    y="monto_invertido",
    title="Top inversionistas por monto",
    color_discrete_sequence=[ENTURE_PRIMARY],
)

fig2 = px.bar(
    top_pre,
    x="cliente_credito",
    y="monto_colocado",
    title="Top clientes por monto colocado",
    color_discrete_sequence=[ENTURE_NAVY],
)

if not timeline.empty:
    timeline_melt = timeline.melt(
        id_vars="mes",
        value_vars=["Fondeo", "Colocación"],
        var_name="Tipo",
        value_name="Monto",
    )
    fig3 = px.line(
        timeline_melt,
        x="mes",
        y="Monto",
        color="Tipo",
        markers=True,
        title="Timeline de vencimientos",
        color_discrete_sequence=[ENTURE_PRIMARY, ENTURE_GOLD],
    )
else:
    fig3 = px.line(title="Timeline de vencimientos")

for fig in [fig1, fig2, fig3]:
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=420,
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title=None,
    )

grafica_1 = pio.to_html(fig1, full_html=False, include_plotlyjs=True)
grafica_2 = pio.to_html(fig2, full_html=False, include_plotlyjs=False)
grafica_3 = pio.to_html(fig3, full_html=False, include_plotlyjs=False)

# =========================
# TABLAS
# =========================
detalle_inv = pd.DataFrame({
    "Inversionista": inversionistas["cliente_inversionista"],
    "Monto Inversión": inversionistas["monto_invertido"].map(fmt_money),
    "Tasa Anual": inversionistas["tasa_efectiva"].map(fmt_pct),
    "Fecha Inicio": inversionistas["fecha_inicio"].map(fmt_date),
    "Fecha de Término": inversionistas["fecha_vencimiento"].map(fmt_date),
    "Temporalidad": inversionistas["temporalidad"],
    "Estatus": inversionistas["estatus"],
}).head(30)

detalle_pre = pd.DataFrame({
    "Cliente": prestamos["cliente_credito"],
    "Préstamo": prestamos["monto_colocado"].map(fmt_money),
    "Tasa Anual": prestamos["tasa_colocacion"].map(fmt_pct),
    "Fecha Inicio": prestamos["fecha_desembolso"].map(fmt_date),
    "Fecha de Término": prestamos["fecha_vencimiento"].map(fmt_date),
    "Temporalidad": prestamos["temporalidad"],
    "Estatus": prestamos["estatus"],
}).head(30)

tabla_inv_html = detalle_inv.to_html(index=False, classes="tabla", border=0)
tabla_pre_html = detalle_pre.to_html(index=False, classes="tabla", border=0)

# =========================
# HTML FINAL
# =========================
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reporte de Cartera Financiera</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        background: {ENTURE_BG};
        color: {ENTURE_NAVY};
    }}
    .wrap {{
        max-width: 1400px;
        margin: 0 auto;
        padding: 24px;
    }}
    .hero {{
        background: linear-gradient(135deg, {ENTURE_NAVY} 0%, {ENTURE_PRIMARY_DARK} 100%);
        color: white;
        padding: 28px;
        border-radius: 22px;
        margin-bottom: 20px;
    }}
    .hero h1 {{
        margin: 0 0 8px 0;
        font-size: 32px;
    }}
    .hero p {{
        margin: 0;
        opacity: 0.92;
    }}
    .grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 14px;
        margin-bottom: 20px;
    }}
    .card {{
        background: white;
        border: 1px solid {ENTURE_BORDER};
        border-left: 6px solid {ENTURE_PRIMARY};
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(15,23,42,0.05);
    }}
    .label {{
        color: {ENTURE_MUTED};
        font-size: 14px;
        margin-bottom: 8px;
        font-weight: 700;
    }}
    .value {{
        font-size: 28px;
        font-weight: 800;
    }}
    .section {{
        margin-top: 26px;
        margin-bottom: 10px;
        font-size: 22px;
        font-weight: 800;
    }}
    .subgrid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 18px;
        margin-bottom: 18px;
    }}
    .chart-card, .table-card {{
        background: white;
        border: 1px solid {ENTURE_BORDER};
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 8px 20px rgba(15,23,42,0.05);
    }}
    .tabla {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }}
    .tabla th {{
        background: {ENTURE_NAVY};
        color: white;
        text-align: left;
        padding: 10px;
    }}
    .tabla td {{
        padding: 10px;
        border-bottom: 1px solid {ENTURE_BORDER};
    }}
    .tabla tr:nth-child(even) {{
        background: #F8FAFC;
    }}
    @media (max-width: 1100px) {{
        .grid {{ grid-template-columns: repeat(2, 1fr); }}
        .subgrid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 700px) {{
        .grid {{ grid-template-columns: 1fr; }}
    }}
</style>
</head>
<body>
<div class="wrap">
    <div class="hero">
        <h1>Reporte de Cartera Financiera</h1>
        <p>Fondeo, colocación, concentración y vencimientos.</p>
    </div>

    <div class="grid">
        <div class="card"><div class="label">Número de inversionistas</div><div class="value">{num_inversionistas:,.0f}</div></div>
        <div class="card"><div class="label">Total fondeo</div><div class="value">{fmt_money(total_fondeo)}</div></div>
        <div class="card"><div class="label">Tasa promedio fondeo</div><div class="value">{fmt_pct(tasa_fondeo)}</div></div>
        <div class="card"><div class="label">Plazo promedio fondeo</div><div class="value">{fmt_days(plazo_fondeo)}</div></div>
    </div>

    <div class="grid">
        <div class="card"><div class="label">Número de clientes crédito</div><div class="value">{num_clientes:,.0f}</div></div>
        <div class="card"><div class="label">Total colocado</div><div class="value">{fmt_money(total_colocado)}</div></div>
        <div class="card"><div class="label">Tasa promedio colocación</div><div class="value">{fmt_pct(tasa_colocacion)}</div></div>
        <div class="card"><div class="label">Spread financiero</div><div class="value">{fmt_pct(spread)}</div></div>
    </div>

    <div class="grid">
        <div class="card"><div class="label">Plazo promedio colocación</div><div class="value">{fmt_days(plazo_colocacion)}</div></div>
        <div class="card"><div class="label">Margen anual estimado</div><div class="value">{fmt_money(margen_estimado)}</div></div>
        <div class="card"><div class="label">Archivo fuente</div><div class="value" style="font-size:18px;">{ARCHIVO_EXCEL}</div></div>
        <div class="card"><div class="label">Generado</div><div class="value" style="font-size:18px;">{pd.Timestamp.today().strftime("%d/%m/%Y %H:%M")}</div></div>
    </div>

    <div class="section">Gráficas</div>
    <div class="subgrid">
        <div class="chart-card">{grafica_1}</div>
        <div class="chart-card">{grafica_2}</div>
    </div>
    <div class="chart-card">{grafica_3}</div>

    <div class="section">Detalle de inversionistas</div>
    <div class="table-card">{tabla_inv_html}</div>

    <div class="section">Detalle de clientes / préstamos</div>
    <div class="table-card">{tabla_pre_html}</div>
</div>
</body>
</html>
"""

with open(ARCHIVO_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Listo. Se generó el archivo: {ARCHIVO_HTML}")
