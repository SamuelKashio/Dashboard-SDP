import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta, date
import time
from functools import lru_cache
import json
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="KashIO · Support Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stDateInput label { color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

  /* Main background */
  .main { background: #0f172a; }
  .block-container { padding: 1rem 2rem 2rem; background: #0f172a; }

  /* KPI Cards */
  .kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 12px 0 0 12px;
  }
  .kpi-blue::before   { background: #3b82f6; }
  .kpi-green::before  { background: #22c55e; }
  .kpi-yellow::before { background: #f59e0b; }
  .kpi-red::before    { background: #ef4444; }
  .kpi-purple::before { background: #a855f7; }
  .kpi-cyan::before   { background: #06b6d4; }
  .kpi-label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 0.35rem; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #f1f5f9; line-height: 1; }
  .kpi-sub   { font-size: 0.75rem; color: #64748b; margin-top: 0.4rem; }
  .kpi-delta-pos { color: #22c55e; font-weight: 600; }
  .kpi-delta-neg { color: #ef4444; font-weight: 600; }

  /* Donut KPI */
  .donut-label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; text-align: center; margin-top: 0.5rem; }

  /* Section title */
  .section-title {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
  }

  /* Page header */
  .page-header {
    background: linear-gradient(90deg, #1e3a5f 0%, #1e293b 100%);
    border: 1px solid #2563eb44;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .page-header h1 { font-size: 1.4rem; font-weight: 700; color: #e2e8f0; margin: 0; }
  .page-header p  { font-size: 0.8rem; color: #64748b; margin: 0; }

  /* Alert banner */
  .alert-critical {
    background: #450a0a; border: 1px solid #ef4444;
    border-radius: 8px; padding: 0.75rem 1rem;
    color: #fca5a5; font-size: 0.85rem; margin-bottom: 0.5rem;
  }
  .alert-warning {
    background: #1c1400; border: 1px solid #f59e0b;
    border-radius: 8px; padding: 0.75rem 1rem;
    color: #fcd34d; font-size: 0.85rem; margin-bottom: 0.5rem;
  }

  /* Plotly chart backgrounds */
  .js-plotly-plot { border-radius: 10px; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { background: #1e293b; border-radius: 8px; gap: 4px; padding: 4px; }
  .stTabs [data-baseweb="tab"] { background: transparent; color: #64748b; border-radius: 6px; font-weight: 500; }
  .stTabs [aria-selected="true"] { background: #3b82f6 !important; color: white !important; }

  /* Dataframe */
  .dataframe-container { border-radius: 10px; overflow: hidden; border: 1px solid #334155; }

  /* Config inputs */
  .stTextInput input, .stTextArea textarea {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px;
  }

  /* Nav button */
  .nav-btn {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.6rem 1rem; border-radius: 8px;
    margin-bottom: 0.25rem; cursor: pointer;
    font-size: 0.85rem; font-weight: 500;
    transition: background 0.15s;
    color: #94a3b8;
  }
  .nav-btn:hover { background: #1e293b; color: #e2e8f0; }
  .nav-btn.active { background: #1d4ed8; color: white; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES Y COLORES
# ─────────────────────────────────────────────
CHART_THEME = {
    "bg": "#0f172a",
    "paper": "#1e293b",
    "grid": "#334155",
    "text": "#94a3b8",
    "blue": "#3b82f6",
    "green": "#22c55e",
    "yellow": "#f59e0b",
    "red": "#ef4444",
    "purple": "#a855f7",
    "cyan": "#06b6d4",
    "orange": "#f97316",
}

PRIORITY_COLORS = {
    "Critica": "#ef4444",
    "Alta": "#f97316",
    "Media": "#f59e0b",
    "Baja": "#22c55e",
    "Sin Prioridad": "#64748b",
}

STATUS_COLORS = {
    "Abierta": "#3b82f6",
    "En Progreso": "#f59e0b",
    "Resuelta": "#22c55e",
    "Completada": "#06b6d4",
    "Pendiente": "#a855f7",
    "Cancelada": "#64748b",
}

def chart_layout(title="", height=300, showlegend=True):
    return dict(
        title=dict(text=title, font=dict(color="#e2e8f0", size=13), x=0),
        plot_bgcolor=CHART_THEME["paper"],
        paper_bgcolor=CHART_THEME["paper"],
        font=dict(color=CHART_THEME["text"], family="Inter"),
        height=height,
        showlegend=showlegend,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
        margin=dict(l=10, r=10, t=40 if title else 15, b=10),
        xaxis=dict(gridcolor=CHART_THEME["grid"], linecolor=CHART_THEME["grid"], zerolinecolor=CHART_THEME["grid"]),
        yaxis=dict(gridcolor=CHART_THEME["grid"], linecolor=CHART_THEME["grid"], zerolinecolor=CHART_THEME["grid"]),
    )

# ─────────────────────────────────────────────
# SERVICEDESKPLUS API CLIENT
# ─────────────────────────────────────────────
class SDPClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "TECHNICIAN_KEY": api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        })

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/api/v3/{endpoint}"
        try:
            r = self.session.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"error": "connection_error", "message": "No se pudo conectar al servidor SDP"}
        except requests.exceptions.Timeout:
            return {"error": "timeout", "message": "El servidor SDP no respondió a tiempo"}
        except Exception as e:
            return {"error": str(type(e).__name__), "message": str(e)}

    def test_connection(self) -> tuple[bool, str]:
        result = self._get("requests", params={"input_data": json.dumps({"list_info": {"row_count": 1}})})
        if "error" in result:
            return False, result.get("message", "Error desconocido")
        return True, "Conexión exitosa"

    def get_requests(self, start_index=1, row_count=100, filters=None) -> dict:
        list_info = {"start_index": start_index, "row_count": row_count, "sort_field": "created_time", "sort_order": "desc"}
        if filters:
            list_info["search_criteria"] = filters
        input_data = {"list_info": list_info}
        return self._get("requests", params={"input_data": json.dumps(input_data)})

    def get_all_requests_paginated(self, date_from=None, date_to=None, max_records=2000) -> pd.DataFrame:
        all_requests = []
        start = 1
        row_count = 100

        filters = []
        if date_from:
            ts_from = int(datetime.combine(date_from, datetime.min.time()).timestamp() * 1000)
            filters.append({"field": "created_time", "condition": "gt", "value": str(ts_from)})
        if date_to:
            ts_to = int(datetime.combine(date_to, datetime.max.time()).timestamp() * 1000)
            filters.append({"field": "created_time", "condition": "lt", "value": str(ts_to)})

        while len(all_requests) < max_records:
            data = self.get_requests(start, row_count, filters if filters else None)
            if "error" in data:
                break
            reqs = data.get("requests", [])
            if not reqs:
                break
            all_requests.extend(reqs)
            if len(reqs) < row_count:
                break
            start += row_count
            time.sleep(0.1)

        return self._parse_requests(all_requests)

    def _parse_requests(self, raw_list: list) -> pd.DataFrame:
        rows = []
        for r in raw_list:
            def gn(obj): return obj.get("name", "") if isinstance(obj, dict) else ""
            def gv(obj, key="value"): return obj.get(key, "") if isinstance(obj, dict) else ""

            created_ts = r.get("created_time", {})
            resolved_ts = r.get("resolved_time", {})
            closed_ts = r.get("closed_time", {})
            first_response_ts = r.get("first_response_due_by_time", {})

            def parse_ts(ts_obj):
                if isinstance(ts_obj, dict) and "value" in ts_obj:
                    try: return pd.to_datetime(int(ts_obj["value"]), unit="ms")
                    except: pass
                return pd.NaT

            created = parse_ts(created_ts)
            resolved = parse_ts(resolved_ts)
            closed = parse_ts(closed_ts)

            # SLA
            sla_obj = r.get("sla", {})
            sla_name = gn(sla_obj) if isinstance(sla_obj, dict) else ""

            # Custom fields
            udf = r.get("udf_fields", {})
            empresa = udf.get("udf_sline_1", "") or udf.get("udf_char1", "")
            tipo_empresa = udf.get("udf_sline_2", "") or udf.get("udf_char2", "")
            region = udf.get("udf_sline_3", "") or udf.get("udf_char3", "")
            erp = udf.get("udf_sline_4", "") or ""
            corporativo = udf.get("udf_sline_5", "") or ""
            informativo = udf.get("udf_sline_6", "") or ""

            # Resolution SLA flag
            due_ts = r.get("due_by_time", {})
            due = parse_ts(due_ts)
            sla_resolution_met = False
            if pd.notna(resolved) and pd.notna(due):
                sla_resolution_met = resolved <= due
            elif pd.notna(closed) and pd.notna(due):
                sla_resolution_met = closed <= due

            # First response SLA
            fr_due = parse_ts(first_response_ts)
            fr_actual = parse_ts(r.get("first_response_time", {}))
            sla_first_response_met = False
            if pd.notna(fr_actual) and pd.notna(fr_due):
                sla_first_response_met = fr_actual <= fr_due

            # Resolution time in hours
            res_time_hrs = np.nan
            if pd.notna(resolved) and pd.notna(created):
                res_time_hrs = (resolved - created).total_seconds() / 3600
            elif pd.notna(closed) and pd.notna(created):
                res_time_hrs = (closed - created).total_seconds() / 3600

            # Closed same day
            closed_same_day = False
            if pd.notna(created) and (pd.notna(resolved) or pd.notna(closed)):
                end = resolved if pd.notna(resolved) else closed
                closed_same_day = created.date() == end.date()

            status_name = gn(r.get("status", {}))
            is_closed = status_name.lower() in ["completada", "resuelta", "cerrada", "completed", "resolved", "closed"]

            rows.append({
                "id": r.get("id", ""),
                "display_id": r.get("display_id", ""),
                "asunto": r.get("subject", ""),
                "estado": status_name,
                "prioridad": gn(r.get("priority", {})),
                "tipo": gn(r.get("request_type", {})),
                "categoria": gn(r.get("category", {})),
                "subcategoria": gn(r.get("subcategory", {})),
                "grupo": gn(r.get("group", {})),
                "tecnico": gn(r.get("technician", {})),
                "solicitante": gn(r.get("requester", {})),
                "empresa": empresa,
                "tipo_empresa": tipo_empresa,
                "region": region,
                "erp": erp,
                "corporativo": corporativo,
                "informativo": informativo,
                "fecha_creacion": created,
                "fecha_resolucion": resolved,
                "fecha_cierre": closed,
                "fecha_vencimiento": due,
                "sla_name": sla_name,
                "sla_resolucion_cumplido": sla_resolution_met,
                "sla_primera_respuesta_cumplido": sla_first_response_met,
                "tiempo_resolucion_hrs": res_time_hrs,
                "cerrado_mismo_dia": closed_same_day,
                "is_closed": is_closed,
            })

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["anio"] = df["fecha_creacion"].dt.year
        df["mes"] = df["fecha_creacion"].dt.month
        df["mes_nombre"] = df["fecha_creacion"].dt.strftime("%b %Y")
        df["semana"] = df["fecha_creacion"].dt.isocalendar().week
        df["dia_semana"] = df["fecha_creacion"].dt.day_name()
        return df

    def get_survey_responses(self, start=1, row_count=100) -> pd.DataFrame:
        data = self._get("requests", params={
            "input_data": json.dumps({
                "list_info": {"start_index": start, "row_count": row_count},
                "fields_required": ["id", "subject", "technician", "group", "survey"]
            })
        })
        rows = []
        for r in data.get("requests", []):
            survey = r.get("survey", {})
            if survey and isinstance(survey, dict) and survey.get("rating"):
                rows.append({
                    "id": r.get("id"),
                    "tecnico": r.get("technician", {}).get("name", "") if r.get("technician") else "",
                    "grupo": r.get("group", {}).get("name", "") if r.get("group") else "",
                    "rating_atencion": survey.get("rating", 0),
                    "comentario": survey.get("comment", ""),
                })
        return pd.DataFrame(rows) if rows else pd.DataFrame()

# ─────────────────────────────────────────────
# DEMO DATA GENERATOR
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def generate_demo_data(n=800) -> pd.DataFrame:
    np.random.seed(42)
    n = n

    start_date = datetime.now() - timedelta(days=365)
    fechas = [start_date + timedelta(days=np.random.exponential(1)) * i // (n // 365)
              for i in range(n)]
    fechas = sorted([start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n)])

    tipos = np.random.choice(["Incidente", "Requerimiento", "Consulta"], n, p=[0.45, 0.35, 0.20])
    prioridades = np.random.choice(["Critica", "Alta", "Media", "Baja"], n, p=[0.10, 0.25, 0.40, 0.25])
    estados = np.random.choice(["Completada", "Resuelta", "En Progreso", "Abierta", "Pendiente"], n,
                               p=[0.45, 0.25, 0.15, 0.10, 0.05])

    grupos = ["TI General", "Infraestructura", "Aplicaciones ERP", "Soporte Usuario", "Redes & Seguridad"]
    tecnicos = {
        "TI General": ["Juan Pérez", "María García"],
        "Infraestructura": ["Carlos López", "Ana Torres"],
        "Aplicaciones ERP": ["Roberto Silva", "Diana Ruiz"],
        "Soporte Usuario": ["Luis Herrera", "Carmen Flores"],
        "Redes & Seguridad": ["Miguel Ángel", "Patricia Ríos"],
    }
    empresas = ["Empresa Alpha", "Beta Corp", "Gamma SA", "Delta Group", "Epsilon Ltd",
                "Zeta Industries", "Eta Solutions", "Theta Corp"]
    tipos_empresa = np.random.choice(["Corporativa", "PYME", "Subsidiaria"], n, p=[0.4, 0.35, 0.25])
    regiones = np.random.choice(["Norte", "Sur", "Centro", "Oriente", "Occidente"], n)
    categorias = np.random.choice(["Hardware", "Software", "Red", "Accesos", "ERP", "Correo", "Impresión"], n)

    grupo_arr = np.random.choice(grupos, n)
    tecnico_arr = [np.random.choice(tecnicos[g]) for g in grupo_arr]
    empresa_arr = np.random.choice(empresas, n)

    # SLA compliance based on priority
    sla_res_prob = {"Critica": 0.72, "Alta": 0.80, "Media": 0.88, "Baja": 0.93}
    sla_fr_prob  = {"Critica": 0.78, "Alta": 0.85, "Media": 0.90, "Baja": 0.95}
    sla_res_arr = [np.random.random() < sla_res_prob[p] for p in prioridades]
    sla_fr_arr  = [np.random.random() < sla_fr_prob[p]  for p in prioridades]

    # Resolution time
    res_time_map = {"Critica": (2, 8), "Alta": (4, 24), "Media": (8, 48), "Baja": (24, 96)}
    res_hrs = [np.random.uniform(*res_time_map[p]) for p in prioridades]

    fechas_resolucion = []
    for i, (fd, rh, est) in enumerate(zip(fechas, res_hrs, estados)):
        if est in ["Completada", "Resuelta"]:
            fechas_resolucion.append(fd + timedelta(hours=rh))
        else:
            fechas_resolucion.append(pd.NaT)

    closed_same_day = [
        (pd.notna(fr) and fc.date() == fr.date())
        for fc, fr in zip(fechas, fechas_resolucion)
    ]

    is_closed = [e in ["Completada", "Resuelta"] for e in estados]

    # CSAT scores (only for closed tickets)
    csat_atencion = [np.random.uniform(3.5, 5.0) if ic else np.nan for ic in is_closed]
    csat_rapidez  = [np.random.uniform(3.0, 5.0) if ic else np.nan for ic in is_closed]
    csat_solucion = [np.random.uniform(3.2, 5.0) if ic else np.nan for ic in is_closed]
    csat_global   = [(a + r + s) / 3 if not np.isnan(a) else np.nan
                     for a, r, s in zip(csat_atencion, csat_rapidez, csat_solucion)]

    df = pd.DataFrame({
        "id": range(1, n + 1),
        "display_id": [f"REQ-{1000+i}" for i in range(n)],
        "asunto": [f"Ticket #{i+1} - {np.random.choice(['Problema con', 'Solicitud de', 'Consulta sobre'])} {np.random.choice(['sistema', 'acceso', 'impresora', 'red', 'email'])}" for i in range(n)],
        "estado": estados,
        "prioridad": prioridades,
        "tipo": tipos,
        "categoria": categorias,
        "subcategoria": np.random.choice(["Nivel 1", "Nivel 2", "Nivel 3", "Especialista"], n),
        "grupo": grupo_arr,
        "tecnico": tecnico_arr,
        "solicitante": [f"Usuario {i}" for i in range(n)],
        "empresa": empresa_arr,
        "tipo_empresa": tipos_empresa,
        "region": regiones,
        "erp": np.random.choice(["SAP", "Oracle", "Odoo", "N/A"], n, p=[0.3, 0.2, 0.2, 0.3]),
        "corporativo": np.random.choice(["Sí", "No"], n, p=[0.3, 0.7]),
        "informativo": np.random.choice(["Sí", "No"], n, p=[0.15, 0.85]),
        "fecha_creacion": fechas,
        "fecha_resolucion": fechas_resolucion,
        "fecha_cierre": fechas_resolucion,
        "sla_resolucion_cumplido": sla_res_arr,
        "sla_primera_respuesta_cumplido": sla_fr_arr,
        "tiempo_resolucion_hrs": res_hrs,
        "cerrado_mismo_dia": closed_same_day,
        "is_closed": is_closed,
        "csat_atencion": csat_atencion,
        "csat_rapidez": csat_rapidez,
        "csat_solucion": csat_solucion,
        "csat_global": csat_global,
    })

    df["fecha_creacion"] = pd.to_datetime(df["fecha_creacion"])
    df["fecha_resolucion"] = pd.to_datetime(df["fecha_resolucion"])
    df["anio"] = df["fecha_creacion"].dt.year
    df["mes"] = df["fecha_creacion"].dt.month
    df["mes_nombre"] = df["fecha_creacion"].dt.strftime("%b %Y")
    df["dia_semana"] = df["fecha_creacion"].dt.day_name()
    return df

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "general"
if "sdp_url" not in st.session_state:
    st.session_state.sdp_url = ""
if "sdp_key" not in st.session_state:
    st.session_state.sdp_key = ""
if "use_demo" not in st.session_state:
    st.session_state.use_demo = True
if "df_cache" not in st.session_state:
    st.session_state.df_cache = None
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

# ─────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_data_from_api(url, key, date_from, date_to):
    client = SDPClient(url, key)
    return client.get_all_requests_paginated(date_from, date_to)

def get_data(date_from=None, date_to=None) -> pd.DataFrame:
    if st.session_state.use_demo:
        df = generate_demo_data()
    else:
        if not st.session_state.sdp_url or not st.session_state.sdp_key:
            return pd.DataFrame()
        with st.spinner("Cargando datos desde ServiceDesk Plus..."):
            df = load_data_from_api(
                st.session_state.sdp_url,
                st.session_state.sdp_key,
                date_from, date_to
            )
    return df

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo area
        st.markdown("""
        <div style="padding: 1rem 0 1.5rem; border-bottom: 1px solid #334155; margin-bottom: 1rem;">
          <div style="font-size:1.3rem; font-weight:800; color:#f1f5f9; letter-spacing:-0.02em;">
            🎯 KashIO Support
          </div>
          <div style="font-size:0.72rem; color:#475569; margin-top:2px;">
            Dashboard Supervisor · ServiceDesk Plus
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        pages = [
            ("general",    "📊", "Informe General"),
            ("sla_fr",     "⚡", "SLA · 1ra Respuesta"),
            ("sla_res",    "✅", "SLA · Resolución"),
            ("grupos",     "👥", "Grupo Resolutor"),
            ("encuestas",  "⭐", "Encuestas CSAT"),
            ("alertas",    "🚨", "Alertas & Pendientes"),
            ("config",     "⚙️", "Configuración API"),
        ]

        for pid, icon, label in pages:
            is_active = st.session_state.page == pid
            style = "background:#1d4ed8;color:#fff" if is_active else "background:transparent;color:#94a3b8"
            if st.button(f"{icon}  {label}", key=f"nav_{pid}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = pid
                st.rerun()

        st.markdown("<div style='border-top:1px solid #334155;margin:1rem 0;'></div>", unsafe_allow_html=True)

        # ─── FILTROS ───
        st.markdown("<div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#475569;margin-bottom:0.75rem;'>🔍 Filtros Globales</div>", unsafe_allow_html=True)

        df_raw = generate_demo_data() if st.session_state.use_demo else get_data()

        if df_raw is not None and len(df_raw) > 0:
            min_d = df_raw["fecha_creacion"].min().date()
            max_d = df_raw["fecha_creacion"].max().date()
        else:
            min_d = date.today() - timedelta(days=365)
            max_d = date.today()

        col1, col2 = st.columns(2)
        with col1:
            date_from = st.date_input("Desde", value=min_d, min_value=min_d, max_value=max_d, key="f_from")
        with col2:
            date_to = st.date_input("Hasta", value=max_d, min_value=min_d, max_value=max_d, key="f_to")

        if df_raw is not None and len(df_raw) > 0:
            grupos_opt = ["Todos"] + sorted(df_raw["grupo"].dropna().unique().tolist())
            tecnicos_opt = ["Todos"] + sorted(df_raw["tecnico"].dropna().unique().tolist())
            prioridades_opt = ["Todas"] + sorted(df_raw["prioridad"].dropna().unique().tolist())
            estados_opt = ["Todos"] + sorted(df_raw["estado"].dropna().unique().tolist())
            tipos_opt = ["Todos"] + sorted(df_raw["tipo"].dropna().unique().tolist())
            empresas_opt = ["Todas"] + sorted(df_raw["empresa"].dropna().unique().tolist())
            regiones_opt = ["Todas"] + sorted(df_raw["region"].dropna().unique().tolist())
        else:
            grupos_opt = tecnicos_opt = prioridades_opt = estados_opt = tipos_opt = empresas_opt = regiones_opt = ["Todos"]

        f_grupo     = st.selectbox("Grupo", grupos_opt, key="f_grupo")
        f_tecnico   = st.selectbox("Técnico", tecnicos_opt, key="f_tecnico")
        f_prioridad = st.selectbox("Prioridad", prioridades_opt, key="f_prioridad")
        f_tipo      = st.selectbox("Tipo", tipos_opt, key="f_tipo")
        f_empresa   = st.selectbox("Empresa", empresas_opt, key="f_empresa")
        f_region    = st.selectbox("Región", regiones_opt, key="f_region")
        f_estado    = st.selectbox("Estado", estados_opt, key="f_estado")

        st.markdown("<div style='border-top:1px solid #334155;margin:1rem 0;'></div>", unsafe_allow_html=True)

        # Refresh
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Actualizar", use_container_width=True, type="primary"):
                st.cache_data.clear()
                st.session_state.last_refresh = datetime.now()
                st.rerun()
        if st.session_state.last_refresh:
            st.markdown(f"<div style='font-size:0.65rem;color:#475569;text-align:center;'>Actualizado: {st.session_state.last_refresh.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

        # Demo / API toggle
        use_demo = st.toggle("Usar datos demo", value=st.session_state.use_demo, key="demo_toggle")
        if use_demo != st.session_state.use_demo:
            st.session_state.use_demo = use_demo
            st.rerun()

        if st.session_state.use_demo:
            st.markdown("<div style='font-size:0.7rem;color:#f59e0b;padding:0.4rem 0.6rem;background:#1c1400;border-radius:6px;border:1px solid #f59e0b44;'>⚠️ Modo Demo activo</div>", unsafe_allow_html=True)

    return date_from, date_to, {
        "grupo": f_grupo, "tecnico": f_tecnico, "prioridad": f_prioridad,
        "tipo": f_tipo, "empresa": f_empresa, "region": f_region, "estado": f_estado
    }

# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
def apply_filters(df: pd.DataFrame, date_from, date_to, filters: dict) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return df
    mask = (df["fecha_creacion"].dt.date >= date_from) & (df["fecha_creacion"].dt.date <= date_to)
    df = df[mask].copy()

    if filters["grupo"] != "Todos":
        df = df[df["grupo"] == filters["grupo"]]
    if filters["tecnico"] != "Todos":
        df = df[df["tecnico"] == filters["tecnico"]]
    if filters["prioridad"] != "Todas":
        df = df[df["prioridad"] == filters["prioridad"]]
    if filters["tipo"] != "Todos":
        df = df[df["tipo"] == filters["tipo"]]
    if filters["empresa"] != "Todas":
        df = df[df["empresa"] == filters["empresa"]]
    if filters["region"] != "Todas":
        df = df[df["region"] == filters["region"]]
    if filters["estado"] != "Todos":
        df = df[df["estado"] == filters["estado"]]

    return df

# ─────────────────────────────────────────────
# KPI CARD HELPER
# ─────────────────────────────────────────────
def kpi_card(label, value, color="blue", sub="", delta=None, icon=""):
    delta_html = ""
    if delta is not None:
        cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<span class="{cls}">{arrow} {abs(delta):.1f}%</span>'
    return f"""
    <div class="kpi-card kpi-{color}">
      <div class="kpi-label">{icon} {label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub} {delta_html}</div>
    </div>
    """

def donut_kpi(value_pct, label, color):
    fig = go.Figure(go.Pie(
        values=[value_pct, 100 - value_pct],
        hole=0.72,
        marker_colors=[color, "#1e293b"],
        textinfo="none",
        showlegend=False,
        hoverinfo="none",
    ))
    fig.update_layout(
        plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
        margin=dict(l=5, r=5, t=5, b=5),
        height=130,
        annotations=[dict(
            text=f"<b>{value_pct:.0f}%</b>",
            x=0.5, y=0.5,
            font=dict(size=20, color="#f1f5f9", family="Inter"),
            showarrow=False,
        )]
    )
    return fig

# ─────────────────────────────────────────────
# PAGE: INFORME GENERAL
# ─────────────────────────────────────────────
def page_general(df):
    st.markdown("""
    <div class="page-header">
      <div>📊</div>
      <div>
        <h1>Informe General de Resolución de Tickets</h1>
        <p>Visión consolidada del desempeño del área de soporte</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles para el período seleccionado.")
        return

    # ── MÉTRICAS PRINCIPALES ──
    total = len(df)
    cerrados = df["is_closed"].sum()
    pendientes = (~df["is_closed"]).sum()
    mismo_dia = df["cerrado_mismo_dia"].sum()
    pct_mismo_dia = (mismo_dia / cerrados * 100) if cerrados > 0 else 0
    sla_cumplido = df[df["is_closed"]]["sla_resolucion_cumplido"].sum()
    pct_sla = (sla_cumplido / cerrados * 100) if cerrados > 0 else 0
    tiempo_prom = df[df["is_closed"] & df["tiempo_resolucion_hrs"].notna()]["tiempo_resolucion_hrs"].mean()
    t_prom_str = f"{tiempo_prom:.1f}h" if not np.isnan(tiempo_prom) else "N/A"

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.markdown(kpi_card("Total Tickets", f"{total:,}", "blue", "período actual", icon="🎫"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Cerrados", f"{cerrados:,}", "green", f"{cerrados/total*100:.0f}% del total", icon="✅"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Pendientes", f"{pendientes:,}", "yellow", "sin resolver", icon="⏳"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Cerrados mismo día", f"{mismo_dia:,}", "cyan", f"{pct_mismo_dia:.0f}% de cerrados", icon="⚡"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("SLA Resolución", f"{pct_sla:.0f}%", "purple" if pct_sla >= 85 else "red", "cumplimiento", icon="🎯"), unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("Tiempo Promedio", t_prom_str, "blue", "resolución", icon="⏱️"), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── ROW 2: LÍNEA DE TENDENCIA + PIE ──
    col_l, col_r = st.columns([3, 1])

    with col_l:
        df_trend = df.groupby("mes_nombre").agg(
            total=("id", "count"),
            cerrados=("is_closed", "sum"),
            mismo_dia=("cerrado_mismo_dia", "sum")
        ).reset_index()
        # Sort by date
        df_trend["sort_key"] = pd.to_datetime(df_trend["mes_nombre"], format="%b %Y", errors="coerce")
        df_trend = df_trend.sort_values("sort_key")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_trend["mes_nombre"], y=df_trend["total"],
            name="Total Tickets", line=dict(color=CHART_THEME["blue"], width=2.5),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.1)", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=df_trend["mes_nombre"], y=df_trend["cerrados"],
            name="Cerrados", line=dict(color=CHART_THEME["green"], width=2, dash="dot"),
            mode="lines+markers"))
        fig.add_trace(go.Scatter(x=df_trend["mes_nombre"], y=df_trend["mismo_dia"],
            name="Cerrados mismo día", line=dict(color=CHART_THEME["cyan"], width=1.5, dash="dash"),
            mode="lines+markers"))
        fig.update_layout(**chart_layout("📈 Tendencia mensual de tickets", height=280))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        tipo_counts = df["tipo"].value_counts().reset_index()
        tipo_counts.columns = ["tipo", "count"]
        fig_pie = px.pie(tipo_counts, values="count", names="tipo",
            color_discrete_sequence=[CHART_THEME["blue"], CHART_THEME["green"], CHART_THEME["yellow"]])
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(**chart_layout("Por tipo", height=280, showlegend=False))
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # ── ROW 3: BARRAS POR EMPRESA + COLUMNAS POR TIPO EMPRESA ──
    col_a, col_b = st.columns(2)

    with col_a:
        df_emp = df.groupby("empresa").agg(
            total=("id", "count"),
            cerrados=("is_closed", "sum")
        ).reset_index().sort_values("total", ascending=True).tail(10)
        fig_emp = go.Figure()
        fig_emp.add_trace(go.Bar(y=df_emp["empresa"], x=df_emp["total"],
            name="Total", orientation="h", marker_color=CHART_THEME["blue"]))
        fig_emp.add_trace(go.Bar(y=df_emp["empresa"], x=df_emp["cerrados"],
            name="Cerrados", orientation="h", marker_color=CHART_THEME["green"]))
        fig_emp.update_layout(**chart_layout("🏢 Tickets por empresa (Top 10)", height=300),
            barmode="overlay")
        st.plotly_chart(fig_emp, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        df_tipo_emp = df.groupby(["tipo_empresa", "tipo"]).size().reset_index(name="count")
        fig_te = px.bar(df_tipo_emp, x="tipo_empresa", y="count", color="tipo",
            color_discrete_map={"Incidente": CHART_THEME["red"],
                                "Requerimiento": CHART_THEME["blue"],
                                "Consulta": CHART_THEME["yellow"]},
            barmode="group")
        fig_te.update_layout(**chart_layout("🏭 Por tipo de empresa", height=300))
        st.plotly_chart(fig_te, use_container_width=True, config={"displayModeBar": False})

    # ── ROW 4: TABLA RESUMEN POR ESTADO + SUBCATEGORÍA ──
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("<div class='section-title'>Resumen por Estado</div>", unsafe_allow_html=True)
        df_est = df.groupby("estado").agg(
            total=("id", "count"),
            sla_ok=("sla_resolucion_cumplido", "sum")
        ).reset_index()
        df_est["sla_%"] = (df_est["sla_ok"] / df_est["total"] * 100).round(1)
        df_est = df_est.rename(columns={"estado": "Estado", "total": "Total", "sla_%": "SLA%"})
        st.dataframe(df_est[["Estado", "Total", "SLA%"]], use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("<div class='section-title'>Top Subcategorías</div>", unsafe_allow_html=True)
        df_sub = df.groupby("subcategoria").size().reset_index(name="Total").sort_values("Total", ascending=False).head(8)
        fig_sub = px.bar(df_sub, x="Total", y="subcategoria", orientation="h",
            color="Total", color_continuous_scale=["#1e3a5f", "#3b82f6"])
        fig_sub.update_layout(**chart_layout(height=250, showlegend=False),
            coloraxis_showscale=False)
        st.plotly_chart(fig_sub, use_container_width=True, config={"displayModeBar": False})

    # ── ROW 5: DETALLE DE TICKETS ──
    st.markdown("<div class='section-title'>📋 Detalle de Tickets Recientes</div>", unsafe_allow_html=True)
    display_cols = ["display_id", "fecha_creacion", "asunto", "solicitante", "tipo", "estado", "prioridad", "tecnico", "empresa"]
    df_disp = df[display_cols].head(50).copy()
    df_disp["fecha_creacion"] = df_disp["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
    df_disp.columns = ["ID", "Fecha", "Asunto", "Solicitante", "Tipo", "Estado", "Prioridad", "Técnico", "Empresa"]
    st.dataframe(df_disp, use_container_width=True, hide_index=True, height=280)

    # ── ROW 6: DISTRIBUCIÓN REGIÓN + DÍA SEMANA ──
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        df_reg = df.groupby(["region", "tipo"]).size().reset_index(name="count")
        fig_reg = px.bar(df_reg, x="region", y="count", color="tipo",
            color_discrete_map={"Incidente": CHART_THEME["red"],
                                "Requerimiento": CHART_THEME["blue"],
                                "Consulta": CHART_THEME["yellow"]})
        fig_reg.update_layout(**chart_layout("🗺️ Distribución por Región", height=260))
        st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})

    with col_m2:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df_dow = df["dia_semana"].value_counts().reindex(day_order).fillna(0).reset_index()
        df_dow.columns = ["dia", "count"]
        day_es = {"Monday":"Lun","Tuesday":"Mar","Wednesday":"Mié","Thursday":"Jue",
                  "Friday":"Vie","Saturday":"Sáb","Sunday":"Dom"}
        df_dow["dia"] = df_dow["dia"].map(day_es)
        fig_dow = px.bar(df_dow, x="dia", y="count",
            color="count", color_continuous_scale=["#1e3a5f", "#3b82f6"])
        fig_dow.update_layout(**chart_layout("📅 Tickets por día de semana", height=260, showlegend=False),
            coloraxis_showscale=False)
        st.plotly_chart(fig_dow, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
# PAGE: SLA PRIMERA RESPUESTA
# ─────────────────────────────────────────────
def page_sla_fr(df):
    st.markdown("""
    <div class="page-header">
      <div>⚡</div>
      <div>
        <h1>SLA · Primera Respuesta</h1>
        <p>Cumplimiento del tiempo de primera respuesta por tipo, prioridad y empresa</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles."); return

    total = len(df)
    cumplido = df["sla_primera_respuesta_cumplido"].sum()
    incumplido = total - cumplido
    pct_cum = (cumplido / total * 100) if total > 0 else 0
    pct_inc = 100 - pct_cum

    # ── KPIs ROW ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        fig_d = donut_kpi(pct_cum, "SLA 1ra Rpta", CHART_THEME["green"] if pct_cum >= 85 else CHART_THEME["red"])
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"<div class='donut-label'>% SLA Cumplido</div>", unsafe_allow_html=True)

    with c2:
        # Incidente donut
        df_inc = df[df["tipo"] == "Incidente"]
        pct_inc_tipo = (df_inc["sla_primera_respuesta_cumplido"].sum() / len(df_inc) * 100) if len(df_inc) > 0 else 0
        fig_d2 = donut_kpi(pct_inc_tipo, "", CHART_THEME["blue"])
        st.plotly_chart(fig_d2, use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='donut-label'>Incidentes</div>", unsafe_allow_html=True)

    with c3:
        df_req = df[df["tipo"] == "Requerimiento"]
        pct_req = (df_req["sla_primera_respuesta_cumplido"].sum() / len(df_req) * 100) if len(df_req) > 0 else 0
        fig_d3 = donut_kpi(pct_req, "", CHART_THEME["purple"])
        st.plotly_chart(fig_d3, use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='donut-label'>Requerimientos</div>", unsafe_allow_html=True)

    with c4:
        df_con = df[df["tipo"] == "Consulta"]
        pct_con = (df_con["sla_primera_respuesta_cumplido"].sum() / len(df_con) * 100) if len(df_con) > 0 else 0
        fig_d4 = donut_kpi(pct_con, "", CHART_THEME["cyan"])
        st.plotly_chart(fig_d4, use_container_width=True, config={"displayModeBar": False})
        st.markdown("<div class='donut-label'>Consultas</div>", unsafe_allow_html=True)

    with c5:
        st.markdown(kpi_card("Incumplidos", f"{incumplido:,}", "red",
            f"{pct_inc:.1f}% del total", icon="❌"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── GRÁFICOS ──
    col_a, col_b = st.columns(2)

    with col_a:
        df_tipo_sla = df.groupby("tipo").agg(
            total=("id", "count"),
            cumplido=("sla_primera_respuesta_cumplido", "sum")
        ).reset_index()
        df_tipo_sla["incumplido"] = df_tipo_sla["total"] - df_tipo_sla["cumplido"]
        df_tipo_sla["pct"] = (df_tipo_sla["cumplido"] / df_tipo_sla["total"] * 100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_tipo_sla["tipo"], y=df_tipo_sla["total"],
            name="Total", marker_color=CHART_THEME["blue"]))
        fig.add_trace(go.Bar(x=df_tipo_sla["tipo"], y=df_tipo_sla["cumplido"],
            name="1ra Rpta OK", marker_color=CHART_THEME["green"]))
        fig.add_trace(go.Scatter(x=df_tipo_sla["tipo"], y=df_tipo_sla["pct"],
            name="% Cumplido", yaxis="y2",
            mode="markers+lines", marker=dict(color=CHART_THEME["yellow"], size=10),
            line=dict(color=CHART_THEME["yellow"], width=2)))
        fig.update_layout(**chart_layout("SLA 1ra Respuesta por tipo", height=300),
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                        gridcolor="transparent", color=CHART_THEME["text"]),
            barmode="group")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        df_pri_sla = df.groupby("prioridad").agg(
            total=("id", "count"),
            cumplido=("sla_primera_respuesta_cumplido", "sum")
        ).reset_index()
        df_pri_sla["pct"] = (df_pri_sla["cumplido"] / df_pri_sla["total"] * 100).round(1)
        df_pri_sla["color"] = df_pri_sla["prioridad"].map(PRIORITY_COLORS).fillna("#64748b")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_pri_sla["prioridad"], y=df_pri_sla["total"],
            name="Total", marker_color=CHART_THEME["blue"]))
        fig2.add_trace(go.Bar(x=df_pri_sla["prioridad"], y=df_pri_sla["cumplido"],
            name="Cumplido", marker_color=CHART_THEME["green"]))
        fig2.add_trace(go.Scatter(x=df_pri_sla["prioridad"], y=df_pri_sla["pct"],
            name="% Cumplido", yaxis="y2",
            mode="markers+lines", marker=dict(color=CHART_THEME["yellow"], size=10),
            line=dict(color=CHART_THEME["yellow"], width=2)))
        fig2.update_layout(**chart_layout("SLA 1ra Respuesta por prioridad", height=300),
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                        gridcolor="transparent", color=CHART_THEME["text"]),
            barmode="group")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── TENDENCIA MENSUAL ──
    df_trend = df.groupby("mes_nombre").agg(
        total=("id", "count"),
        cumplido=("sla_primera_respuesta_cumplido", "sum")
    ).reset_index()
    df_trend["pct"] = (df_trend["cumplido"] / df_trend["total"] * 100).round(1)
    df_trend["sort_key"] = pd.to_datetime(df_trend["mes_nombre"], format="%b %Y", errors="coerce")
    df_trend = df_trend.sort_values("sort_key")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_trend["mes_nombre"], y=df_trend["pct"],
        name="% SLA Cumplido", mode="lines+markers",
        line=dict(color=CHART_THEME["green"], width=2.5),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.1)"))
    fig_line.add_hline(y=85, line=dict(color=CHART_THEME["red"], width=1.5, dash="dash"),
                       annotation_text="Meta 85%", annotation_font_color=CHART_THEME["red"])
    fig_line.update_layout(**chart_layout("📈 Tendencia SLA 1ra Respuesta mensual", height=260))
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    # ── TABLA EMPRESA x TIPO ──
    st.markdown("<div class='section-title'>Cumplimiento SLA por Empresa y Tipo</div>", unsafe_allow_html=True)
    df_pivot = df.groupby(["empresa", "tipo"]).agg(
        total=("id", "count"),
        cumplido=("sla_primera_respuesta_cumplido", "sum")
    ).reset_index()
    df_pivot["pct"] = (df_pivot["cumplido"] / df_pivot["total"] * 100).round(1).astype(str) + "%"
    pivot_tbl = df_pivot.pivot_table(index="empresa", columns="tipo",
                                     values=["total", "pct"], aggfunc="first")
    st.dataframe(pivot_tbl, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE: SLA RESOLUCIÓN
# ─────────────────────────────────────────────
def page_sla_resolucion(df):
    st.markdown("""
    <div class="page-header">
      <div>✅</div>
      <div>
        <h1>SLA · Resolución</h1>
        <p>Cumplimiento del tiempo de resolución final por prioridad, tipo y empresa</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles."); return

    df_c = df[df["is_closed"]].copy()
    total_c = len(df_c)
    cumplido = df_c["sla_resolucion_cumplido"].sum()
    pct_cum = (cumplido / total_c * 100) if total_c > 0 else 0
    tiempo_prom = df_c["tiempo_resolucion_hrs"].mean()

    # SLA por prioridad
    sla_crit = df_c[df_c["prioridad"] == "Critica"]["sla_resolucion_cumplido"].mean() * 100 if len(df_c[df_c["prioridad"] == "Critica"]) > 0 else 0
    sla_alta = df_c[df_c["prioridad"] == "Alta"]["sla_resolucion_cumplido"].mean() * 100 if len(df_c[df_c["prioridad"] == "Alta"]) > 0 else 0
    sla_med  = df_c[df_c["prioridad"] == "Media"]["sla_resolucion_cumplido"].mean() * 100 if len(df_c[df_c["prioridad"] == "Media"]) > 0 else 0

    # ── DONUTS ──
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    configs = [
        (c1, pct_cum, "SLA Global", CHART_THEME["green"] if pct_cum >= 85 else CHART_THEME["red"]),
        (c2, sla_crit, "Crítica", CHART_THEME["red"]),
        (c3, sla_alta, "Alta", CHART_THEME["orange"]),
        (c4, sla_med,  "Media", CHART_THEME["yellow"]),
    ]
    for col, val, lbl, clr in configs:
        with col:
            fig_d = donut_kpi(val, lbl, clr)
            st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
            st.markdown(f"<div class='donut-label'>{lbl}</div>", unsafe_allow_html=True)

    with c5:
        st.markdown(kpi_card("Incumplido", f"{100-pct_cum:.0f}%", "red",
            f"{total_c - cumplido:,} tickets", icon="❌"), unsafe_allow_html=True)
    with c6:
        t_str = f"{tiempo_prom:.1f}h" if not np.isnan(tiempo_prom) else "N/A"
        st.markdown(kpi_card("Tiempo Prom.", t_str, "blue", "resolución", icon="⏱️"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── GRÁFICOS ──
    col_a, col_b = st.columns(2)

    with col_a:
        df_tipo_sla = df_c.groupby("tipo").agg(
            total=("id", "count"),
            cumplido=("sla_resolucion_cumplido", "sum")
        ).reset_index()
        df_tipo_sla["pct"] = (df_tipo_sla["cumplido"] / df_tipo_sla["total"] * 100).round(1)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_tipo_sla["tipo"], y=df_tipo_sla["total"],
            name="Total Cerrados", marker_color=CHART_THEME["blue"]))
        fig.add_trace(go.Bar(x=df_tipo_sla["tipo"], y=df_tipo_sla["cumplido"],
            name="SLA OK", marker_color=CHART_THEME["green"]))
        fig.add_trace(go.Scatter(x=df_tipo_sla["tipo"], y=df_tipo_sla["pct"],
            name="%", yaxis="y2", mode="markers+lines",
            marker=dict(color=CHART_THEME["yellow"], size=10),
            line=dict(color=CHART_THEME["yellow"], width=2)))
        fig.update_layout(**chart_layout("Resolución SLA por tipo", height=300),
            yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                        gridcolor="transparent", color=CHART_THEME["text"]),
            barmode="group")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        # Tiempo resolución por prioridad
        df_time = df_c.groupby("prioridad")["tiempo_resolucion_hrs"].mean().reset_index()
        df_time["color"] = df_time["prioridad"].map(PRIORITY_COLORS).fillna("#64748b")
        fig2 = go.Figure(go.Bar(x=df_time["prioridad"], y=df_time["tiempo_resolucion_hrs"],
            marker_color=df_time["color"].tolist()))
        fig2.update_layout(**chart_layout("⏱️ Tiempo Prom. Resolución (hrs) por prioridad", height=300))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── TENDENCIA ──
    df_trend = df_c.groupby("mes_nombre").agg(
        total=("id", "count"),
        cumplido=("sla_resolucion_cumplido", "sum")
    ).reset_index()
    df_trend["pct"] = (df_trend["cumplido"] / df_trend["total"] * 100).round(1)
    df_trend["sort_key"] = pd.to_datetime(df_trend["mes_nombre"], format="%b %Y", errors="coerce")
    df_trend = df_trend.sort_values("sort_key")

    fig_line = go.Figure()
    fig_line.add_trace(go.Bar(x=df_trend["mes_nombre"], y=df_trend["total"],
        name="Total Cerrados", marker_color=CHART_THEME["blue"], opacity=0.6))
    fig_line.add_trace(go.Scatter(x=df_trend["mes_nombre"], y=df_trend["pct"],
        name="% SLA Cumplido", yaxis="y2", mode="lines+markers",
        line=dict(color=CHART_THEME["green"], width=2.5),
        marker=dict(size=7)))
    fig_line.add_hline(y=85, yref="y2", line=dict(color=CHART_THEME["red"], width=1.5, dash="dash"),
                       annotation_text="Meta 85%", annotation_font_color=CHART_THEME["red"])
    fig_line.update_layout(**chart_layout("📈 Tendencia SLA Resolución mensual", height=280),
        yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                    gridcolor="transparent", color=CHART_THEME["text"]))
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    # ── PIVOT EMPRESA ──
    st.markdown("<div class='section-title'>SLA Resolución por empresa y prioridad</div>", unsafe_allow_html=True)
    df_piv = df_c.groupby(["empresa", "prioridad"]).agg(
        cumplimiento=("sla_resolucion_cumplido", lambda x: f"{x.mean()*100:.0f}%"),
        total=("id", "count")
    ).reset_index()
    piv = df_piv.pivot_table(index="empresa", columns="prioridad",
                             values=["cumplimiento", "total"], aggfunc="first")
    st.dataframe(piv, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE: GRUPO RESOLUTOR
# ─────────────────────────────────────────────
def page_grupos(df):
    st.markdown("""
    <div class="page-header">
      <div>👥</div>
      <div>
        <h1>Grupo Resolutor</h1>
        <p>Desempeño individual de técnicos y grupos de soporte</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles."); return

    tab1, tab2 = st.tabs(["📊 Por Grupo", "👤 Por Técnico"])

    with tab1:
        df_g = df.groupby("grupo").agg(
            total=("id", "count"),
            cerrados=("is_closed", "sum"),
            sla_ok=("sla_resolucion_cumplido", "sum"),
            pendientes=("is_closed", lambda x: (~x).sum()),
            tiempo_prom=("tiempo_resolucion_hrs", "mean"),
            mismo_dia=("cerrado_mismo_dia", "sum")
        ).reset_index()
        df_g["pct_sla"] = (df_g["sla_ok"] / df_g["cerrados"] * 100).round(1)
        df_g["pct_cerrado"] = (df_g["cerrados"] / df_g["total"] * 100).round(1)

        # KPIs por grupo
        for _, row in df_g.iterrows():
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.markdown(f"**{row['grupo']}**")
            with c2: st.markdown(kpi_card("Tickets", str(int(row["total"])), "blue"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("Cerrados", f"{row['pct_cerrado']}%", "green"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card("SLA%", f"{row['pct_sla']}%", "purple" if row['pct_sla'] >= 85 else "red"), unsafe_allow_html=True)
            with c5: st.markdown(kpi_card("T.Prom", f"{row['tiempo_prom']:.1f}h", "cyan"), unsafe_allow_html=True)
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Gráfico comparativo
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=df_g["grupo"], y=df_g["total"],
                name="Total", marker_color=CHART_THEME["blue"]))
            fig1.add_trace(go.Bar(x=df_g["grupo"], y=df_g["cerrados"],
                name="Cerrados+Resueltos", marker_color=CHART_THEME["green"]))
            fig1.add_trace(go.Scatter(x=df_g["grupo"], y=df_g["pct_sla"],
                name="% SLA", yaxis="y2", mode="lines+markers",
                line=dict(color=CHART_THEME["yellow"], width=2)))
            fig1.update_layout(**chart_layout("Tickets por grupo vs SLA", height=300),
                yaxis2=dict(overlaying="y", side="right", ticksuffix="%",
                            gridcolor="transparent", color=CHART_THEME["text"]),
                barmode="group")
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            fig2 = go.Figure(go.Bar(
                x=df_g["grupo"], y=df_g["tiempo_prom"],
                marker_color=CHART_THEME["purple"],
                text=df_g["tiempo_prom"].round(1).astype(str) + "h",
                textposition="outside"
            ))
            fig2.update_layout(**chart_layout("⏱️ Tiempo promedio resolución por grupo", height=300))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with tab2:
        df_t = df.groupby(["tecnico", "grupo"]).agg(
            total=("id", "count"),
            cerrados=("is_closed", "sum"),
            sla_ok=("sla_resolucion_cumplido", "sum"),
            tiempo_prom=("tiempo_resolucion_hrs", "mean"),
            mismo_dia=("cerrado_mismo_dia", "sum")
        ).reset_index()
        df_t["pct_sla"] = (df_t["sla_ok"] / df_t["cerrados"].replace(0, 1) * 100).round(1)
        df_t["pct_mismo_dia"] = (df_t["mismo_dia"] / df_t["cerrados"].replace(0, 1) * 100).round(1)
        df_t = df_t.sort_values("total", ascending=False)

        fig_tec = go.Figure()
        fig_tec.add_trace(go.Bar(y=df_t["tecnico"], x=df_t["total"],
            name="Total", orientation="h", marker_color=CHART_THEME["blue"]))
        fig_tec.add_trace(go.Bar(y=df_t["tecnico"], x=df_t["cerrados"],
            name="Cerrados", orientation="h", marker_color=CHART_THEME["green"]))
        fig_tec.update_layout(**chart_layout("🏆 Desempeño por técnico", height=350),
            barmode="overlay")
        st.plotly_chart(fig_tec, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div class='section-title'>Tabla de Desempeño Individual</div>", unsafe_allow_html=True)
        df_t_disp = df_t[["tecnico", "grupo", "total", "cerrados", "pct_sla", "tiempo_prom", "pct_mismo_dia"]].copy()
        df_t_disp.columns = ["Técnico", "Grupo", "Total", "Cerrados", "SLA%", "T.Prom(h)", "%Mismo Día"]
        df_t_disp["T.Prom(h)"] = df_t_disp["T.Prom(h)"].round(1)
        st.dataframe(df_t_disp, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: ENCUESTAS CSAT
# ─────────────────────────────────────────────
def page_encuestas(df):
    st.markdown("""
    <div class="page-header">
      <div>⭐</div>
      <div>
        <h1>Encuestas de Satisfacción (CSAT)</h1>
        <p>Calificación de usuarios por atención, rapidez, solución y experiencia global</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles."); return

    df_s = df[df["csat_global"].notna()].copy() if "csat_global" in df.columns else pd.DataFrame()

    if len(df_s) == 0:
        st.info("No hay datos de encuestas en el período seleccionado.")
        return

    csat_global   = df_s["csat_global"].mean()
    csat_atencion = df_s["csat_atencion"].mean()
    csat_rapidez  = df_s["csat_rapidez"].mean()
    csat_solucion = df_s["csat_solucion"].mean()

    def star_str(v): return "⭐" * round(v) if not np.isnan(v) else "N/A"
    def color_csat(v): return "green" if v >= 4.0 else "yellow" if v >= 3.0 else "red"

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("CSAT Global",    f"{csat_global:.2f}", color_csat(csat_global),    star_str(csat_global),    icon="🌐"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Atención",        f"{csat_atencion:.2f}", color_csat(csat_atencion), star_str(csat_atencion), icon="🤝"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Rapidez",         f"{csat_rapidez:.2f}", color_csat(csat_rapidez),  star_str(csat_rapidez),  icon="⚡"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Solución",        f"{csat_solucion:.2f}", color_csat(csat_solucion), star_str(csat_solucion), icon="✅"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        # Radar CSAT
        categories = ["Atención", "Rapidez", "Solución", "Global"]
        values = [csat_atencion, csat_rapidez, csat_solucion, csat_global]
        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(59,130,246,0.15)",
            line=dict(color=CHART_THEME["blue"], width=2),
            marker=dict(color=CHART_THEME["blue"], size=8)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5],
                                gridcolor=CHART_THEME["grid"], color=CHART_THEME["text"]),
                angularaxis=dict(color=CHART_THEME["text"]),
                bgcolor=CHART_THEME["paper"],
            ),
            paper_bgcolor=CHART_THEME["paper"],
            plot_bgcolor=CHART_THEME["paper"],
            font=dict(color=CHART_THEME["text"], family="Inter"),
            showlegend=False, height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            title=dict(text="⭐ Radar CSAT", font=dict(color="#e2e8f0", size=13))
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        # CSAT por técnico
        df_tec_csat = df_s.groupby("tecnico").agg(
            global_avg=("csat_global", "mean"),
            respuestas=("csat_global", "count")
        ).reset_index().sort_values("global_avg", ascending=True)
        fig_tec = go.Figure(go.Bar(
            y=df_tec_csat["tecnico"], x=df_tec_csat["global_avg"],
            orientation="h",
            marker=dict(
                color=df_tec_csat["global_avg"],
                colorscale=[[0, CHART_THEME["red"]], [0.5, CHART_THEME["yellow"]], [1, CHART_THEME["green"]]],
                cmin=1, cmax=5
            ),
            text=df_tec_csat["global_avg"].round(2),
            textposition="outside"
        ))
        fig_tec.update_layout(**chart_layout("CSAT Global por Técnico", height=300))
        fig_tec.update_xaxes(range=[0, 5.5])
        st.plotly_chart(fig_tec, use_container_width=True, config={"displayModeBar": False})

    # Distribución de calificaciones
    col_c, col_d = st.columns(2)
    with col_c:
        df_s["stars"] = df_s["csat_global"].round().astype(int).clip(1, 5)
        star_counts = df_s["stars"].value_counts().sort_index()
        fig_dist = go.Figure(go.Bar(
            x=[f"{'⭐'*i}" for i in star_counts.index],
            y=star_counts.values,
            marker_color=[CHART_THEME["red"], CHART_THEME["orange"], CHART_THEME["yellow"],
                          CHART_THEME["cyan"], CHART_THEME["green"]][:len(star_counts)]
        ))
        fig_dist.update_layout(**chart_layout("Distribución de calificaciones", height=260, showlegend=False))
        st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        # CSAT por mes
        df_csat_mes = df_s.groupby("mes_nombre").agg(
            global_avg=("csat_global", "mean")
        ).reset_index()
        df_csat_mes["sort_key"] = pd.to_datetime(df_csat_mes["mes_nombre"], format="%b %Y", errors="coerce")
        df_csat_mes = df_csat_mes.sort_values("sort_key")
        fig_mes = go.Figure(go.Scatter(
            x=df_csat_mes["mes_nombre"], y=df_csat_mes["global_avg"],
            mode="lines+markers",
            line=dict(color=CHART_THEME["yellow"], width=2.5),
            marker=dict(size=8, color=CHART_THEME["yellow"]),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.1)"
        ))
        fig_mes.add_hline(y=4.0, line=dict(color=CHART_THEME["green"], width=1.5, dash="dash"),
                          annotation_text="Meta 4.0", annotation_font_color=CHART_THEME["green"])
        fig_mes.update_layout(**chart_layout("Tendencia CSAT mensual", height=260))
        fig_mes.update_yaxes(range=[0, 5.5])
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})

    # Tabla detalle
    st.markdown("<div class='section-title'>Detalle de Encuestas Recientes</div>", unsafe_allow_html=True)
    df_det = df_s[["fecha_creacion", "display_id", "asunto", "empresa", "subcategoria",
                   "tecnico", "grupo", "csat_atencion", "csat_rapidez", "csat_solucion", "csat_global"]].head(30).copy()
    df_det["fecha_creacion"] = df_det["fecha_creacion"].dt.strftime("%d/%m/%Y")
    df_det.columns = ["Fecha", "ID", "Asunto", "Empresa", "Subcategoría",
                      "Técnico", "Grupo", "Atención", "Rapidez", "Solución", "Global"]
    for col in ["Atención", "Rapidez", "Solución", "Global"]:
        df_det[col] = df_det[col].round(1)
    st.dataframe(df_det, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: ALERTAS & PENDIENTES
# ─────────────────────────────────────────────
def page_alertas(df):
    st.markdown("""
    <div class="page-header">
      <div>🚨</div>
      <div>
        <h1>Alertas & Tickets Pendientes</h1>
        <p>Vista operativa en tiempo real: tickets críticos, vencidos y en riesgo de SLA</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if df is None or len(df) == 0:
        st.warning("Sin datos disponibles."); return

    now = datetime.now()
    df_open = df[~df["is_closed"]].copy()

    # Tickets críticos abiertos
    df_crit = df_open[df_open["prioridad"] == "Critica"]
    df_alta = df_open[df_open["prioridad"] == "Alta"]
    df_old = df_open[df_open["fecha_creacion"] < pd.Timestamp(now - timedelta(hours=48))]

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Abiertos Totales", str(len(df_open)), "yellow", "sin resolver", icon="⏳"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Críticos Abiertos", str(len(df_crit)), "red", "prioridad crítica", icon="🔴"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Alta Prioridad", str(len(df_alta)), "yellow", "prioridad alta", icon="🟠"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card(">48h sin resolver", str(len(df_old)), "red", "antiguedad alta", icon="⚠️"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Alertas visuales
    if len(df_crit) > 0:
        st.markdown(f'<div class="alert-critical">🔴 <strong>{len(df_crit)} ticket(s) crítico(s)</strong> abiertos requieren atención inmediata</div>', unsafe_allow_html=True)
    if len(df_old) > 0:
        st.markdown(f'<div class="alert-warning">⚠️ <strong>{len(df_old)} ticket(s)</strong> llevan más de 48 horas abiertos</div>', unsafe_allow_html=True)

    # Gráficos
    col_a, col_b = st.columns(2)
    with col_a:
        df_by_pri = df_open["prioridad"].value_counts().reset_index()
        df_by_pri.columns = ["prioridad", "count"]
        colors = [PRIORITY_COLORS.get(p, "#64748b") for p in df_by_pri["prioridad"]]
        fig1 = go.Figure(go.Bar(x=df_by_pri["prioridad"], y=df_by_pri["count"],
            marker_color=colors, text=df_by_pri["count"], textposition="outside"))
        fig1.update_layout(**chart_layout("Abiertos por prioridad", height=260, showlegend=False))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        df_by_grupo = df_open.groupby("grupo").size().reset_index(name="count").sort_values("count", ascending=True)
        fig2 = go.Figure(go.Bar(
            y=df_by_grupo["grupo"], x=df_by_grupo["count"],
            orientation="h", marker_color=CHART_THEME["orange"],
            text=df_by_grupo["count"], textposition="outside"
        ))
        fig2.update_layout(**chart_layout("Abiertos por grupo", height=260, showlegend=False))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Tabla de tickets críticos
    st.markdown("<div class='section-title'>🔴 Tickets Críticos Abiertos</div>", unsafe_allow_html=True)
    if len(df_crit) > 0:
        df_crit_disp = df_crit[["display_id", "fecha_creacion", "asunto", "solicitante",
                                  "empresa", "tecnico", "grupo", "estado"]].copy()
        df_crit_disp["fecha_creacion"] = df_crit_disp["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
        df_crit_disp["Antigüedad"] = (df_crit["fecha_creacion"].apply(
            lambda x: f"{(now - x.to_pydatetime()).total_seconds() / 3600:.0f}h" if pd.notna(x) else "N/A"
        )).values
        df_crit_disp.columns = ["ID", "Fecha", "Asunto", "Solicitante", "Empresa", "Técnico", "Grupo", "Estado", "Antigüedad"]
        st.dataframe(df_crit_disp, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No hay tickets críticos abiertos actualmente")

    # Tabla de tickets >48h
    st.markdown("<div class='section-title'>⚠️ Tickets con más de 48 horas abiertos</div>", unsafe_allow_html=True)
    if len(df_old) > 0:
        df_old_disp = df_old[["display_id", "fecha_creacion", "asunto", "solicitante",
                               "empresa", "prioridad", "tecnico", "grupo", "estado"]].copy()
        df_old_disp["Antigüedad (h)"] = df_old["fecha_creacion"].apply(
            lambda x: round((now - x.to_pydatetime()).total_seconds() / 3600, 0) if pd.notna(x) else 0
        ).values
        df_old_disp["fecha_creacion"] = df_old_disp["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
        df_old_disp.columns = ["ID", "Fecha", "Asunto", "Solicitante", "Empresa", "Prioridad", "Técnico", "Grupo", "Estado", "Antigüedad (h)"]
        df_old_disp = df_old_disp.sort_values("Antigüedad (h)", ascending=False)
        st.dataframe(df_old_disp, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# PAGE: CONFIGURACIÓN
# ─────────────────────────────────────────────
def page_config():
    st.markdown("""
    <div class="page-header">
      <div>⚙️</div>
      <div>
        <h1>Configuración API · ServiceDesk Plus</h1>
        <p>Conecta el dashboard con tu instancia de SDP para datos en tiempo real</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔌 Conexión a ServiceDesk Plus")

    with st.form("config_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            url = st.text_input(
                "URL de tu instancia SDP",
                value=st.session_state.sdp_url,
                placeholder="https://tuempresa.sdpondemand.com o http://servidor:8080",
                help="Incluye http:// o https://"
            )
        with col2:
            key = st.text_input(
                "API Key (TECHNICIAN_KEY)",
                value=st.session_state.sdp_key,
                type="password",
                placeholder="Tu TECHNICIAN_KEY de SDP"
            )

        col_a, col_b, _ = st.columns([1, 1, 2])
        with col_a:
            submitted = st.form_submit_button("💾 Guardar y conectar", type="primary", use_container_width=True)
        with col_b:
            test_btn = st.form_submit_button("🧪 Probar conexión", use_container_width=True)

        if submitted:
            st.session_state.sdp_url = url
            st.session_state.sdp_key = key
            st.session_state.use_demo = False
            st.success("✅ Configuración guardada. Desactiva el modo demo en el sidebar para usar datos reales.")

        if test_btn and url and key:
            with st.spinner("Probando conexión..."):
                client = SDPClient(url, key)
                ok, msg = client.test_connection()
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

    st.markdown("---")
    st.markdown("""
    ### 📚 Guía de configuración

    **1. Obtener el TECHNICIAN_KEY:**
    - Inicia sesión en SDP como administrador
    - Ve a **Admin → Technicians**
    - Selecciona tu usuario y haz clic en **API Key**

    **2. Endpoints utilizados:**
    """)

    endpoints_data = {
        "Endpoint": ["/api/v3/requests", "/api/v3/requests/{id}", "/api/v3/technicians", "/api/v3/groups"],
        "Método": ["GET", "GET", "GET", "GET"],
        "Uso en el dashboard": [
            "Listado paginado de tickets con filtros de fecha",
            "Detalle individual de un ticket (SLA, campos UDF)",
            "Lista de técnicos para filtros",
            "Lista de grupos para filtros"
        ]
    }
    st.dataframe(pd.DataFrame(endpoints_data), use_container_width=True, hide_index=True)

    st.markdown("""
    **3. Campos personalizados (UDF) requeridos:**
    - `udf_sline_1` → Empresa
    - `udf_sline_2` → Tipo de Empresa
    - `udf_sline_3` → Región
    - `udf_sline_4` → ERP
    - `udf_sline_5` → Corporativo
    - `udf_sline_6` → Informativo

    > Si tus UDF usan nombres diferentes, edita el método `_parse_requests` en `app.py`

    **4. Deploy en Streamlit Cloud:**
    - Sube `app.py` y `requirements.txt` a GitHub
    - Usa `st.secrets` para proteger la API key:
    ```toml
    # .streamlit/secrets.toml
    SDP_URL = "https://tuinstancia.sdpondemand.com"
    SDP_KEY = "tu_technician_key"
    ```
    """)

    st.markdown("---")
    st.markdown("### 📦 requirements.txt")
    st.code("""streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
requests>=2.31.0""", language="text")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    date_from, date_to, filters = render_sidebar()

    # Load and filter data
    if st.session_state.page != "config":
        raw_df = get_data(date_from, date_to)
        df = apply_filters(raw_df, date_from, date_to, filters)
    else:
        df = None

    # Route to page
    page = st.session_state.page

    if page == "general":
        page_general(df)
    elif page == "sla_fr":
        page_sla_fr(df)
    elif page == "sla_res":
        page_sla_resolucion(df)
    elif page == "grupos":
        page_grupos(df)
    elif page == "encuestas":
        page_encuestas(df)
    elif page == "alertas":
        page_alertas(df)
    elif page == "config":
        page_config()

if __name__ == "__main__":
    main()
