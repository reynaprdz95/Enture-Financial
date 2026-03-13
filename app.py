import re
import unicodedata
from io import BytesIO

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Análisis de Cartera Financiera', page_icon='📊', layout='wide', initial_sidebar_state='expanded')

ENTURE_PRIMARY = '#B03927'
ENTURE_PRIMARY_DARK = '#4C0C05'
ENTURE_ACCENT = '#E57A2E'
ENTURE_NAVY = '#181F30'
ENTURE_GOLD = '#C96C2B'
ENTURE_BG = '#F6F2EF'
ENTURE_CARD = '#FFFFFF'
ENTURE_MUTED = '#6B7280'
ENTURE_BORDER = '#DDD6CF'
ENTURE_SUCCESS = '#2E8B57'
ENTURE_WARNING = '#D97706'
ENTURE_DANGER = '#B03927'

PLOT_COLORS = [
    ENTURE_PRIMARY, ENTURE_ACCENT, ENTURE_NAVY, ENTURE_GOLD,
    '#9F2D20', '#C86428', '#2A3348', '#7A1B10'
]
PLOT_CONFIG = {'displayModeBar': False, 'displaylogo': False, 'responsive': True}


def inject_custom_css():
    st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(180deg, #F8FAFC 0%, {ENTURE_BG} 100%); }}
    .block-container {{ padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1500px; }}
    [data-testid='stSidebar'] {{ background: linear-gradient(180deg, {ENTURE_NAVY} 0%, #132238 100%); }}
    [data-testid='stSidebar'] * {{ color: #F8FAFC !important; }}
    .hero-card {{ background: linear-gradient(135deg, {ENTURE_NAVY} 0%, {ENTURE_PRIMARY_DARK} 100%); color: white; padding: 1.5rem 1.7rem; border-radius: 22px; margin-bottom: 1rem; }}
    .hero-eyebrow {{ font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; color: rgba(255,255,255,.78); font-weight:700; }}
    .hero-title {{ font-size: 2rem; font-weight: 800; margin: .2rem 0 0 0; }}
    .hero-subtitle {{ margin-top: .55rem; color: rgba(255,255,255,.90); font-size: .98rem; }}
    .info-pill-row {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:.85rem; }}
    .info-pill {{ background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.12); color:white; padding:10px 14px; border-radius:999px; font-size:.88rem; }}
    .section-title {{ font-size:1.05rem; font-weight:800; color:{ENTURE_NAVY}; margin-top:.25rem; margin-bottom:.65rem; }}
    .mini-note {{ color:{ENTURE_MUTED}; font-size:.88rem; margin-bottom:.5rem; }}
    [data-testid='stMetric'] {{ background:{ENTURE_CARD}; border:1px solid {ENTURE_BORDER}; border-left:5px solid {ENTURE_PRIMARY}; padding:16px 16px 12px 16px; border-radius:18px; box-shadow:0 10px 25px rgba(15,23,42,.05); min-height:118px; }}
    [data-testid='stMetricLabel'] {{ color:{ENTURE_MUTED}; font-weight:700; }}
    [data-testid='stMetricValue'] {{ color:{ENTURE_NAVY}; font-weight:800; }}
    .alert-card {{ background:{ENTURE_CARD}; border-radius:16px; padding:14px 16px; border:1px solid {ENTURE_BORDER}; margin-bottom:10px; }}
    .alert-error {{ border-left:5px solid {ENTURE_DANGER}; }}
    .alert-warning {{ border-left:5px solid {ENTURE_WARNING}; }}
    .alert-success {{ border-left:5px solid {ENTURE_SUCCESS}; }}
    .alert-title {{ font-weight:800; color:{ENTURE_NAVY}; margin-bottom:4px; }}
    .alert-text {{ color:{ENTURE_MUTED}; font-size:.92rem; }}
    .stTabs [data-baseweb='tab-list'] {{ gap: 8px; }}
    .stTabs [data-baseweb='tab'] {{ background: rgba(255,255,255,.65); border:1px solid {ENTURE_BORDER}; border-radius:12px; padding:10px 16px; font-weight:700; color:{ENTURE_NAVY}; }}
    .stTabs [aria-selected='true'] {{ background: linear-gradient(135deg, {ENTURE_PRIMARY} 0%, {ENTURE_PRIMARY_DARK} 100%) !important; color:white !important; border-color:transparent !important; }}
    .footer-note {{ color:{ENTURE_MUTED}; font-size:.85rem; margin-top:1rem; }}
    .narrative-band {{ background:#EAF1FB; border:1px solid #D5E0F3; color:#1356A2; padding:14px 16px; border-radius:16px; margin: 0.35rem 0 1rem 0; font-size: 0.96rem; line-height: 1.45; }}
    .premium-wrap {{ overflow-x:auto; margin-bottom: 1rem; }}
    table.premium-table {{ border-collapse: separate; border-spacing: 0; width:100%; font-size: 0.94rem; background:white; border:1px solid {ENTURE_BORDER}; border-radius:14px; overflow:hidden; }}
    table.premium-table thead th {{ position: sticky; top: 0; background: #F8FAFC; color: {ENTURE_NAVY}; font-weight: 800; z-index: 1; border-bottom: 1px solid {ENTURE_BORDER}; }}
    table.premium-table th, table.premium-table td {{ padding: 10px 12px; text-align:left; border-bottom: 1px solid #EEF2F7; }}
    table.premium-table tbody tr:nth-child(even) {{ background: #FBFCFE; }}
    table.premium-table tbody tr:hover {{ background: #F5F8FC; }}
    table.premium-table tbody tr.total-row {{ background: #FFF7ED !important; font-weight: 800; color: {ENTURE_NAVY}; }}
    </style>
    """, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class='hero-card'>
      <div class='hero-eyebrow'>ENTURE · Financial Intelligence</div>
      <div class='hero-title'>Análisis de Cartera de Inversionistas y Colocación</div>
      <div class='hero-subtitle'>Dashboard ejecutivo y operativo para monitorear fondeo, colocación, vencimientos, concentración, spreads y programación de pagos y cobros.</div>
      <div class='info-pill-row'>
        <div class='info-pill'>Fondeo</div><div class='info-pill'>Colocación</div><div class='info-pill'>Vencimientos</div>
        <div class='info-pill'>Concentración</div><div class='info-pill'>Tesorería</div><div class='info-pill'>Calendario de flujos</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def section_title(title: str, note: str | None = None):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if note:
        st.markdown(f"<div class='mini-note'>{note}</div>", unsafe_allow_html=True)


def render_alert_box(level: str, title: str, text: str):
    css = 'alert-success'
    if level == 'error':
        css = 'alert-error'
    elif level == 'warning':
        css = 'alert-warning'
    st.markdown(f"<div class='alert-card {css}'><div class='alert-title'>{title}</div><div class='alert-text'>{text}</div></div>", unsafe_allow_html=True)


def render_narrative_band(text: str):
    st.markdown(f"<div class='narrative-band'>{text}</div>", unsafe_allow_html=True)


def add_display_total_row(display_df: pd.DataFrame, label_col: str, formatted_values: dict, label: str = 'TOTAL') -> pd.DataFrame:
    if display_df.empty:
        return display_df
    row = {col: '' for col in display_df.columns}
    row[label_col] = label
    row.update(formatted_values)
    out = pd.concat([display_df, pd.DataFrame([row])], ignore_index=True)
    return out


def render_premium_table(df: pd.DataFrame):
    if df is None or df.empty:
        st.info('Sin información para mostrar.')
        return
    html = df.to_html(index=False, escape=False, classes='premium-table')
    html = html.replace('<tr>\n      <td>TOTAL</td>', '<tr class="total-row">\n      <td>TOTAL</td>')
    st.markdown(f"<div class='premium-wrap'>{html}</div>", unsafe_allow_html=True)


inject_custom_css(); render_hero()


def limpiar_texto(texto: str) -> str:
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    for ch in [' ', '-', '/', '.', '(', ')', '%']:
        texto = texto.replace(ch, '_')
    while '__' in texto:
        texto = texto.replace('__', '_')
    return texto.strip('_')


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy(); df.columns = [limpiar_texto(c) for c in df.columns]; return df


def a_numero(serie: pd.Series) -> pd.Series:
    if serie is None:
        return pd.Series(dtype='float64')
    s = serie.astype(str).str.replace(',', '', regex=False).str.replace('$', '', regex=False).str.replace('%', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce')


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
            df[c] = pd.to_datetime(df[c], errors='coerce')
    return df


def weighted_avg(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors='coerce')
    w = pd.to_numeric(weights, errors='coerce')
    mask = v.notna() & w.notna()
    if mask.sum() == 0 or w[mask].sum() == 0:
        return 0.0
    return float(np.average(v[mask], weights=w[mask]))


def nombre_mes_es(fecha) -> str:
    meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    fecha = pd.Timestamp(fecha)
    return f"{meses[fecha.month - 1]} {fecha.year}"


def obtener_mes_actual_bounds(fecha_ref=None):
    ref = pd.Timestamp.today().normalize() if fecha_ref is None else pd.Timestamp(fecha_ref).normalize()
    mes_inicio = ref.replace(day=1)
    mes_fin = mes_inicio + pd.offsets.MonthEnd(1)
    return mes_inicio, mes_fin


def dias_operacion_en_mes(fecha_inicio, fecha_fin, mes_inicio, mes_fin) -> int:
    if pd.isna(fecha_inicio) and pd.isna(fecha_fin):
        return 0
    fecha_inicio = mes_inicio if pd.isna(fecha_inicio) else pd.Timestamp(fecha_inicio).normalize()
    fecha_fin = mes_fin if pd.isna(fecha_fin) else pd.Timestamp(fecha_fin).normalize()
    inicio = max(fecha_inicio, mes_inicio)
    fin = min(fecha_fin, mes_fin)
    if fin < inicio:
        return 0
    return int((fin - inicio).days + 1)


def esta_activa_en_mes(fecha_inicio, fecha_fin, mes_inicio, mes_fin) -> bool:
    if pd.isna(fecha_inicio) and pd.isna(fecha_fin):
        return False
    fecha_inicio = mes_inicio if pd.isna(fecha_inicio) else pd.Timestamp(fecha_inicio).normalize()
    fecha_fin = mes_fin if pd.isna(fecha_fin) else pd.Timestamp(fecha_fin).normalize()
    return not (fecha_fin < mes_inicio or fecha_inicio > mes_fin)


def enriquecer_fondeo_costos(df: pd.DataFrame, fecha_ref=None) -> pd.DataFrame:
    out = df.copy()
    if 'saldo_actual' not in out.columns:
        out['saldo_actual'] = np.nan
    if 'base_calculo' not in out.columns:
        out['base_calculo'] = 365
    out['saldo_base'] = pd.to_numeric(out['saldo_actual'], errors='coerce').fillna(pd.to_numeric(out['monto_invertido'], errors='coerce')).fillna(0.0)
    out['base_calculo'] = pd.to_numeric(out['base_calculo'], errors='coerce').replace(0, np.nan).fillna(365)
    out['tasa_efectiva'] = pd.to_numeric(out['tasa_efectiva'], errors='coerce').fillna(0.0)
    out['costo_anual_estimado'] = out['saldo_base'] * out['tasa_efectiva']
    mes_inicio, mes_fin = obtener_mes_actual_bounds(fecha_ref)
    out['dias_mes_actual'] = out.apply(lambda r: 30.42 if esta_activa_en_mes(r.get('fecha_inicio'), r.get('fecha_vencimiento'), mes_inicio, mes_fin) else 0.0, axis=1)
    out['interes_mes_actual'] = out['saldo_base'] * out['tasa_efectiva'] * out['dias_mes_actual'] / out['base_calculo']
    return out


def enriquecer_colocacion_ingresos(df: pd.DataFrame, fecha_ref=None) -> pd.DataFrame:
    out = df.copy()
    if 'saldo_actual' not in out.columns:
        out['saldo_actual'] = np.nan
    if 'base_calculo' not in out.columns:
        out['base_calculo'] = 365
    out['saldo_base_credito'] = pd.to_numeric(out['saldo_actual'], errors='coerce').fillna(pd.to_numeric(out['monto_colocado'], errors='coerce')).fillna(0.0)
    out['base_calculo'] = pd.to_numeric(out['base_calculo'], errors='coerce').replace(0, np.nan).fillna(365)
    out['tasa_colocacion'] = pd.to_numeric(out['tasa_colocacion'], errors='coerce').fillna(0.0)
    out['ingreso_anual_estimado'] = out['saldo_base_credito'] * out['tasa_colocacion']
    mes_inicio, mes_fin = obtener_mes_actual_bounds(fecha_ref)
    out['dias_mes_actual'] = out.apply(lambda r: dias_operacion_en_mes(r.get('fecha_desembolso'), r.get('fecha_vencimiento'), mes_inicio, mes_fin), axis=1)
    out['interes_mes_actual'] = out['saldo_base_credito'] * out['tasa_colocacion'] * out['dias_mes_actual'] / out['base_calculo']
    return out


def fmt_money(x) -> str:
    if pd.isna(x): return '—'
    return f"${x:,.0f}"

def fmt_pct(x) -> str:
    if pd.isna(x): return '—'
    return f"{x:.2%}"

def fmt_pct_pp(x) -> str:
    if pd.isna(x): return '—'
    return f"{x * 100:,.2f} pp"

def fmt_days(x) -> str:
    if pd.isna(x): return '—'
    return f"{x:,.2f} días" if isinstance(x, float) and not float(x).is_integer() else f"{x:,.0f} días"

def fmt_date(x) -> str:
    if pd.isna(x): return '—'
    try: return pd.to_datetime(x).strftime('%d/%m/%Y')
    except Exception: return '—'


def renombrar_aliases(df: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    df = df.copy(); rename_map = {}
    for col in df.columns:
        if col in aliases and aliases[col] not in df.columns:
            rename_map[col] = aliases[col]
    return df.rename(columns=rename_map) if rename_map else df


def normalizar_moneda(valor):
    if pd.isna(valor) or str(valor).strip() == '': return 'MXN'
    t = limpiar_texto(valor)
    mapping = {'mxn':'MXN','mn':'MXN','m_n':'MXN','peso':'MXN','pesos':'MXN','moneda_nacional':'MXN','usd':'USD','us_dollar':'USD','dolar':'USD','dolares':'USD','dolar_americano':'USD','dolares_americanos':'USD','us$':'USD'}
    return mapping.get(t, str(valor).strip().upper())


def build_monthly_fondeo_snapshot(df: pd.DataFrame, n_months: int = 12) -> pd.DataFrame:
    cols = ['mes', 'mes_label', 'moneda', 'monto', 'tasa_promedio']
    if df.empty: return pd.DataFrame(columns=cols)
    base = df.copy()
    if 'moneda' not in base.columns: base['moneda'] = 'MXN'
    base['moneda'] = base['moneda'].apply(normalizar_moneda)
    cierre_actual = pd.Timestamp.today().normalize() + pd.offsets.MonthEnd(0)
    meses = pd.date_range(end=cierre_actual, periods=n_months, freq='M')
    registros = []
    for mes in meses:
        activos = base[base['fecha_inicio'].notna() & (base['fecha_inicio'] <= mes) & (base['fecha_vencimiento'].isna() | (base['fecha_vencimiento'] >= mes))].copy()
        monto_total = activos['monto_invertido'].sum() if not activos.empty else 0.0
        tasa_total = weighted_avg(activos['tasa_efectiva'], activos['monto_invertido']) if not activos.empty else np.nan
        registros.append({'mes': mes, 'mes_label': mes.strftime('%b %y').upper(), 'moneda': 'TOTAL', 'monto': monto_total, 'tasa_promedio': tasa_total})
        for moneda in ['MXN', 'USD']:
            grp = activos[activos['moneda'] == moneda].copy()
            registros.append({'mes': mes, 'mes_label': mes.strftime('%b %y').upper(), 'moneda': moneda, 'monto': grp['monto_invertido'].sum() if not grp.empty else 0.0, 'tasa_promedio': weighted_avg(grp['tasa_efectiva'], grp['monto_invertido']) if not grp.empty else np.nan})
    return pd.DataFrame(registros)


def construir_vencimientos_resumen(df_fondeo: pd.DataFrame, df_coloc: pd.DataFrame, months_forward: int = 24) -> pd.DataFrame:
    hoy = pd.Timestamp.today().normalize(); limite = (hoy + pd.DateOffset(months=months_forward)) + pd.offsets.MonthEnd(0)
    def _agg(df, fecha_col, monto_col, etiqueta):
        if df.empty or fecha_col not in df.columns or monto_col not in df.columns:
            return pd.DataFrame(columns=['mes', etiqueta])
        base = df[df[fecha_col].notna() & (df[fecha_col] >= hoy) & (df[fecha_col] <= limite)].copy()
        if base.empty: return pd.DataFrame(columns=['mes', etiqueta])
        base['mes'] = base[fecha_col].dt.to_period('M').dt.to_timestamp()
        return base.groupby('mes')[monto_col].sum().reset_index().rename(columns={monto_col: etiqueta})
    fondeo = _agg(df_fondeo, 'fecha_vencimiento', 'monto_invertido', 'Fondeo'); coloc = _agg(df_coloc, 'fecha_vencimiento', 'monto_colocado', 'Colocación')
    out = pd.merge(fondeo, coloc, on='mes', how='outer').fillna(0)
    if out.empty: return pd.DataFrame(columns=['mes','mes_label','Fondeo','Colocación'])
    out = out[(out['Fondeo'] > 0) | (out['Colocación'] > 0)].sort_values('mes'); out['mes_label'] = out['mes'].dt.strftime('%b %y').str.upper(); return out


def parse_temporalidad_a_dias(valor):
    if pd.isna(valor): return np.nan
    texto = str(valor).strip().lower()
    if texto == '': return np.nan
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    numeros = re.findall(r'\d+', texto); n = float(numeros[0]) if numeros else np.nan
    if 'dia' in texto: return n if not pd.isna(n) else np.nan
    if 'semana' in texto: return n * 7 if not pd.isna(n) else 7
    if 'quincena' in texto: return n * 15 if not pd.isna(n) else 15
    if 'mes' in texto: return n * 30 if not pd.isna(n) else 30
    if 'bimestre' in texto: return n * 60 if not pd.isna(n) else 60
    if 'trimestre' in texto: return n * 90 if not pd.isna(n) else 90
    if 'semestre' in texto: return n * 180 if not pd.isna(n) else 180
    if 'ano' in texto or 'año' in texto: return n * 365 if not pd.isna(n) else 365
    return n if not pd.isna(n) else np.nan


def dias_a_temporalidad(dias):
    if pd.isna(dias): return '—'
    dias = float(dias)
    if dias <= 7: return 'Semanal'
    if dias <= 15: return 'Quincenal'
    if dias <= 45: return 'Mensual'
    if dias <= 75: return 'Bimestral'
    if dias <= 120: return 'Trimestral'
    if dias <= 210: return 'Semestral'
    if dias <= 420: return 'Anual'
    return f"{int(round(dias))} días"


def completar_plazo_dias(df: pd.DataFrame, plazo_col: str, fecha_inicio_col: str, fecha_fin_col: str, temporalidad_col: str = 'temporalidad') -> pd.DataFrame:
    df = df.copy()
    if plazo_col not in df.columns: df[plazo_col] = np.nan
    df[plazo_col] = pd.to_numeric(df[plazo_col], errors='coerce')
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


def completar_temporalidad(df: pd.DataFrame, plazo_col: str = 'plazo_dias', temporalidad_col: str = 'temporalidad') -> pd.DataFrame:
    df = df.copy()
    if temporalidad_col not in df.columns: df[temporalidad_col] = np.nan
    vacio = df[temporalidad_col].isna() | (df[temporalidad_col].astype(str).str.strip() == '')
    df.loc[vacio, temporalidad_col] = df.loc[vacio, plazo_col].apply(dias_a_temporalidad)
    return df


def construir_estatus_automatico(df: pd.DataFrame, fecha_fin_col: str = 'fecha_vencimiento', estatus_col: str = 'estatus') -> pd.DataFrame:
    df = df.copy()
    if estatus_col not in df.columns: df[estatus_col] = np.nan
    hoy = pd.Timestamp.today().normalize()
    estatus_original = df[estatus_col].astype('string').fillna('').str.strip(); estatus_lower = estatus_original.str.lower()
    estatus_cerrados = {'liquidado','liquidada','pagado','pagada','cerrado','cerrada','cancelado','cancelada','finalizado','finalizada'}
    auto = np.where(df[fecha_fin_col].isna(), 'Sin fecha', np.where(df[fecha_fin_col] < hoy, 'Vencido', np.where(df[fecha_fin_col] == hoy, 'Vence hoy', 'Activo')))
    df[estatus_col] = np.where(estatus_lower.isin(estatus_cerrados), estatus_original, auto)
    return df


def normalizar_periodicidad_pago(valor):
    if pd.isna(valor): return 'Al vencimiento'
    t = limpiar_texto(valor)
    mapping = {'semanal':'Semanal','quincenal':'Quincenal','mensual':'Mensual','bimestral':'Bimestral','trimestral':'Trimestral','semestral':'Semestral','anual':'Anual','al_vencimiento':'Al vencimiento','vencimiento':'Al vencimiento','bullet':'Al vencimiento','pago_unico':'Al vencimiento'}
    return mapping.get(t, str(valor).strip().title())


def periodicidad_a_dias(valor):
    val = normalizar_periodicidad_pago(valor)
    return {'Semanal':7,'Quincenal':15,'Mensual':30,'Bimestral':60,'Trimestral':90,'Semestral':180,'Anual':365,'Al vencimiento':None}.get(val, None)


def normalizar_tipo_capital(valor):
    if pd.isna(valor): return 'Bullet'
    t = limpiar_texto(valor)
    mapping = {'bullet':'Bullet','pago_unico':'Bullet','pago_unico_al_vencimiento':'Bullet','al_vencimiento':'Bullet','amortizable':'Amortizable','amortizacion':'Amortizable','amortizable_lineal':'Amortizable'}
    return mapping.get(t, str(valor).strip().title())


def construir_fechas_pago(fecha_inicio, fecha_fin, periodicidad):
    if pd.isna(fecha_inicio) or pd.isna(fecha_fin): return []
    if fecha_fin < fecha_inicio: return []
    dias = periodicidad_a_dias(periodicidad)
    if dias is None: return [fecha_fin]
    fechas = []; siguiente = fecha_inicio + pd.Timedelta(days=dias)
    while siguiente < fecha_fin:
        fechas.append(siguiente); siguiente = siguiente + pd.Timedelta(days=dias)
    if not fechas or fechas[-1] != fecha_fin: fechas.append(fecha_fin)
    return fechas


def generar_calendario_flujos(df: pd.DataFrame, cartera_nombre: str, tipo_flujo: str, nombre_col: str, monto_col: str, tasa_col: str, fecha_inicio_col: str, fecha_fin_col: str, periodicidad_col: str, tipo_capital_col: str, saldo_col: str, base_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['Fecha','Cartera','Tipo Flujo','Contraparte','Periodicidad','Tipo Capital','Interés','Principal','Total','Estatus'])
    hoy = pd.Timestamp.today().normalize(); filas = []
    for _, row in df.iterrows():
        contraparte = str(row.get(nombre_col, '')).strip()
        principal_original = pd.to_numeric(row.get(monto_col), errors='coerce'); saldo_actual = pd.to_numeric(row.get(saldo_col), errors='coerce')
        tasa = pd.to_numeric(row.get(tasa_col), errors='coerce'); fecha_inicio = pd.to_datetime(row.get(fecha_inicio_col), errors='coerce'); fecha_fin = pd.to_datetime(row.get(fecha_fin_col), errors='coerce')
        if pd.isna(saldo_actual): saldo_actual = principal_original
        if pd.isna(saldo_actual): saldo_actual = 0
        if pd.isna(principal_original): principal_original = saldo_actual
        base_calc = pd.to_numeric(row.get(base_col), errors='coerce')
        if pd.isna(base_calc) or base_calc <= 0: base_calc = 365
        periodicidad = normalizar_periodicidad_pago(row.get(periodicidad_col, 'Al vencimiento'))
        tipo_capital = normalizar_tipo_capital(row.get(tipo_capital_col, 'Bullet'))
        if pd.isna(tasa) or tasa <= 0 or pd.isna(fecha_inicio) or pd.isna(fecha_fin) or saldo_actual <= 0:
            continue
        fechas_pago = construir_fechas_pago(fecha_inicio, fecha_fin, periodicidad)
        if not fechas_pago: continue
        saldo_vivo = float(saldo_actual); fecha_anterior = fecha_inicio; n_eventos = len(fechas_pago); principal_uniforme = saldo_vivo / n_eventos if tipo_capital == 'Amortizable' else 0
        for i, fecha_pago in enumerate(fechas_pago):
            dias_periodo = max((fecha_pago - fecha_anterior).days, 0)
            interes = saldo_vivo * tasa * dias_periodo / base_calc
            es_ultimo = i == (n_eventos - 1); principal = 0.0
            if tipo_capital == 'Amortizable': principal = saldo_vivo if es_ultimo else min(principal_uniforme, saldo_vivo)
            elif tipo_capital == 'Bullet': principal = saldo_vivo if es_ultimo else 0.0
            total = interes + principal
            estatus = 'Vencido' if fecha_pago < hoy else ('Hoy' if fecha_pago == hoy else 'Programado')
            filas.append({'Fecha': fecha_pago,'Cartera': cartera_nombre,'Tipo Flujo': tipo_flujo,'Contraparte': contraparte,'Periodicidad': periodicidad,'Tipo Capital': tipo_capital,'Interés': interes,'Principal': principal,'Total': total,'Estatus': estatus,'Base Cálculo': base_calc,'Días Periodo': dias_periodo})
            saldo_vivo = max(saldo_vivo - principal, 0); fecha_anterior = fecha_pago
    calendario = pd.DataFrame(filas)
    return calendario.sort_values(['Fecha','Tipo Flujo','Contraparte']).reset_index(drop=True) if not calendario.empty else calendario


def flujo_mensual_neto(calendario: pd.DataFrame) -> pd.DataFrame:
    if calendario.empty: return pd.DataFrame(columns=['mes','Cobros','Pagos','Neto'])
    base = calendario.copy(); base['mes'] = base['Fecha'].dt.to_period('M').dt.to_timestamp(); base['Monto Neto'] = np.where(base['Tipo Flujo'] == 'Cobro', base['Total'], -base['Total'])
    cobros = base[base['Tipo Flujo'] == 'Cobro'].groupby('mes')['Total'].sum().reset_index().rename(columns={'Total':'Cobros'})
    pagos = base[base['Tipo Flujo'] == 'Pago'].groupby('mes')['Total'].sum().reset_index().rename(columns={'Total':'Pagos'})
    neto = base.groupby('mes')['Monto Neto'].sum().reset_index().rename(columns={'Monto Neto':'Neto'})
    return cobros.merge(pagos, on='mes', how='outer').merge(neto, on='mes', how='outer').fillna(0).sort_values('mes')


def build_current_month_execution_summary(calendario: pd.DataFrame, base_df: pd.DataFrame, counterpart_col: str, real_col: str, month_start, month_end) -> pd.DataFrame:
    if calendario.empty:
        schedule = pd.DataFrame(columns=['Contraparte','Interés Programado','Principal Programado','Total Programado','Próxima Fecha'])
    else:
        base = calendario[(calendario['Fecha'] >= month_start) & (calendario['Fecha'] <= month_end)].copy()
        if base.empty:
            schedule = pd.DataFrame(columns=['Contraparte','Interés Programado','Principal Programado','Total Programado','Próxima Fecha'])
        else:
            schedule = base.groupby('Contraparte', dropna=False).agg(**{'Interés Programado':('Interés','sum'),'Principal Programado':('Principal','sum'),'Total Programado':('Total','sum'),'Próxima Fecha':('Fecha','min')}).reset_index()
    if real_col not in base_df.columns:
        real_df = pd.DataFrame(columns=['Contraparte','Real Reportado'])
    else:
        real_df = base_df.groupby(counterpart_col, dropna=False)[real_col].sum().reset_index().rename(columns={counterpart_col:'Contraparte', real_col:'Real Reportado'})
    out = pd.merge(schedule, real_df, on='Contraparte', how='outer')
    if out.empty:
        return pd.DataFrame(columns=['Contraparte','Interés Programado','Principal Programado','Total Programado','Real Reportado','Pendiente','Exceso','Próxima Fecha','Estatus Control'])
    for col in ['Interés Programado','Principal Programado','Total Programado','Real Reportado']:
        out[col] = out[col].fillna(0.0)
    out['Pendiente'] = (out['Total Programado'] - out['Real Reportado']).clip(lower=0)
    out['Exceso'] = (out['Real Reportado'] - out['Total Programado']).clip(lower=0)
    out['Estatus Control'] = np.select([
        (out['Total Programado'] == 0) & (out['Real Reportado'] > 0),
        out['Pendiente'] == 0,
        (out['Real Reportado'] > 0) & (out['Pendiente'] > 0),
        (out['Total Programado'] > 0) & (out['Real Reportado'] == 0),
    ], ['Sin programa / capturado','Cubierto','Parcial','Pendiente'], default='Sin movimiento')
    return out.sort_values(['Pendiente','Total Programado'], ascending=[False, False]).reset_index(drop=True)


def add_control_emoji(value: str) -> str:
    mapping = {'Cubierto':'🟢 Cubierto','Parcial':'🟡 Parcial','Pendiente':'🔴 Pendiente','Sin programa / capturado':'🔵 Sin programa / capturado','Sin movimiento':'⚪ Sin movimiento'}
    return mapping.get(str(value), str(value))


def build_investor_month_control(base_df: pd.DataFrame, counterpart_col: str, real_col: str) -> pd.DataFrame:
    if base_df.empty:
        return pd.DataFrame(columns=['Contraparte','Interés Esperado','Principal Esperado','Total Esperado','Real Reportado','Pendiente','Exceso','Próxima Fecha','Estatus Control'])
    work = base_df.copy()
    schedule = work.groupby(counterpart_col, dropna=False).agg(**{
        'Interés Esperado': ('interes_mes_actual', 'sum'),
        'Principal Esperado': ('saldo_base', lambda s: 0.0),
        'Total Esperado': ('interes_mes_actual', 'sum'),
        'Próxima Fecha': ('fecha_vencimiento', 'min'),
    }).reset_index().rename(columns={counterpart_col:'Contraparte'})
    real_df = work.groupby(counterpart_col, dropna=False)[real_col].sum().reset_index().rename(columns={counterpart_col:'Contraparte', real_col:'Real Reportado'}) if real_col in work.columns else pd.DataFrame(columns=['Contraparte','Real Reportado'])
    out = pd.merge(schedule, real_df, on='Contraparte', how='left')
    out['Real Reportado'] = out['Real Reportado'].fillna(0.0)
    out['Pendiente'] = (out['Total Esperado'] - out['Real Reportado']).clip(lower=0)
    out['Exceso'] = (out['Real Reportado'] - out['Total Esperado']).clip(lower=0)
    out['Estatus Control'] = np.select([
        out['Pendiente'] == 0,
        (out['Real Reportado'] > 0) & (out['Pendiente'] > 0),
        (out['Total Esperado'] > 0) & (out['Real Reportado'] == 0),
    ], ['Cubierto','Parcial','Pendiente'], default='Sin movimiento')
    return out.sort_values(['Pendiente','Total Esperado'], ascending=[False, False]).reset_index(drop=True)


def build_credit_month_control(base_df: pd.DataFrame, calendario_cobros: pd.DataFrame, counterpart_col: str, real_col: str, month_start, month_end) -> pd.DataFrame:
    if base_df.empty and calendario_cobros.empty:
        return pd.DataFrame(columns=['Contraparte','Interés Esperado','Principal Esperado','Total Esperado','Real Reportado','Pendiente','Exceso','Próxima Fecha','Estatus Control'])

    if base_df.empty:
        interes_df = pd.DataFrame(columns=['Contraparte','Interés Esperado'])
        real_df = pd.DataFrame(columns=['Contraparte','Real Reportado'])
    else:
        work = base_df.copy()
        interes_df = work.groupby(counterpart_col, dropna=False)['interes_mes_actual'].sum().reset_index().rename(columns={counterpart_col:'Contraparte','interes_mes_actual':'Interés Esperado'})
        real_df = work.groupby(counterpart_col, dropna=False)[real_col].sum().reset_index().rename(columns={counterpart_col:'Contraparte', real_col:'Real Reportado'}) if real_col in work.columns else pd.DataFrame(columns=['Contraparte','Real Reportado'])

    if calendario_cobros.empty:
        principal_df = pd.DataFrame(columns=['Contraparte','Principal Esperado','Próxima Fecha'])
    else:
        cal = calendario_cobros[(calendario_cobros['Fecha'] >= month_start) & (calendario_cobros['Fecha'] <= month_end)].copy()
        if cal.empty:
            principal_df = pd.DataFrame(columns=['Contraparte','Principal Esperado','Próxima Fecha'])
        else:
            principal_df = cal.groupby('Contraparte', dropna=False).agg(**{'Principal Esperado':('Principal','sum'),'Próxima Fecha':('Fecha','min')}).reset_index()

    out = pd.merge(interes_df, principal_df, on='Contraparte', how='outer')
    out = pd.merge(out, real_df, on='Contraparte', how='left')
    if out.empty:
        return pd.DataFrame(columns=['Contraparte','Interés Esperado','Principal Esperado','Total Esperado','Real Reportado','Pendiente','Exceso','Próxima Fecha','Estatus Control'])
    for col in ['Interés Esperado','Principal Esperado','Real Reportado']:
        out[col] = out[col].fillna(0.0)
    out['Total Esperado'] = out['Interés Esperado'] + out['Principal Esperado']
    out['Pendiente'] = (out['Total Esperado'] - out['Real Reportado']).clip(lower=0)
    out['Exceso'] = (out['Real Reportado'] - out['Total Esperado']).clip(lower=0)
    out['Estatus Control'] = np.select([
        out['Pendiente'] == 0,
        (out['Real Reportado'] > 0) & (out['Pendiente'] > 0),
        (out['Total Esperado'] > 0) & (out['Real Reportado'] == 0),
    ], ['Cubierto','Parcial','Pendiente'], default='Sin movimiento')
    return out.sort_values(['Pendiente','Total Esperado'], ascending=[False, False]).reset_index(drop=True)


def timeline_status_from_end(fecha_fin):
    hoy = pd.Timestamp.today().normalize()
    if pd.isna(fecha_fin): return 'Sin fecha'
    dias = (pd.Timestamp(fecha_fin).normalize() - hoy).days
    if dias < 0: return 'Vencido'
    if dias <= 60: return 'Vence <=60d'
    return 'Activo >60d'


def build_timeline_chart(df: pd.DataFrame, name_col: str, start_col: str, end_col: str, amount_col: str, title: str, color_col: str | None = None, months_forward: int = 12):
    base = df.copy()
    needed = [name_col, start_col, end_col, amount_col]
    if any(c not in base.columns for c in needed):
        return None
    base = base[base[start_col].notna() & base[end_col].notna()].copy()
    if base.empty:
        return None

    hoy = pd.Timestamp.today().normalize().replace(day=1)
    limite = (hoy + pd.DateOffset(months=months_forward)) + pd.offsets.MonthEnd(0)

    base = base[(base[end_col] >= hoy) & (base[start_col] <= limite)].copy()
    if base.empty:
        return None

    base['start_plot'] = base[start_col].clip(lower=hoy)
    base['end_plot'] = base[end_col].clip(upper=limite)
    dias_restantes = (base[end_col].dt.normalize() - pd.Timestamp.today().normalize()).dt.days
    base['timeline_status'] = np.select(
        [dias_restantes < 0, dias_restantes <= 30, dias_restantes <= 60, dias_restantes > 60],
        ['Vencido', 'Vence <=30d', 'Vence 31-60d', 'Activo >60d'],
        default='Activo >60d'
    )
    base = base.sort_values([amount_col, end_col], ascending=[False, True]).head(20).copy()
    base = base.sort_values('end_plot', ascending=True)
    color_use = color_col if color_col and color_col in base.columns else 'timeline_status'
    color_map = {
        'Vencido': ENTURE_PRIMARY,
        'Vence <=30d': ENTURE_PRIMARY,
        'Vence 31-60d': ENTURE_ACCENT,
        'Activo >60d': ENTURE_NAVY,
        'Sin fecha': ENTURE_GOLD,
    }
    fig = px.timeline(
        base,
        x_start='start_plot',
        x_end='end_plot',
        y=name_col,
        color=color_use,
        title=title,
        hover_data={amount_col:':,.0f', start_col:'|%d/%m/%Y', end_col:'|%d/%m/%Y'}
    )
    fig.update_yaxes(autorange='reversed')
    fig.update_xaxes(range=[hoy, limite], dtick='M1', tickformat='%b %Y')
    fig.update_layout(
        height=520,
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis_title='',
        yaxis_title='',
        legend_title=None,
        margin=dict(l=20, r=20, t=85, b=20)
    )
    if color_use == 'timeline_status':
        for trace in fig.data:
            trace.marker.color = color_map.get(trace.name, ENTURE_NAVY)
    try:
        hoy_linea = pd.Timestamp.today().normalize()
        fig.add_vrect(x0=hoy_linea - pd.Timedelta(days=1), x1=hoy_linea + pd.Timedelta(days=1), fillcolor='#14B8A6', opacity=0.14, line_width=0, layer='below')
        fig.add_shape(type='line', x0=hoy_linea, x1=hoy_linea, y0=0, y1=1, xref='x', yref='paper', line=dict(color='#14B8A6', width=4, dash='dash'), layer='above')
        fig.add_annotation(x=hoy_linea, y=1.06, xref='x', yref='paper', text='HOY', showarrow=False, font=dict(size=12, color='#14B8A6'), bgcolor='white', bordercolor='#14B8A6', borderwidth=1, borderpad=4)
    except Exception:
        pass
    return fig


def style_status(value):
    mapping = {'vencido':'🔴 Vencido','vence hoy':'🟡 Vence hoy','activo':'🟢 Activo','sin fecha':'⚪ Sin fecha'}
    return mapping.get(str(value).lower(), str(value))


def style_event_status(value):
    mapping = {'vencido':'🔴 Vencido','hoy':'🟡 Hoy','programado':'🟢 Programado'}
    return mapping.get(str(value).lower(), str(value))


def style_table(df: pd.DataFrame):
    # kept simple for compile; actual rendering in Streamlit accepts Styler too
    return df




# =========================================================
# FUNCIONES DE ANÁLISIS
# =========================================================
def top_concentration(df: pd.DataFrame, client_col: str, amount_col: str, top_n: int = 5) -> float:
    if df.empty or client_col not in df.columns or amount_col not in df.columns:
        return 0.0
    total = pd.to_numeric(df[amount_col], errors="coerce").fillna(0).sum()
    if total == 0:
        return 0.0
    top = (
        df.groupby(client_col, dropna=False)[amount_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .sum()
    )
    return float(top / total)


def top_one_concentration(df: pd.DataFrame, client_col: str, amount_col: str) -> float:
    return top_concentration(df, client_col, amount_col, top_n=1)


def monto_vence_en_dias(df: pd.DataFrame, fecha_col: str, amount_col: str, dias: int) -> float:
    if df.empty or fecha_col not in df.columns or amount_col not in df.columns:
        return 0.0
    hoy = pd.Timestamp.today().normalize()
    limite = hoy + pd.Timedelta(days=dias)
    mask = df[fecha_col].notna() & (df[fecha_col] >= hoy) & (df[fecha_col] <= limite)
    return float(pd.to_numeric(df.loc[mask, amount_col], errors="coerce").fillna(0).sum())


def tabla_top(df: pd.DataFrame, client_col: str, amount_col: str, n: int = 10) -> pd.DataFrame:
    if df.empty or client_col not in df.columns or amount_col not in df.columns:
        return pd.DataFrame()
    t = (
        df.groupby(client_col, dropna=False)[amount_col]
        .sum()
        .reset_index()
        .sort_values(amount_col, ascending=False)
        .head(n)
    )
    total_general = pd.to_numeric(df[amount_col], errors="coerce").fillna(0).sum()
    t["participacion_total"] = t[amount_col] / total_general if total_general != 0 else 0
    return t


def serie_vencimientos(df: pd.DataFrame, fecha_col: str, monto_col: str, etiqueta: str) -> pd.DataFrame:
    if df.empty or fecha_col not in df.columns or monto_col not in df.columns:
        return pd.DataFrame(columns=["mes", etiqueta])
    base = df[df[fecha_col].notna()].copy()
    if base.empty:
        return pd.DataFrame(columns=["mes", etiqueta])
    base["mes"] = base[fecha_col].dt.to_period("M").dt.to_timestamp()
    s = (
        base.groupby("mes")[monto_col]
        .sum()
        .reset_index()
        .rename(columns={monto_col: etiqueta})
    )
    return s


def serie_inicio(df: pd.DataFrame, fecha_col: str, monto_col: str, etiqueta: str) -> pd.DataFrame:
    if df.empty or fecha_col not in df.columns or monto_col not in df.columns:
        return pd.DataFrame(columns=["mes", etiqueta])
    base = df[df[fecha_col].notna()].copy()
    if base.empty:
        return pd.DataFrame(columns=["mes", etiqueta])
    base["mes"] = base[fecha_col].dt.to_period("M").dt.to_timestamp()
    s = (
        base.groupby("mes")[monto_col]
        .sum()
        .reset_index()
        .rename(columns={monto_col: etiqueta})
    )
    return s


def construir_buckets_vencimiento(df: pd.DataFrame, fecha_col: str, monto_col: str) -> pd.DataFrame:
    if df.empty or fecha_col not in df.columns or monto_col not in df.columns:
        return pd.DataFrame(columns=["bucket", "monto"])
    base = df[[fecha_col, monto_col]].copy()
    base = base[base[fecha_col].notna()]
    if base.empty:
        return pd.DataFrame(columns=["bucket", "monto"])
    hoy = pd.Timestamp.today().normalize()
    dias = (base[fecha_col] - hoy).dt.days

    condiciones = [
        dias < 0,
        (dias >= 0) & (dias <= 30),
        (dias >= 31) & (dias <= 60),
        (dias >= 61) & (dias <= 90),
        dias > 90,
    ]
    etiquetas = ["Vencido", "0-30 días", "31-60 días", "61-90 días", "+90 días"]
    base["bucket"] = np.select(condiciones, etiquetas, default="Sin clasificar")

    res = (
        base.groupby("bucket", dropna=False)[monto_col]
        .sum()
        .reset_index()
        .rename(columns={monto_col: "monto"})
    )
    orden = ["Vencido", "0-30 días", "31-60 días", "61-90 días", "+90 días"]
    res["bucket"] = pd.Categorical(res["bucket"], categories=orden, ordered=True)
    res = res.sort_values("bucket")
    return res


def top_otros(df: pd.DataFrame, client_col: str, amount_col: str, top_n: int = 5) -> pd.DataFrame:
    if df.empty or client_col not in df.columns or amount_col not in df.columns:
        return pd.DataFrame(columns=[client_col, amount_col])
    base = (
        df.groupby(client_col, dropna=False)[amount_col]
        .sum()
        .reset_index()
        .sort_values(amount_col, ascending=False)
    )
    if base.empty:
        return pd.DataFrame(columns=[client_col, amount_col])
    top = base.head(top_n).copy()
    resto = base.iloc[top_n:][amount_col].sum()
    if resto > 0:
        top.loc[len(top)] = ["Otros", resto]
    return top


def filtrar_dataframe(df: pd.DataFrame, columnas_opcionales: list[str], prefijo: str) -> pd.DataFrame:
    out = df.copy()
    for col in columnas_opcionales:
        if col in out.columns:
            valores = sorted([v for v in out[col].dropna().astype(str).unique().tolist() if v != ""])
            if valores:
                seleccion = st.sidebar.multiselect(f"{prefijo} - {col}", valores, default=valores)
                if seleccion:
                    out = out[out[col].astype(str).isin(seleccion)]
    return out


def enriquecer_rentabilidad_colocacion(df: pd.DataFrame, tasa_fondeo_base: float) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        out['spread_neto'] = []
        out['margen_anual_cliente'] = []
        out['clasificacion_rentabilidad'] = []
        return out
    out['spread_neto'] = pd.to_numeric(out['tasa_colocacion'], errors='coerce').fillna(0) - tasa_fondeo_base
    out['margen_anual_cliente'] = pd.to_numeric(out['saldo_base_credito'], errors='coerce').fillna(0) * out['spread_neto']
    out['clasificacion_rentabilidad'] = np.where(out['margen_anual_cliente'] < 0, 'Destruye valor', 'Aporta margen')
    return out


def resumen_margen_por_cliente(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['Cliente','Saldo Base','Ingreso Anual','Margen Anual','Spread Neto'])
    rows = []
    for cliente, g in df.groupby('cliente_credito', dropna=False):
        saldo = pd.to_numeric(g['saldo_base_credito'], errors='coerce').fillna(0).sum()
        ingreso = pd.to_numeric(g['ingreso_anual_estimado'], errors='coerce').fillna(0).sum()
        margen = pd.to_numeric(g['margen_anual_cliente'], errors='coerce').fillna(0).sum()
        spread = weighted_avg(g['spread_neto'], g['saldo_base_credito']) if saldo > 0 else 0
        rows.append({'Cliente': cliente, 'Saldo Base': saldo, 'Ingreso Anual': ingreso, 'Margen Anual': margen, 'Spread Neto': spread})
    return pd.DataFrame(rows).sort_values('Margen Anual', ascending=False)


def resumen_rentabilidad_por_segmento(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['Segmento','Saldo Base','Ingreso Anual','Margen Anual','Spread Neto'])
    work = df.copy()
    if 'segmento' not in work.columns:
        work['segmento'] = 'Sin segmento'
    rows = []
    for seg, g in work.groupby('segmento', dropna=False):
        saldo = pd.to_numeric(g['saldo_base_credito'], errors='coerce').fillna(0).sum()
        ingreso = pd.to_numeric(g['ingreso_anual_estimado'], errors='coerce').fillna(0).sum()
        margen = pd.to_numeric(g['margen_anual_cliente'], errors='coerce').fillna(0).sum()
        spread = weighted_avg(g['spread_neto'], g['saldo_base_credito']) if saldo > 0 else 0
        rows.append({'Segmento': seg, 'Saldo Base': saldo, 'Ingreso Anual': ingreso, 'Margen Anual': margen, 'Spread Neto': spread})
    return pd.DataFrame(rows).sort_values('Margen Anual', ascending=False)


def concentracion_ajustada_por_rendimiento(df: pd.DataFrame) -> float:
    if df.empty:
        return np.nan
    resumen = resumen_margen_por_cliente(df)
    positivos = resumen[resumen['Margen Anual'] > 0].copy()
    if positivos.empty:
        return np.nan
    total = positivos['Margen Anual'].sum()
    top5 = positivos.head(5)['Margen Anual'].sum()
    return float(top5 / total) if total else np.nan


def semaforo(valor, tipo):
    if pd.isna(valor):
        return "⚪ Sin dato"
    if tipo == "spread":
        if valor >= 0.06:
            return "🟢 Sólido"
        if valor >= 0.03:
            return "🟡 A revisar"
        return "🔴 Presión"
    if tipo == "concentracion_top1":
        if valor <= 0.20:
            return "🟢 Diversificado"
        if valor <= 0.30:
            return "🟡 Media"
        return "🔴 Alta"
    if tipo == "gap":
        if valor >= 0:
            return "🟢 Cubierto"
        return "🔴 Déficit"
    if tipo == "plazo":
        if valor <= 30:
            return "🟢 Alineado"
        if valor <= 90:
            return "🟡 Moderado"
        return "🔴 Relevante"
    if tipo == "cobertura":
        if valor >= 1.0:
            return "🟢 Suficiente"
        if valor >= 0.9:
            return "🟡 Justa"
        return "🔴 Baja"
    return "⚪ N/D"


def color_status(value):
    if str(value).lower() == "vencido":
        return "🔴 Vencido"
    if str(value).lower() == "vence hoy":
        return "🟡 Vence hoy"
    if str(value).lower() == "activo":
        return "🟢 Activo"
    if str(value).lower() == "sin fecha":
        return "⚪ Sin fecha"
    return str(value)


def color_event_status(value):
    if str(value).lower() == "vencido":
        return "🔴 Vencido"
    if str(value).lower() == "hoy":
        return "🟡 Hoy"
    if str(value).lower() == "programado":
        return "🟢 Programado"
    return str(value)


def crear_datos_demo():
    inversionistas = pd.DataFrame({
        'inversionista':['Fondo A','Family Office B','Inversionista C','Fondo D','Patrimonial E'],
        'monto_inversion':[25000000,18000000,12000000,32000000,9000000],
        'tasa_anual':[11.8,12.5,13.2,12.1,13.5],
        'fecha_inicio':['2026-01-15','2025-12-01','2026-02-10','2025-10-20','2026-03-01'],
        'fecha_de_termino':['2026-07-14','2026-11-26','2026-11-07','2026-04-18','2026-05-30'],
        'moneda':['MXN','USD','MXN','USD','MXN'],
        'periodicidad_pago':['Mensual','Trimestral','Al vencimiento','Mensual','Mensual'],
        'tipo_pago_capital':['Bullet','Bullet','Bullet','Bullet','Bullet'],
        'base_calculo':[365,365,365,365,365],
        'monto_pagado_mes_actual':[0,0,0,0,0],
        'estatus':['','','','',''],
        'producto':['Pagaré','Pagaré','Captación','Pagaré','Captación'],
        'asesor':['Ana','Luis','Ana','María','Luis'],
    })
    prestamos = pd.DataFrame({
        'cliente':['Cliente 1','Cliente 2','Cliente 3','Cliente 4','Cliente 5','Cliente 6'],
        'prestamo':[15000000,22000000,17000000,11000000,9000000,14000000],
        'tasa_anual':[19.5,21.5,20.5,22.5,23.5,19.8],
        'fecha_inicio':['2026-01-10','2026-02-15','2025-12-10','2026-03-01','2026-01-25','2025-11-20'],
        'fecha_de_termino':['2026-05-10','2026-08-14','2026-08-07','2026-05-30','2026-06-24','2026-11-15'],
        'periodicidad_cobro':['Mensual','Mensual','Trimestral','Mensual','Mensual','Al vencimiento'],
        'tipo_cobro_capital':['Bullet','Amortizable','Bullet','Bullet','Amortizable','Bullet'],
        'base_calculo':[365,365,365,365,365,365],
        'monto_cobrado_mes_actual':[0,0,0,0,0,0],
        'estatus':['','','','','',''],
        'segmento':['PyME','Consumo','Empresarial','PyME','Consumo','Empresarial'],
        'asesor':['Carlos','Sofía','Carlos','Sofía','Carlos','Sofía'],
    })
    return inversionistas, prestamos


@st.cache_data
def cargar_excel(archivo_bytes):
    archivo = BytesIO(archivo_bytes)
    hojas = pd.read_excel(archivo, sheet_name=None)
    hojas = {limpiar_texto(k): normalizar_columnas(v) for k, v in hojas.items()}
    if 'inversionistas' not in hojas: raise ValueError("No encontré la hoja 'inversionistas'.")
    if 'prestamos' not in hojas: raise ValueError("No encontré la hoja 'prestamos'.")
    inversionistas = hojas['inversionistas'].copy(); prestamos = hojas['prestamos'].copy()
    aliases_inv = {'inversionista':'cliente_inversionista','monto_inversion':'monto_invertido','monto_de_inversion':'monto_invertido','tasa_anual':'tasa_efectiva','fecha_de_inicio':'fecha_inicio','fecha_inicio':'fecha_inicio','fecha_fin':'fecha_vencimiento','fecha_de_termino':'fecha_vencimiento','fecha_termino':'fecha_vencimiento','fecha_de_cierre':'fecha_vencimiento','fecha_cierre':'fecha_vencimiento','periodicidad_de_pago':'periodicidad_pago','periodicidad_pago_interes':'periodicidad_pago','periodicidad':'periodicidad_pago','tipo_pago_de_capital':'tipo_pago_capital','tipo_capital':'tipo_pago_capital','saldo':'saldo_actual','saldo_vigente':'saldo_actual','saldo_actualizado':'saldo_actual','base':'base_calculo','moneda':'moneda','divisa':'moneda','currency':'moneda','monto_pagado_mes_actual':'monto_pagado_mes_actual','pagado_mes_actual':'monto_pagado_mes_actual','pago_real_mes_actual':'monto_pagado_mes_actual'}
    aliases_pre = {'cliente':'cliente_credito','prestamo':'monto_colocado','monto_prestamo':'monto_colocado','monto_de_prestamo':'monto_colocado','tasa_anual':'tasa_colocacion','fecha_de_inicio':'fecha_desembolso','fecha_inicio':'fecha_desembolso','fecha_fin':'fecha_vencimiento','fecha_de_termino':'fecha_vencimiento','fecha_termino':'fecha_vencimiento','fecha_de_cierre':'fecha_vencimiento','fecha_cierre':'fecha_vencimiento','periodicidad_de_cobro':'periodicidad_cobro','periodicidad_cobro_interes':'periodicidad_cobro','periodicidad':'periodicidad_cobro','tipo_cobro_de_capital':'tipo_cobro_capital','tipo_capital':'tipo_cobro_capital','saldo':'saldo_actual','saldo_vigente':'saldo_actual','saldo_actualizado':'saldo_actual','base':'base_calculo','monto_cobrado_mes_actual':'monto_cobrado_mes_actual','cobrado_mes_actual':'monto_cobrado_mes_actual','cobro_real_mes_actual':'monto_cobrado_mes_actual'}
    inversionistas = renombrar_aliases(inversionistas, aliases_inv); prestamos = renombrar_aliases(prestamos, aliases_pre)
    inversionistas = preparar_fechas(inversionistas, ['fecha_inicio','fecha_vencimiento']); prestamos = preparar_fechas(prestamos, ['fecha_desembolso','fecha_vencimiento'])
    for col in ['cliente_inversionista','monto_invertido','tasa_efectiva','plazo_dias','estatus','temporalidad','periodicidad_pago','tipo_pago_capital','saldo_actual','base_calculo','moneda','monto_pagado_mes_actual']:
        if col not in inversionistas.columns: inversionistas[col] = np.nan
    for col in ['cliente_credito','monto_colocado','tasa_colocacion','plazo_dias','estatus','temporalidad','periodicidad_cobro','tipo_cobro_capital','saldo_actual','base_calculo','monto_cobrado_mes_actual']:
        if col not in prestamos.columns: prestamos[col] = np.nan
    inversionistas['monto_invertido'] = a_numero(inversionistas['monto_invertido']); inversionistas['tasa_efectiva'] = normalizar_tasa(inversionistas['tasa_efectiva']); inversionistas['plazo_dias'] = a_numero(inversionistas['plazo_dias']); inversionistas['saldo_actual'] = a_numero(inversionistas['saldo_actual']); inversionistas['base_calculo'] = a_numero(inversionistas['base_calculo']); inversionistas['monto_pagado_mes_actual'] = a_numero(inversionistas['monto_pagado_mes_actual']).fillna(0)
    prestamos['monto_colocado'] = a_numero(prestamos['monto_colocado']); prestamos['tasa_colocacion'] = normalizar_tasa(prestamos['tasa_colocacion']); prestamos['plazo_dias'] = a_numero(prestamos['plazo_dias']); prestamos['saldo_actual'] = a_numero(prestamos['saldo_actual']); prestamos['base_calculo'] = a_numero(prestamos['base_calculo']); prestamos['monto_cobrado_mes_actual'] = a_numero(prestamos['monto_cobrado_mes_actual']).fillna(0)
    inversionistas = completar_plazo_dias(inversionistas, 'plazo_dias', 'fecha_inicio', 'fecha_vencimiento', 'temporalidad'); prestamos = completar_plazo_dias(prestamos, 'plazo_dias', 'fecha_desembolso', 'fecha_vencimiento', 'temporalidad')
    inversionistas = completar_temporalidad(inversionistas, 'plazo_dias', 'temporalidad'); prestamos = completar_temporalidad(prestamos, 'plazo_dias', 'temporalidad')
    inversionistas = construir_estatus_automatico(inversionistas, 'fecha_vencimiento', 'estatus'); prestamos = construir_estatus_automatico(prestamos, 'fecha_vencimiento', 'estatus')
    inversionistas['periodicidad_pago'] = inversionistas['periodicidad_pago'].apply(normalizar_periodicidad_pago); prestamos['periodicidad_cobro'] = prestamos['periodicidad_cobro'].apply(normalizar_periodicidad_pago)
    inversionistas['tipo_pago_capital'] = inversionistas['tipo_pago_capital'].apply(normalizar_tipo_capital); prestamos['tipo_cobro_capital'] = prestamos['tipo_cobro_capital'].apply(normalizar_tipo_capital)
    inversionistas['saldo_actual'] = inversionistas['saldo_actual'].fillna(inversionistas['monto_invertido']); prestamos['saldo_actual'] = prestamos['saldo_actual'].fillna(prestamos['monto_colocado'])
    inversionistas['base_calculo'] = inversionistas['base_calculo'].fillna(365); prestamos['base_calculo'] = prestamos['base_calculo'].fillna(365)
    if 'moneda' not in inversionistas.columns: inversionistas['moneda'] = 'MXN'
    inversionistas['moneda'] = inversionistas['moneda'].fillna('MXN').apply(normalizar_moneda)
    return inversionistas, prestamos


st.sidebar.markdown('## Carga de información')
usar_demo = st.sidebar.checkbox('Usar datos demo', value=True)
archivo = st.sidebar.file_uploader('Sube tu Excel', type=['xlsx', 'xls'])
if usar_demo:
    inversionistas_raw, prestamos_raw = crear_datos_demo(); buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        inversionistas_raw.to_excel(writer, sheet_name='inversionistas', index=False)
        prestamos_raw.to_excel(writer, sheet_name='prestamos', index=False)
    inversionistas, prestamos = cargar_excel(buffer.getvalue())
else:
    if archivo is None:
        st.info("Sube un archivo Excel con las hojas 'inversionistas' y 'prestamos'.")
        st.stop()
    inversionistas, prestamos = cargar_excel(archivo.getvalue())


st.sidebar.markdown('## Filtros')
inversionistas_f = filtrar_dataframe(inversionistas, ['estatus','producto','asesor'], 'Inversionistas')
prestamos_f = filtrar_dataframe(prestamos, ['estatus','segmento','asesor'], 'Préstamos')


inversionistas_f_cost = enriquecer_fondeo_costos(inversionistas_f)
prestamos_f_ing = enriquecer_colocacion_ingresos(prestamos_f)
mes_actual_inicio, mes_actual_fin = obtener_mes_actual_bounds(); mes_actual_label = nombre_mes_es(mes_actual_inicio)
num_inversionistas = inversionistas_f['cliente_inversionista'].nunique() if 'cliente_inversionista' in inversionistas_f.columns else 0
total_fondeo = inversionistas_f_cost['saldo_base'].sum() if not inversionistas_f_cost.empty else 0
costo_anual_total_fondeo = inversionistas_f_cost['costo_anual_estimado'].sum() if not inversionistas_f_cost.empty else 0
tasa_fondeo = (costo_anual_total_fondeo / total_fondeo) if total_fondeo > 0 else 0
plazo_fondeo = weighted_avg(inversionistas_f['plazo_dias'], inversionistas_f['monto_invertido']) if not inversionistas_f.empty else 0
interes_pagar_mes_actual = inversionistas_f_cost['interes_mes_actual'].sum() if not inversionistas_f_cost.empty else 0
num_clientes_credito = prestamos_f['cliente_credito'].nunique() if 'cliente_credito' in prestamos_f.columns else 0
total_colocado = prestamos_f['monto_colocado'].sum() if 'monto_colocado' in prestamos_f.columns else 0
saldo_base_colocacion_total = prestamos_f_ing['saldo_base_credito'].sum() if not prestamos_f_ing.empty else 0
ingreso_anual_total_colocacion = prestamos_f_ing['ingreso_anual_estimado'].sum() if not prestamos_f_ing.empty else 0
tasa_colocacion = (ingreso_anual_total_colocacion / saldo_base_colocacion_total) if saldo_base_colocacion_total > 0 else 0
plazo_colocacion = weighted_avg(prestamos_f['plazo_dias'], prestamos_f['monto_colocado']) if not prestamos_f.empty else 0
interes_cobrar_mes_actual = prestamos_f_ing['interes_mes_actual'].sum() if not prestamos_f_ing.empty else 0
spread = tasa_colocacion - tasa_fondeo
ingreso_anual_estimado = ingreso_anual_total_colocacion
costo_anual_estimado = costo_anual_total_fondeo
margen_financiero_estimado = ingreso_anual_estimado - costo_anual_estimado
venc_fondeo_30 = monto_vence_en_dias(inversionistas_f, 'fecha_vencimiento', 'monto_invertido', 30)
venc_fondeo_60 = monto_vence_en_dias(inversionistas_f, 'fecha_vencimiento', 'monto_invertido', 60)
venc_fondeo_90 = monto_vence_en_dias(inversionistas_f, 'fecha_vencimiento', 'monto_invertido', 90)
venc_coloc_30 = monto_vence_en_dias(prestamos_f, 'fecha_vencimiento', 'monto_colocado', 30)
venc_coloc_60 = monto_vence_en_dias(prestamos_f, 'fecha_vencimiento', 'monto_colocado', 60)
venc_coloc_90 = monto_vence_en_dias(prestamos_f, 'fecha_vencimiento', 'monto_colocado', 90)
gap_30 = venc_coloc_30 - venc_fondeo_30; gap_60 = venc_coloc_60 - venc_fondeo_60; gap_90 = venc_coloc_90 - venc_fondeo_90
conc_top5_inv = top_concentration(inversionistas_f, 'cliente_inversionista', 'monto_invertido', 5); conc_top5_pre = top_concentration(prestamos_f, 'cliente_credito', 'monto_colocado', 5)
conc_top1_inv = top_one_concentration(inversionistas_f, 'cliente_inversionista', 'monto_invertido'); conc_top1_pre = top_one_concentration(prestamos_f, 'cliente_credito', 'monto_colocado')
cobertura = saldo_base_colocacion_total / total_fondeo if total_fondeo != 0 else np.nan
descalce_plazos = plazo_colocacion - plazo_fondeo
alertas = []
if spread < 0: alertas.append(('error', 'Spread negativo', 'La tasa de colocación está por debajo del costo promedio del fondeo.'))
if conc_top1_inv > 0.25: alertas.append(('warning', 'Concentración en fondeo', 'El principal inversionista supera 25% del fondeo total.'))
if conc_top1_pre > 0.25: alertas.append(('warning', 'Concentración en colocación', 'El principal cliente supera 25% de la cartera colocada.'))
if gap_30 < 0: alertas.append(('warning', 'Gap de liquidez 30 días', 'En el corto plazo vencen antes tus obligaciones que tus activos.'))
if descalce_plazos > 60: alertas.append(('warning', 'Descalce de plazos', 'La colocación promedio vence materialmente después que el fondeo.'))
if not alertas: alertas.append(('success','Situación general estable','No se detectaron alertas críticas con la información filtrada actual.'))


timeline_inicio_inv = serie_inicio(inversionistas_f, 'fecha_inicio', 'monto_invertido', 'Captación'); timeline_inicio_pre = serie_inicio(prestamos_f, 'fecha_desembolso', 'monto_colocado', 'Colocación'); timeline_inicio = pd.merge(timeline_inicio_inv, timeline_inicio_pre, on='mes', how='outer').fillna(0).sort_values('mes')
buckets_inv = construir_buckets_vencimiento(inversionistas_f, 'fecha_vencimiento', 'monto_invertido'); buckets_pre = construir_buckets_vencimiento(prestamos_f, 'fecha_vencimiento', 'monto_colocado')
donut_inv = top_otros(inversionistas_f, 'cliente_inversionista', 'monto_invertido', 5); donut_pre = top_otros(prestamos_f, 'cliente_credito', 'monto_colocado', 5)
fondeo_snapshot_12m = build_monthly_fondeo_snapshot(inversionistas_f, 12); fondeo_growth_12m = fondeo_snapshot_12m[fondeo_snapshot_12m['moneda'] == 'TOTAL'].copy()
if not fondeo_growth_12m.empty: fondeo_growth_12m['monto_mdp'] = fondeo_growth_12m['monto'] / 1_000_000
mix_moneda_12m = fondeo_snapshot_12m[fondeo_snapshot_12m['moneda'].isin(['MXN','USD'])].copy()
if not mix_moneda_12m.empty:
    mix_moneda_12m['monto_total_mes'] = mix_moneda_12m.groupby('mes')['monto'].transform('sum')
    mix_moneda_12m['pct'] = np.where(mix_moneda_12m['monto_total_mes'] > 0, mix_moneda_12m['monto'] / mix_moneda_12m['monto_total_mes'], 0)
    mix_moneda_12m['monto_mdp'] = mix_moneda_12m['monto'] / 1_000_000
tasa_fondeo_moneda_12m = mix_moneda_12m[mix_moneda_12m['monto'] > 0].copy()
timeline_venc_24m = construir_vencimientos_resumen(inversionistas_f, prestamos_f, 24)
if not timeline_venc_24m.empty:
    timeline_venc_24m['Fondeo_mdp'] = timeline_venc_24m['Fondeo'] / 1_000_000
    timeline_venc_24m['Colocación_mdp'] = timeline_venc_24m['Colocación'] / 1_000_000

calendario_pagos = generar_calendario_flujos(inversionistas_f, 'Fondeo', 'Pago', 'cliente_inversionista', 'monto_invertido', 'tasa_efectiva', 'fecha_inicio', 'fecha_vencimiento', 'periodicidad_pago', 'tipo_pago_capital', 'saldo_actual', 'base_calculo')
calendario_cobros = generar_calendario_flujos(prestamos_f, 'Colocación', 'Cobro', 'cliente_credito', 'monto_colocado', 'tasa_colocacion', 'fecha_desembolso', 'fecha_vencimiento', 'periodicidad_cobro', 'tipo_cobro_capital', 'saldo_actual', 'base_calculo')
calendario_flujos = pd.concat([calendario_pagos, calendario_cobros], ignore_index=True) if (not calendario_pagos.empty or not calendario_cobros.empty) else pd.DataFrame()
if not calendario_flujos.empty: calendario_flujos = calendario_flujos.sort_values('Fecha').reset_index(drop=True)
flujo_mes = flujo_mensual_neto(calendario_flujos)
resumen_pago_mes_actual = build_investor_month_control(inversionistas_f_cost, 'cliente_inversionista', 'monto_pagado_mes_actual')
resumen_cobro_mes_actual = build_credit_month_control(prestamos_f_ing, calendario_cobros, 'cliente_credito', 'monto_cobrado_mes_actual', mes_actual_inicio, mes_actual_fin)
principal_cobrar_mes_actual = resumen_cobro_mes_actual['Principal Esperado'].sum() if not resumen_cobro_mes_actual.empty else 0
total_pagar_mes_actual = interes_pagar_mes_actual
total_cobrar_mes_actual = interes_cobrar_mes_actual + principal_cobrar_mes_actual
flujo_neto_mes_actual = total_cobrar_mes_actual - total_pagar_mes_actual
pagado_real_mes_actual = resumen_pago_mes_actual['Real Reportado'].sum() if not resumen_pago_mes_actual.empty else 0
cobrado_real_mes_actual = resumen_cobro_mes_actual['Real Reportado'].sum() if not resumen_cobro_mes_actual.empty else 0
pendiente_pagar_mes_actual = max(total_pagar_mes_actual - pagado_real_mes_actual, 0)
pendiente_cobrar_mes_actual = max(total_cobrar_mes_actual - cobrado_real_mes_actual, 0)

if not prestamos_f_ing.empty:
    merge_cobro = resumen_cobro_mes_actual[['Contraparte','Interés Esperado','Principal Esperado','Total Esperado']].rename(columns={'Contraparte':'cliente_credito','Interés Esperado':'interes_cobrar_mes','Principal Esperado':'principal_cobrar_mes','Total Esperado':'total_cobrar_mes'}) if not resumen_cobro_mes_actual.empty else pd.DataFrame(columns=['cliente_credito','interes_cobrar_mes','principal_cobrar_mes','total_cobrar_mes'])
    prestamos_f_ing = prestamos_f_ing.merge(merge_cobro, on='cliente_credito', how='left')
    for c in ['interes_cobrar_mes','principal_cobrar_mes','total_cobrar_mes']:
        if c not in prestamos_f_ing.columns: prestamos_f_ing[c] = 0.0
        prestamos_f_ing[c] = prestamos_f_ing[c].fillna(0.0)

prestamos_f_ing = enriquecer_rentabilidad_colocacion(prestamos_f_ing, tasa_fondeo)
cliente_margin_df = resumen_margen_por_cliente(prestamos_f_ing)
segment_margin_df = resumen_rentabilidad_por_segmento(prestamos_f_ing)
conc_ajustada_rend = concentracion_ajustada_por_rendimiento(prestamos_f_ing)
cartera_destruye_valor = prestamos_f_ing[prestamos_f_ing['margen_anual_cliente'] < 0].copy()
cartera_aporta_valor = prestamos_f_ing[prestamos_f_ing['margen_anual_cliente'] >= 0].copy()
monto_destruye_valor = pd.to_numeric(cartera_destruye_valor['saldo_base_credito'], errors='coerce').fillna(0).sum() if not cartera_destruye_valor.empty else 0
monto_aporta_valor = pd.to_numeric(cartera_aporta_valor['saldo_base_credito'], errors='coerce').fillna(0).sum() if not cartera_aporta_valor.empty else 0

resumen_text = f"En {mes_actual_label}, el flujo neto programado es {'positivo' if flujo_neto_mes_actual >= 0 else 'negativo'} por {fmt_money(flujo_neto_mes_actual)}, con una concentración top 5 de clientes de {fmt_pct(conc_top5_pre)} y spread promedio de {fmt_pct(spread)}."
fondeo_text = f"El fondeo total asciende a {fmt_money(total_fondeo)}. El interés mensual estimado a pagar es {fmt_money(interes_pagar_mes_actual)} y la concentración top 5 de inversionistas es {fmt_pct(conc_top5_inv)}."
coloc_text = f"La cartera colocada mantiene una tasa efectiva de {fmt_pct(tasa_colocacion)}. El total a cobrar del mes es {fmt_money(total_cobrar_mes_actual)} y {'existe' if monto_destruye_valor > 0 else 'no existe'} cartera que destruye valor relevante."
riesgo_text = f"El gap a 30 días es de {fmt_money(gap_30)} y la cobertura colocación/fondeo es {f'{cobertura:,.2f}x' if pd.notna(cobertura) else '—'}."
tesoreria_text = f"En el mes actual hay {fmt_money(pendiente_pagar_mes_actual)} pendientes por pagar y {fmt_money(pendiente_cobrar_mes_actual)} pendientes por cobrar según lo reportado."

fondeo_timeline_fig = build_timeline_chart(inversionistas_f, 'cliente_inversionista', 'fecha_inicio', 'fecha_vencimiento', 'monto_invertido', 'Vigencia de fondeo | Próximos 12 meses')
coloc_timeline_fig = build_timeline_chart(prestamos_f, 'cliente_credito', 'fecha_desembolso', 'fecha_vencimiento', 'monto_colocado', 'Vigencia de colocación | Próximos 12 meses')

# just compile until here

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Resumen Ejecutivo','Fondeo / Inversionistas','Colocación / Préstamos','Riesgos y Vencimientos','Tesorería y Flujos'])

with tab1:
    section_title('KPIs Ejecutivos', 'Vista consolidada de fondeo, colocación, rentabilidad, flujo del mes y descalces.')
    render_narrative_band(resumen_text)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Número de inversionistas', f"{num_inversionistas:,.0f}")
    c2.metric('Total fondeo', fmt_money(total_fondeo))
    c3.metric('Tasa promedio fondeo', fmt_pct(tasa_fondeo))
    c4.metric('Plazo promedio fondeo', fmt_days(plazo_fondeo))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric('Número de clientes crédito', f"{num_clientes_credito:,.0f}")
    c6.metric('Total colocado', fmt_money(total_colocado), delta=f"{cobertura:,.2f}x cobertura" if pd.notna(cobertura) else None)
    c7.metric('Tasa promedio colocación', fmt_pct(tasa_colocacion), delta=fmt_pct_pp(spread))
    c8.metric('Plazo promedio colocación', fmt_days(plazo_colocacion))
    c9, c10, c11, c12 = st.columns(4)
    c9.metric('Spread financiero', fmt_pct(spread))
    c10.metric('Margen anual estimado', fmt_money(margen_financiero_estimado))
    c11.metric('Gap 30 días', fmt_money(gap_30))
    c12.metric('Concentración top 1', fmt_pct(max(conc_top1_inv, conc_top1_pre)))
    c13, c14, c15 = st.columns(3)
    c13.metric(f'Intereses a pagar {mes_actual_label}', fmt_money(total_pagar_mes_actual), help='Costo mensual estimado del fondeo del mes actual, calculado con 30.42 días para cada inversionista activo.')
    c14.metric(f'Total a cobrar {mes_actual_label}', fmt_money(total_cobrar_mes_actual), help='Incluye interés del mes calculado con días reales para cada crédito activo más principal con vencimiento dentro del mes actual.')
    c15.metric(f'Flujo neto {mes_actual_label}', fmt_money(flujo_neto_mes_actual), help='Diferencia entre el total a cobrar del mes y los intereses a pagar del mismo mes.')
    section_title('Alertas ejecutivas')
    for nivel, titulo, texto in alertas:
        render_alert_box(nivel, titulo, texto)

    col_a, col_b = st.columns(2)
    with col_a:
        section_title('Crecimiento de cartera de inversionistas | últimos 12 meses', 'Monto activo al cierre de cada mes.')
        if not fondeo_growth_12m.empty:
            fig_growth = px.bar(fondeo_growth_12m, x='mes_label', y='monto_mdp', text='monto_mdp', title='Cartera de fondeo (MDP)', color_discrete_sequence=[ENTURE_PRIMARY])
            fig_growth.update_traces(texttemplate='%{text:,.1f} MDP', textposition='outside')
            fig_growth.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='MDP', margin=dict(l=20, r=20, t=60, b=20), showlegend=False)
            st.plotly_chart(fig_growth, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay información suficiente para construir el crecimiento mensual.')
    with col_b:
        section_title('Mezcla mensual de moneda de fondeo', 'Participación MXN vs USD al cierre de cada mes.')
        if not mix_moneda_12m.empty:
            fig_mix = px.bar(mix_moneda_12m, x='mes_label', y='pct', color='moneda', barmode='stack', text='pct', title='Mix de moneda por mes', color_discrete_map={'MXN': ENTURE_ACCENT, 'USD': ENTURE_NAVY})
            fig_mix.update_traces(texttemplate='%{text:.0%}', textposition='inside')
            fig_mix.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='% participación', margin=dict(l=20, r=20, t=60, b=20), legend_title=None)
            fig_mix.update_yaxes(tickformat='.0%')
            st.plotly_chart(fig_mix, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay información de moneda para construir la mezcla mensual.')

    col_c, col_d = st.columns(2)
    with col_c:
        section_title('Evolución de tasa promedio de fondeo', 'Promedio ponderado mensual por moneda.')
        if not tasa_fondeo_moneda_12m.empty:
            fig_tasa = px.line(tasa_fondeo_moneda_12m, x='mes_label', y='tasa_promedio', color='moneda', markers=True, title='Tasa promedio de fondeo | MXN vs USD', color_discrete_map={'MXN': ENTURE_ACCENT, 'USD': ENTURE_NAVY})
            fig_tasa.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Tasa', margin=dict(l=20, r=20, t=60, b=20), legend_title=None)
            fig_tasa.update_yaxes(tickformat='.0%')
            st.plotly_chart(fig_tasa, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay suficiente información para la evolución de tasas por moneda.')
    with col_d:
        section_title('Vencimientos próximos 24 meses', 'Solo se muestran meses con pagos o vencimientos.')
        if not timeline_venc_24m.empty:
            venc_melt = timeline_venc_24m.melt(id_vars='mes_label', value_vars=['Fondeo_mdp','Colocación_mdp'], var_name='Tipo', value_name='Monto')
            venc_melt['Tipo'] = venc_melt['Tipo'].replace({'Fondeo_mdp':'Fondeo','Colocación_mdp':'Colocación'})
            fig_venc = px.bar(venc_melt, x='mes_label', y='Monto', color='Tipo', barmode='group', title='Vencimientos con evento', color_discrete_map={'Fondeo': ENTURE_PRIMARY, 'Colocación': ENTURE_NAVY})
            fig_venc.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='MDP', margin=dict(l=20, r=20, t=60, b=20), legend_title=None)
            st.plotly_chart(fig_venc, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay vencimientos dentro de los próximos 24 meses.')

    col_e, col_f = st.columns(2)
    with col_e:
        section_title('Concentración de fondeo', 'Top 5 inversionistas + resto.')
        if not donut_inv.empty:
            fig_donut_inv = px.pie(donut_inv, names='cliente_inversionista', values='monto_invertido', hole=.60, color_discrete_sequence=[ENTURE_ACCENT, ENTURE_PRIMARY, ENTURE_NAVY, ENTURE_GOLD, '#A94438', '#2B3244'], title='Mix de inversionistas')
            fig_donut_inv.update_layout(height=390, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_donut_inv, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay datos de fondeo para graficar.')
    with col_f:
        section_title('Concentración de colocación', 'Top 5 clientes + resto.')
        if not donut_pre.empty:
            fig_donut_pre = px.pie(donut_pre, names='cliente_credito', values='monto_colocado', hole=.60, color_discrete_sequence=[ENTURE_NAVY, ENTURE_PRIMARY, ENTURE_ACCENT, ENTURE_GOLD, '#A94438', '#2B3244'], title='Mix de colocación')
            fig_donut_pre.update_layout(height=390, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_donut_pre, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay datos de colocación para graficar.')

with tab2:
    section_title('Resumen de fondeo', 'Vista detallada del pasivo financiero y sus concentraciones.')
    render_narrative_band(fondeo_text)
    st.info('En inversionistas, el interés mensual se calcula con una base fija de 30.42 días. La gráfica de vigencias muestra solo la ventana de los próximos 12 meses e incluye una línea vertical con la fecha actual como referencia.')
    a1, a2, a3 = st.columns(3)
    a1.metric('Total fondeo', fmt_money(total_fondeo)); a2.metric('Tasa efectiva de fondeo', fmt_pct(tasa_fondeo)); a3.metric('Costo anual total de fondeo', fmt_money(costo_anual_total_fondeo))
    a4, a5, a6 = st.columns(3)
    a4.metric(f'Intereses por pagar en {mes_actual_label}', fmt_money(interes_pagar_mes_actual)); a5.metric('Vence en 30 días', fmt_money(venc_fondeo_30)); a6.metric('Top 5 concentración', fmt_pct(conc_top5_inv))
    a7, a8, a9 = st.columns(3)
    a7.metric('Pagado real del mes', fmt_money(pagado_real_mes_actual))
    a8.metric('Pendiente por pagar del mes', fmt_money(pendiente_pagar_mes_actual))
    a9.metric('Concentración ajustada por margen', fmt_pct(conc_ajustada_rend) if pd.notna(conc_ajustada_rend) else '—')
    col1, col2 = st.columns(2)
    with col1:
        section_title('Top inversionistas por monto')
        top_inv = tabla_top(inversionistas_f, 'cliente_inversionista', 'monto_invertido', 10)
        if not top_inv.empty:
            fig_inv = px.bar(top_inv, x='cliente_inversionista', y='monto_invertido', text='monto_invertido', title='Top inversionistas', color_discrete_sequence=[ENTURE_PRIMARY])
            fig_inv.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_inv.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Monto', margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_inv, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay inversionistas para mostrar.')
    with col2:
        section_title('Buckets de vencimiento de fondeo')
        if not buckets_inv.empty:
            fig_bucket_inv = px.bar(buckets_inv, x='bucket', y='monto', text='monto', title='Distribución por bucket', color='bucket', color_discrete_sequence=PLOT_COLORS)
            fig_bucket_inv.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_bucket_inv.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Monto', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_bucket_inv, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay vencimientos para mostrar.')
    section_title('Vigencia de operaciones de fondeo', 'Se muestran las 20 operaciones de mayor monto.')
    if fondeo_timeline_fig is not None:
        st.plotly_chart(fondeo_timeline_fig, use_container_width=True, config=PLOT_CONFIG)
    else:
        st.info('No hay suficiente información para la gráfica de vigencias.')
    section_title('Detalle de inversionistas')
    if not inversionistas_f_cost.empty:
        detalle_inv = pd.DataFrame({
            'Inversionista': inversionistas_f_cost['cliente_inversionista'],
            'Moneda': inversionistas_f_cost['moneda'] if 'moneda' in inversionistas_f_cost.columns else 'MXN',
            'Saldo Base': inversionistas_f_cost['saldo_base'].map(fmt_money),
            'Monto Inversión': inversionistas_f_cost['monto_invertido'].map(fmt_money),
            'Tasa Anual': inversionistas_f_cost['tasa_efectiva'].map(fmt_pct),
            'Costo Anual Estimado': inversionistas_f_cost['costo_anual_estimado'].map(fmt_money),
            f'Interés {mes_actual_label}': inversionistas_f_cost['interes_mes_actual'].map(fmt_money),
            'Días Base Mes': inversionistas_f_cost['dias_mes_actual'].apply(lambda x: '—' if pd.isna(x) else round(float(x), 2)),
            'Fecha Inicio': inversionistas_f_cost['fecha_inicio'].map(fmt_date),
            'Fecha de Término': inversionistas_f_cost['fecha_vencimiento'].map(fmt_date),
            'Periodicidad Pago': inversionistas_f_cost['periodicidad_pago'],
            'Tipo Capital': inversionistas_f_cost['tipo_pago_capital'],
            'Pagado real mes': inversionistas_f_cost['monto_pagado_mes_actual'].map(fmt_money),
            'Estatus': inversionistas_f_cost['estatus'].apply(style_status),
        })
        detalle_inv = add_display_total_row(detalle_inv, 'Inversionista', {'Saldo Base': fmt_money(inversionistas_f_cost['saldo_base'].sum()), 'Monto Inversión': fmt_money(inversionistas_f_cost['monto_invertido'].sum()), 'Costo Anual Estimado': fmt_money(inversionistas_f_cost['costo_anual_estimado'].sum()), f'Interés {mes_actual_label}': fmt_money(inversionistas_f_cost['interes_mes_actual'].sum()), 'Pagado real mes': fmt_money(inversionistas_f_cost['monto_pagado_mes_actual'].sum())})
        render_premium_table(detalle_inv)
    else:
        st.info('No hay detalle de inversionistas para mostrar.')

with tab3:
    section_title('Resumen de colocación', 'Vista comercial, financiera y operativa de la cartera colocada.')
    render_narrative_band(coloc_text)
    st.info('En créditos, el interés del mes se calcula con los días reales del mes actual. El principal a cobrar del mes proviene del calendario de vencimientos.')
    b1, b2, b3 = st.columns(3)
    b1.metric('Monto colocado histórico', fmt_money(total_colocado))
    b2.metric('Saldo base cartera', fmt_money(saldo_base_colocacion_total))
    b3.metric('Tasa efectiva de colocación', fmt_pct(tasa_colocacion))
    b4, b5, b6 = st.columns(3)
    b4.metric('Ingreso anual estimado', fmt_money(ingreso_anual_total_colocacion))
    b5.metric(f'Interés del mes {mes_actual_label}', fmt_money(interes_cobrar_mes_actual), help='Interés del mes actual calculado con días reales del mes para cada crédito activo.')
    b6.metric(f'Principal a cobrar {mes_actual_label}', fmt_money(principal_cobrar_mes_actual), help='Principal con vencimiento dentro del mes actual según el calendario de cobros.')
    b7, b8, b9 = st.columns(3)
    b7.metric(f'Total a cobrar {mes_actual_label}', fmt_money(total_cobrar_mes_actual), help='Suma del interés del mes más el principal a cobrar dentro del mes actual.')
    b8.metric('Cobrado real del mes', fmt_money(cobrado_real_mes_actual))
    b9.metric('Pendiente por cobrar del mes', fmt_money(pendiente_cobrar_mes_actual))
    b10, b11, b12 = st.columns(3)
    b10.metric('Top 5 concentración', fmt_pct(conc_top5_pre))
    b11.metric('Concentración ajustada por margen', fmt_pct(conc_ajustada_rend) if pd.notna(conc_ajustada_rend) else '—')
    b12.metric('Cartera que destruye valor', fmt_money(monto_destruye_valor))
    col1, col2 = st.columns(2)
    with col1:
        section_title('Top clientes por monto colocado')
        top_pre = tabla_top(prestamos_f, 'cliente_credito', 'monto_colocado', 10)
        if not top_pre.empty:
            fig_pre = px.bar(top_pre, x='cliente_credito', y='monto_colocado', text='monto_colocado', title='Top clientes', color_discrete_sequence=[ENTURE_NAVY])
            fig_pre.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_pre.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Monto', margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_pre, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay clientes para mostrar.')
    with col2:
        section_title('Buckets de vencimiento de colocación')
        if not buckets_pre.empty:
            fig_bucket_pre = px.bar(buckets_pre, x='bucket', y='monto', text='monto', title='Distribución por bucket', color='bucket', color_discrete_sequence=PLOT_COLORS)
            fig_bucket_pre.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_bucket_pre.update_layout(height=420, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Monto', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_bucket_pre, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay vencimientos para mostrar.')
    section_title('Vigencia de créditos / colocación', 'Se muestran los 20 créditos de mayor monto.')
    if coloc_timeline_fig is not None:
        st.plotly_chart(coloc_timeline_fig, use_container_width=True, config=PLOT_CONFIG)
    else:
        st.info('No hay suficiente información para la gráfica de vigencias.')
    col5, col6 = st.columns(2)
    with col5:
        section_title('Margen financiero por cliente', 'Spread neto real estimado sobre saldo base por cliente.')
        if not cliente_margin_df.empty:
            top_margin = cliente_margin_df.head(10).copy()
            fig_margin = px.bar(top_margin, x='Cliente', y='Margen Anual', color='Margen Anual', title='Top clientes por margen anual', color_continuous_scale=['#B03927', '#E57A2E', '#181F30'])
            fig_margin.update_layout(height=380, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Margen anual', coloraxis_showscale=False, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_margin, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay información suficiente de margen por cliente.')
    with col6:
        section_title('Rentabilidad por segmento', 'Ingreso y margen anual agrupado por segmento.')
        if not segment_margin_df.empty:
            seg_plot = segment_margin_df.copy()
            fig_seg_margin = px.bar(seg_plot, x='Segmento', y='Margen Anual', text='Margen Anual', title='Margen anual por segmento', color_discrete_sequence=[ENTURE_ACCENT])
            fig_seg_margin.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig_seg_margin.update_layout(height=380, paper_bgcolor='white', plot_bgcolor='white', xaxis_title='', yaxis_title='Margen anual', margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_seg_margin, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay segmentos para evaluar rentabilidad.')

    section_title('Spread y rentabilidad de la cartera', 'Permite identificar clientes o segmentos que destruyen valor y concentración ajustada por rendimiento.')
    if not cliente_margin_df.empty:
        client_disp = pd.DataFrame({
            'Cliente': cliente_margin_df['Cliente'],
            'Saldo Base': cliente_margin_df['Saldo Base'].map(fmt_money),
            'Ingreso Anual': cliente_margin_df['Ingreso Anual'].map(fmt_money),
            'Margen Anual': cliente_margin_df['Margen Anual'].map(fmt_money),
            'Spread Neto': cliente_margin_df['Spread Neto'].map(fmt_pct),
        })
        client_disp = add_display_total_row(client_disp, 'Cliente', {
            'Saldo Base': fmt_money(cliente_margin_df['Saldo Base'].sum()),
            'Ingreso Anual': fmt_money(cliente_margin_df['Ingreso Anual'].sum()),
            'Margen Anual': fmt_money(cliente_margin_df['Margen Anual'].sum()),
        })
        render_premium_table(client_disp.head(16))
    else:
        st.info('No hay datos de spread neto por cliente.')

    section_title('Detalle de clientes / préstamos')
    if not prestamos_f_ing.empty:
        detalle_pre = pd.DataFrame({
            'Cliente': prestamos_f_ing['cliente_credito'],
            'Saldo Base Crédito': prestamos_f_ing['saldo_base_credito'].map(fmt_money),
            'Préstamo Histórico': prestamos_f_ing['monto_colocado'].map(fmt_money),
            'Tasa Anual': prestamos_f_ing['tasa_colocacion'].map(fmt_pct),
            'Ingreso Anual Estimado': prestamos_f_ing['ingreso_anual_estimado'].map(fmt_money),
            f'Interés del mes {mes_actual_label}': prestamos_f_ing['interes_mes_actual'].map(fmt_money),
            f'Interés a cobrar {mes_actual_label}': prestamos_f_ing['interes_cobrar_mes'].map(fmt_money),
            f'Principal a cobrar {mes_actual_label}': prestamos_f_ing['principal_cobrar_mes'].map(fmt_money),
            f'Total a cobrar {mes_actual_label}': prestamos_f_ing['total_cobrar_mes'].map(fmt_money),
            'Días del Mes Considerados': prestamos_f_ing['dias_mes_actual'].apply(lambda x: '—' if pd.isna(x) else int(x)),
            'Fecha Inicio': prestamos_f_ing['fecha_desembolso'].map(fmt_date),
            'Fecha de Término': prestamos_f_ing['fecha_vencimiento'].map(fmt_date),
            'Periodicidad Cobro': prestamos_f_ing['periodicidad_cobro'],
            'Tipo Capital': prestamos_f_ing['tipo_cobro_capital'],
            'Cobrado real mes': prestamos_f_ing['monto_cobrado_mes_actual'].map(fmt_money),
            'Estatus': prestamos_f_ing['estatus'].apply(style_status),
            'Segmento': prestamos_f_ing['segmento'] if 'segmento' in prestamos_f_ing.columns else '',
        })
        detalle_pre = add_display_total_row(detalle_pre, 'Cliente', {'Saldo Base Crédito': fmt_money(prestamos_f_ing['saldo_base_credito'].sum()), 'Préstamo Histórico': fmt_money(prestamos_f_ing['monto_colocado'].sum()), 'Ingreso Anual Estimado': fmt_money(prestamos_f_ing['ingreso_anual_estimado'].sum()), f'Interés del mes {mes_actual_label}': fmt_money(prestamos_f_ing['interes_mes_actual'].sum()), f'Interés a cobrar {mes_actual_label}': fmt_money(prestamos_f_ing['interes_cobrar_mes'].sum()), f'Principal a cobrar {mes_actual_label}': fmt_money(prestamos_f_ing['principal_cobrar_mes'].sum()), f'Total a cobrar {mes_actual_label}': fmt_money(prestamos_f_ing['total_cobrar_mes'].sum()), 'Cobrado real mes': fmt_money(prestamos_f_ing['monto_cobrado_mes_actual'].sum())})
        render_premium_table(detalle_pre)
    else:
        st.info('No hay detalle de clientes para mostrar.')

with tab4:
    section_title('Indicadores de riesgo', 'Monitoreo de liquidez, concentración, cobertura y alineación de plazos.')
    render_narrative_band(riesgo_text)
    r1, r2, r3, r4 = st.columns(4)
    r1.metric('Gap 30 días', fmt_money(gap_30)); r2.metric('Gap 60 días', fmt_money(gap_60)); r3.metric('Gap 90 días', fmt_money(gap_90)); r4.metric('Cobertura colocación/fondeo', f"{cobertura:,.2f}x" if pd.notna(cobertura) else '—')
    col1, col2 = st.columns(2)
    with col1:
        section_title('Comparativo de vencimientos próximos')
        vencimientos_df = pd.DataFrame({'Horizonte':['30 días','60 días','90 días'],'Fondeo':[venc_fondeo_30,venc_fondeo_60,venc_fondeo_90],'Colocación':[venc_coloc_30,venc_coloc_60,venc_coloc_90],'Gap':[gap_30,gap_60,gap_90]})
        venc_melt = vencimientos_df.melt(id_vars='Horizonte', value_vars=['Fondeo','Colocación'], var_name='Tipo', value_name='Monto')
        fig_gap = px.bar(venc_melt, x='Horizonte', y='Monto', color='Tipo', barmode='group', title='Fondeo vs colocación por horizonte', color_discrete_sequence=[ENTURE_PRIMARY, ENTURE_GOLD])
        fig_gap.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_gap, use_container_width=True, config=PLOT_CONFIG)
    with col2:
        section_title('Gap por horizonte')
        gap_df = pd.DataFrame({'Horizonte':['30 días','60 días','90 días'],'Gap':[gap_30,gap_60,gap_90]}); gap_df['Color'] = np.where(gap_df['Gap'] >= 0, 'Positivo', 'Negativo')
        fig_gap_line = px.bar(gap_df, x='Horizonte', y='Gap', color='Color', text='Gap', title='Holgura o déficit de liquidez', color_discrete_map={'Positivo': ENTURE_SUCCESS, 'Negativo': ENTURE_DANGER})
        fig_gap_line.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_gap_line.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_gap_line, use_container_width=True, config=PLOT_CONFIG)
    section_title('Matriz de semáforos')
    riesgos = pd.DataFrame({'Indicador':['Spread financiero','Concentración principal inversionista','Concentración principal cliente','Gap a 30 días','Descalce de plazos','Cobertura colocación/fondeo'],'Valor':[fmt_pct(spread),fmt_pct(conc_top1_inv),fmt_pct(conc_top1_pre),fmt_money(gap_30),fmt_days(descalce_plazos),f"{cobertura:,.2f}x" if pd.notna(cobertura) else '—'],'Semáforo':[semaforo(spread,'spread'),semaforo(conc_top1_inv,'concentracion_top1'),semaforo(conc_top1_pre,'concentracion_top1'),semaforo(gap_30,'gap'),semaforo(abs(descalce_plazos),'plazo'),semaforo(cobertura,'cobertura')]})
    render_premium_table(riesgos)

with tab5:
    section_title('Tesorería y programación de flujos', 'Foco en el mes actual: cuánto se espera pagar/cobrar, cuánto se reportó y qué sigue pendiente.')
    render_narrative_band(tesoreria_text)
    st.info("Columnas opcionales para control real: 'monto_pagado_mes_actual' en inversionistas y 'monto_cobrado_mes_actual' en préstamos. Si no vienen en el Excel, el sistema asume 0 y todo queda pendiente.")
    t1, t2, t3 = st.columns(3)
    t1.metric(f'Intereses a pagar {mes_actual_label}', fmt_money(total_pagar_mes_actual), help='Interés mensual estimado del fondeo del mes actual con base fija de 30.42 días.')
    t2.metric(f'Total a cobrar {mes_actual_label}', fmt_money(total_cobrar_mes_actual), help='Interés del mes con días reales más principal con vencimiento dentro del mes actual.')
    t3.metric(f'Flujo neto {mes_actual_label}', fmt_money(flujo_neto_mes_actual), help='Total a cobrar del mes menos intereses a pagar del mismo mes.')
    t4, t5, t6, t7 = st.columns(4)
    t4.metric('Pagado real del mes', fmt_money(pagado_real_mes_actual)); t5.metric('Cobrado real del mes', fmt_money(cobrado_real_mes_actual)); t6.metric('Pendiente por pagar del mes', fmt_money(pendiente_pagar_mes_actual)); t7.metric('Pendiente por cobrar del mes', fmt_money(pendiente_cobrar_mes_actual))

    section_title('Control de pagos del mes actual', 'Interés esperado del mes vs monto real reportado por inversionista.')
    if not resumen_pago_mes_actual.empty:
        pagos_show = resumen_pago_mes_actual.copy()
        pagos_show['Interés Esperado'] = pagos_show['Interés Esperado'].map(fmt_money)
        pagos_show['Principal Esperado'] = pagos_show['Principal Esperado'].map(fmt_money)
        pagos_show['Total Esperado'] = pagos_show['Total Esperado'].map(fmt_money)
        pagos_show['Real Reportado'] = pagos_show['Real Reportado'].map(fmt_money)
        pagos_show['Pendiente'] = pagos_show['Pendiente'].map(fmt_money)
        pagos_show['Exceso'] = pagos_show['Exceso'].map(fmt_money)
        pagos_show['Próxima Fecha'] = pagos_show['Próxima Fecha'].map(fmt_date)
        pagos_show['Estatus Control'] = pagos_show['Estatus Control'].apply(add_control_emoji)
        pagos_show = add_display_total_row(pagos_show, 'Contraparte', {'Interés Esperado': fmt_money(resumen_pago_mes_actual['Interés Esperado'].sum()), 'Total Esperado': fmt_money(resumen_pago_mes_actual['Total Esperado'].sum()), 'Real Reportado': fmt_money(resumen_pago_mes_actual['Real Reportado'].sum()), 'Pendiente': fmt_money(resumen_pago_mes_actual['Pendiente'].sum())})
        render_premium_table(pagos_show)
    else:
        st.info('No hay pagos programados para el mes actual.')

    section_title('Control de cobros del mes actual', 'Interés del mes con días reales más principal del mes vs monto real reportado por cliente.')
    if not resumen_cobro_mes_actual.empty:
        cobros_show = resumen_cobro_mes_actual.copy()
        cobros_show['Interés Esperado'] = cobros_show['Interés Esperado'].map(fmt_money)
        cobros_show['Principal Esperado'] = cobros_show['Principal Esperado'].map(fmt_money)
        cobros_show['Total Esperado'] = cobros_show['Total Esperado'].map(fmt_money)
        cobros_show['Real Reportado'] = cobros_show['Real Reportado'].map(fmt_money)
        cobros_show['Pendiente'] = cobros_show['Pendiente'].map(fmt_money)
        cobros_show['Exceso'] = cobros_show['Exceso'].map(fmt_money)
        cobros_show['Próxima Fecha'] = cobros_show['Próxima Fecha'].map(fmt_date)
        cobros_show['Estatus Control'] = cobros_show['Estatus Control'].apply(add_control_emoji)
        cobros_show = add_display_total_row(cobros_show, 'Contraparte', {'Interés Esperado': fmt_money(resumen_cobro_mes_actual['Interés Esperado'].sum()), 'Principal Esperado': fmt_money(resumen_cobro_mes_actual['Principal Esperado'].sum()), 'Total Esperado': fmt_money(resumen_cobro_mes_actual['Total Esperado'].sum()), 'Real Reportado': fmt_money(resumen_cobro_mes_actual['Real Reportado'].sum()), 'Pendiente': fmt_money(resumen_cobro_mes_actual['Pendiente'].sum())})
        render_premium_table(cobros_show)
    else:
        st.info('No hay cobros programados para el mes actual.')

    col_a, col_b = st.columns(2)
    with col_a:
        section_title('Flujo mensual proyectado', 'Cobros y pagos esperados por mes.')
        if not flujo_mes.empty:
            flujo_mes_melt = flujo_mes.melt(id_vars='mes', value_vars=['Cobros','Pagos'], var_name='Tipo', value_name='Monto')
            fig_flujo = px.bar(flujo_mes_melt, x='mes', y='Monto', color='Tipo', barmode='group', title='Cobros vs pagos mensuales', color_discrete_sequence=[ENTURE_SUCCESS, ENTURE_DANGER])
            fig_flujo.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_flujo, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay suficiente información para proyectar flujos.')
    with col_b:
        section_title('Flujo neto mensual', 'Resultado esperado de caja por mes.')
        if not flujo_mes.empty:
            flujo_mes_show = flujo_mes.copy(); flujo_mes_show['Color'] = np.where(flujo_mes_show['Neto'] >= 0, 'Positivo', 'Negativo')
            fig_neto = px.bar(flujo_mes_show, x='mes', y='Neto', color='Color', title='Neto mensual proyectado', color_discrete_map={'Positivo': ENTURE_PRIMARY, 'Negativo': ENTURE_DANGER})
            fig_neto.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white', legend_title=None, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_neto, use_container_width=True, config=PLOT_CONFIG)
        else:
            st.info('No hay flujo neto suficiente para graficar.')

    section_title('Agenda operativa de flujos', 'Calendario completo de pagos y cobros.')
    if not calendario_flujos.empty:
        calendario_show = calendario_flujos.copy()
        calendario_show['Fecha'] = calendario_show['Fecha'].map(fmt_date)
        calendario_show['Interés'] = calendario_show['Interés'].map(fmt_money)
        calendario_show['Principal'] = calendario_show['Principal'].map(fmt_money)
        calendario_show['Total'] = calendario_show['Total'].map(fmt_money)
        calendario_show['Estatus'] = calendario_show['Estatus'].apply(style_event_status)
        st.dataframe(calendario_show[['Fecha','Tipo Flujo','Cartera','Contraparte','Periodicidad','Tipo Capital','Interés','Principal','Total','Estatus']], use_container_width=True, hide_index=True)
    else:
        st.info('No hay calendario de flujos para mostrar con la información actual.')

st.markdown("<div class='footer-note'>Siguiente mejora recomendada: exportación a Excel del control del mes actual, filtro por moneda/vehículo y carga de estatus real pagado/cobrado por evento.</div>", unsafe_allow_html=True)
