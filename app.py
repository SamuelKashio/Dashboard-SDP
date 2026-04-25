import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta, date
import time
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
# CARGA DE SECRETS (Streamlit Cloud o local)
# ─────────────────────────────────────────────
def load_secrets():
    """Carga tokens desde st.secrets (Streamlit Cloud o .streamlit/secrets.toml local)."""
    try:
        return {
            "access_token":  st.secrets["zoho"]["access_token"],
            "refresh_token": st.secrets["zoho"]["refresh_token"],
            "api_domain":    st.secrets["zoho"]["api_domain"],
            "sdp_portal":    st.secrets["zoho"]["sdp_portal"],
            "client_id":     st.secrets["zoho"].get("client_id", ""),
            "client_secret": st.secrets["zoho"].get("client_secret", ""),
        }
    except Exception:
        return None

# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }

  .main, .block-container { background: #0f172a; padding: 1rem 2rem 2rem; }

  .kpi-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155; border-radius: 12px;
    padding: 1.2rem 1.4rem; position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }
  .kpi-card::before { content:''; position:absolute; top:0; left:0; width:4px; height:100%; border-radius:12px 0 0 12px; }
  .kpi-blue::before   { background:#3b82f6; }
  .kpi-green::before  { background:#22c55e; }
  .kpi-yellow::before { background:#f59e0b; }
  .kpi-red::before    { background:#ef4444; }
  .kpi-purple::before { background:#a855f7; }
  .kpi-cyan::before   { background:#06b6d4; }
  .kpi-orange::before { background:#f97316; }
  .kpi-label { font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; margin-bottom:0.3rem; }
  .kpi-value { font-size:1.9rem; font-weight:700; color:#f1f5f9; line-height:1; }
  .kpi-sub   { font-size:0.73rem; color:#64748b; margin-top:0.35rem; }
  .kpi-pos   { color:#22c55e; font-weight:600; }
  .kpi-neg   { color:#ef4444; font-weight:600; }

  .donut-label { font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:#64748b; text-align:center; margin-top:0.3rem; }

  .section-title {
    font-size:0.8rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.1em; color:#475569;
    border-bottom:1px solid #1e293b; padding-bottom:0.4rem; margin:1.5rem 0 0.8rem;
  }

  .page-header {
    background: linear-gradient(90deg,#1e3a5f 0%,#1e293b 100%);
    border:1px solid #2563eb44; border-radius:12px;
    padding:0.9rem 1.4rem; margin-bottom:1.2rem;
    display:flex; align-items:center; gap:1rem;
  }
  .page-header h1 { font-size:1.35rem; font-weight:700; color:#e2e8f0; margin:0; }
  .page-header p  { font-size:0.78rem; color:#64748b; margin:0; }

  .alert-critical { background:#450a0a; border:1px solid #ef4444; border-radius:8px; padding:0.7rem 1rem; color:#fca5a5; font-size:0.84rem; margin-bottom:0.5rem; }
  .alert-warning  { background:#1c1400; border:1px solid #f59e0b; border-radius:8px; padding:0.7rem 1rem; color:#fcd34d; font-size:0.84rem; margin-bottom:0.5rem; }
  .alert-info     { background:#0c1a2e; border:1px solid #3b82f6; border-radius:8px; padding:0.7rem 1rem; color:#93c5fd; font-size:0.84rem; margin-bottom:0.5rem; }

  .token-badge { display:inline-block; padding:0.2rem 0.6rem; border-radius:20px; font-size:0.7rem; font-weight:600; }
  .token-ok    { background:#14532d; color:#86efac; border:1px solid #22c55e44; }
  .token-exp   { background:#450a0a; color:#fca5a5; border:1px solid #ef444444; }

  .stTabs [data-baseweb="tab-list"] { background:#1e293b; border-radius:8px; gap:4px; padding:4px; }
  .stTabs [data-baseweb="tab"]       { background:transparent; color:#64748b; border-radius:6px; font-weight:500; }
  .stTabs [aria-selected="true"]     { background:#3b82f6 !important; color:white !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
CHART_T = {
    "bg":"#0f172a","paper":"#1e293b","grid":"#334155","text":"#94a3b8",
    "blue":"#3b82f6","green":"#22c55e","yellow":"#f59e0b","red":"#ef4444",
    "purple":"#a855f7","cyan":"#06b6d4","orange":"#f97316",
}
PRIORITY_COLORS = {"Critica":"#ef4444","Alta":"#f97316","Media":"#f59e0b","Baja":"#22c55e"}

def clo(title="", height=300, showlegend=True):
    return dict(
        title=dict(text=title, font=dict(color="#e2e8f0", size=13), x=0),
        plot_bgcolor=CHART_T["paper"], paper_bgcolor=CHART_T["paper"],
        font=dict(color=CHART_T["text"], family="Inter"),
        height=height, showlegend=showlegend,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
        margin=dict(l=10, r=10, t=40 if title else 15, b=10),
        xaxis=dict(gridcolor=CHART_T["grid"], linecolor=CHART_T["grid"], zerolinecolor=CHART_T["grid"]),
        yaxis=dict(gridcolor=CHART_T["grid"], linecolor=CHART_T["grid"], zerolinecolor=CHART_T["grid"]),
    )

# ─────────────────────────────────────────────
# ZOHO OAUTH CLIENT — ServiceDesk Plus On-Demand
# ─────────────────────────────────────────────
class ZohoSDPClient:
    """
    Cliente OAuth 2.0 para ManageEngine ServiceDesk Plus On-Demand (Zoho).
    Endpoints:  {sdp_portal}/api/v3/requests
    Auth header: Authorization: Zoho-oauthtoken {access_token}
    Refresh:     POST https://accounts.zoho.com/oauth/v2/token
    """

    ACCOUNTS_URL = "https://accounts.zoho.com/oauth/v2/token"
    # Región: ajusta si tu cuenta es .eu / .in / .com.au
    ACCOUNTS_URL_MAP = {
        "https://www.zohoapis.com":    "https://accounts.zoho.com/oauth/v2/token",
        "https://www.zohoapis.eu":     "https://accounts.zoho.eu/oauth/v2/token",
        "https://www.zohoapis.in":     "https://accounts.zoho.in/oauth/v2/token",
        "https://www.zohoapis.com.au": "https://accounts.zoho.com.au/oauth/v2/token",
        "https://www.zohoapis.jp":     "https://accounts.zoho.jp/oauth/v2/token",
    }

    def __init__(self, sdp_portal: str, access_token: str, refresh_token: str,
                 api_domain: str = "https://www.zohoapis.com",
                 client_id: str = "", client_secret: str = "",
                 app_name: str = "itdesk"):
        self.portal        = sdp_portal.rstrip("/")
        self.app_name      = app_name   # e.g. "itdesk"
        self.access_token  = access_token
        self.refresh_token = refresh_token
        self.api_domain    = api_domain
        self.client_id     = client_id
        self.client_secret = client_secret
        self.token_refreshed_at = datetime.now()
        self._accounts_url = self.ACCOUNTS_URL_MAP.get(api_domain, self.ACCOUNTS_URL)

    def _auth_header(self) -> dict:
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def refresh_access_token(self) -> tuple[bool, str]:
        """Renueva el access_token usando el refresh_token (requiere client_id + secret)."""
        if not self.client_id or not self.client_secret:
            return False, "Sin client_id/client_secret — renueva el token manualmente en Zoho Developer Console"
        try:
            r = requests.post(self._accounts_url, data={
                "grant_type":    "refresh_token",
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            }, timeout=15)
            data = r.json()
            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_refreshed_at = datetime.now()
                # Actualizar session state
                st.session_state.access_token = self.access_token
                return True, "Token renovado exitosamente"
            return False, data.get("error", "Error desconocido al renovar token")
        except Exception as e:
            return False, str(e)

    def _get(self, endpoint: str, params: dict = None) -> dict:
        # SDP on-premise with custom domain: /app/{app_name}/api/v3/
        url = f"{self.portal}/app/{self.app_name}/api/v3/{endpoint}"
        try:
            r = requests.get(url, headers=self._auth_header(), params=params, timeout=30)
            if r.status_code == 401:
                # Token expirado — intentar refresh
                ok, msg = self.refresh_access_token()
                if ok:
                    r = requests.get(url, headers=self._auth_header(), params=params, timeout=30)
                else:
                    return {"error": "token_expired", "message": f"Token expirado. {msg}"}
            if r.status_code == 403:
                return {"error": "forbidden", "message": "Sin permisos. Verifica el scope SDPOnDemand.requests.READ"}
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"error": "connection", "message": f"No se pudo conectar a {self.portal}"}
        except requests.exceptions.Timeout:
            return {"error": "timeout", "message": "SDP no respondió (timeout 30s)"}
        except Exception as e:
            return {"error": type(e).__name__, "message": str(e)}

    def test_connection(self) -> tuple[bool, str, dict]:
        data = self._get("requests", params={
            "input_data": json.dumps({"list_info": {"row_count": 1, "start_index": 1}})
        })
        if "error" in data:
            return False, data["message"], {}
        meta = data.get("response_status", {})
        total = data.get("list_info", {}).get("total_count", "?")
        return True, f"OK — {total} tickets encontrados", data

    def get_requests_page(self, start: int = 1, row_count: int = 100,
                          date_from=None, date_to=None, extra_filters=None) -> dict:
        list_info = {
            "start_index": start,
            "row_count": row_count,
            "sort_field": "created_time",
            "sort_order": "desc",
        }
        search = []
        if date_from:
            ts = int(datetime.combine(date_from, datetime.min.time()).timestamp() * 1000)
            search.append({"field": "created_time", "condition": "gt", "value": str(ts), "logical_operator": "AND"})
        if date_to:
            ts = int(datetime.combine(date_to, datetime.max.time()).timestamp() * 1000)
            search.append({"field": "created_time", "condition": "lt", "value": str(ts), "logical_operator": "AND"})
        if extra_filters:
            search.extend(extra_filters)
        if search:
            list_info["search_criteria"] = search
        return self._get("requests", params={"input_data": json.dumps({"list_info": list_info})})

    def get_all_requests(self, date_from=None, date_to=None, max_records=3000,
                         progress_cb=None) -> pd.DataFrame:
        all_reqs, start, batch = [], 1, 100
        while len(all_reqs) < max_records:
            data = self.get_requests_page(start, batch, date_from, date_to)
            if "error" in data:
                st.error(f"❌ Error API: {data['message']}")
                break
            batch_reqs = data.get("requests", [])
            if not batch_reqs:
                break
            all_reqs.extend(batch_reqs)
            total_available = data.get("list_info", {}).get("total_count", 0)
            if progress_cb:
                progress_cb(len(all_reqs), total_available or len(all_reqs))
            if len(batch_reqs) < batch:
                break
            start += batch
            time.sleep(0.12)   # rate-limit gentil

        return self._parse(all_reqs)

    def _parse(self, raw: list) -> pd.DataFrame:
        if not raw:
            return pd.DataFrame()
        rows = []
        for r in raw:
            def gn(o): return o.get("name", "") if isinstance(o, dict) else (o or "")
            def pts(o):
                if isinstance(o, dict) and "value" in o:
                    try: return pd.to_datetime(int(o["value"]), unit="ms")
                    except: pass
                return pd.NaT

            created   = pts(r.get("created_time", {}))
            resolved  = pts(r.get("resolved_time", {}))
            closed    = pts(r.get("closed_time", {}))
            due       = pts(r.get("due_by_time", {}))
            fr_due    = pts(r.get("first_response_due_by_time", {}))
            fr_actual = pts(r.get("first_response_time", {}))

            # SLA flags
            end = resolved if pd.notna(resolved) else closed
            sla_res = (pd.notna(end) and pd.notna(due) and end <= due)
            sla_fr  = (pd.notna(fr_actual) and pd.notna(fr_due) and fr_actual <= fr_due)

            res_hrs = (end - created).total_seconds() / 3600 if (pd.notna(end) and pd.notna(created)) else np.nan
            same_day = (pd.notna(created) and pd.notna(end) and created.date() == end.date())

            # UDF / campos adicionales
            udf = r.get("udf_fields", {}) or {}
            # SDP OnDemand puede devolver campos_adicionales como lista
            ca = {}
            for item in (r.get("additional_fields") or []):
                if isinstance(item, dict):
                    ca[item.get("label", "")] = item.get("value", "")

            def udf_get(*keys):
                for k in keys:
                    v = udf.get(k) or ca.get(k)
                    if v: return str(v)
                return ""

            status  = gn(r.get("status", {}))
            is_done = status.lower() in ["completada","resuelta","cerrada","completed","resolved","closed"]

            # CSAT (si viene en el objeto)
            survey  = r.get("survey", {}) or {}
            rating  = float(survey.get("rating", 0) or 0)

            rows.append({
                "id":            r.get("id", ""),
                "display_id":    r.get("display_id", r.get("id", "")),
                "asunto":        r.get("subject", ""),
                "estado":        status,
                "prioridad":     gn(r.get("priority", {})),
                "tipo":          gn(r.get("request_type", {})),
                "categoria":     gn(r.get("category", {})),
                "subcategoria":  gn(r.get("subcategory", {})),
                "grupo":         gn(r.get("group", {})),
                "tecnico":       gn(r.get("technician", {})),
                "solicitante":   gn(r.get("requester", {})),
                # Campos adicionales — ajusta los nombres a tu instancia
                "empresa":       udf_get("udf_sline_1","Empresa","empresa"),
                "tipo_empresa":  udf_get("udf_sline_2","Tipo de Empresa","tipo_empresa"),
                "region":        udf_get("udf_sline_3","Región","region"),
                "erp":           udf_get("udf_sline_4","ERP","erp"),
                "corporativo":   udf_get("udf_sline_5","Corporativo","corporativo"),
                "informativo":   udf_get("udf_sline_6","Informativo","informativo"),
                "fecha_creacion":  created,
                "fecha_resolucion": resolved,
                "fecha_cierre":    closed,
                "fecha_venc":      due,
                "sla_resolucion":  sla_res,
                "sla_fr":          sla_fr,
                "tiempo_hrs":      res_hrs,
                "mismo_dia":       same_day,
                "is_closed":       is_done,
                "csat_global":     rating if rating > 0 else np.nan,
            })

        df = pd.DataFrame(rows)
        df["fecha_creacion"] = pd.to_datetime(df["fecha_creacion"])
        df["anio"]      = df["fecha_creacion"].dt.year
        df["mes"]       = df["fecha_creacion"].dt.month
        df["mes_label"] = df["fecha_creacion"].dt.strftime("%b %Y")
        df["dia_sem"]   = df["fecha_creacion"].dt.day_name()
        return df

# ─────────────────────────────────────────────
# DEMO DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def demo_data(n=800) -> pd.DataFrame:
    np.random.seed(42)
    start = datetime.now() - timedelta(days=365)
    fechas = sorted([start + timedelta(days=np.random.randint(0,365)) for _ in range(n)])
    tipos = np.random.choice(["Incidente","Requerimiento","Consulta"], n, p=[.45,.35,.20])
    prios = np.random.choice(["Critica","Alta","Media","Baja"], n, p=[.10,.25,.40,.25])
    estados = np.random.choice(["Completada","Resuelta","En Progreso","Abierta","Pendiente"], n, p=[.45,.25,.15,.10,.05])
    grupos  = ["TI General","Infraestructura","Aplicaciones ERP","Soporte Usuario","Redes & Seguridad"]
    tecs_by_g = {
        "TI General":["Juan Pérez","María García"],
        "Infraestructura":["Carlos López","Ana Torres"],
        "Aplicaciones ERP":["Roberto Silva","Diana Ruiz"],
        "Soporte Usuario":["Luis Herrera","Carmen Flores"],
        "Redes & Seguridad":["Miguel Ángel","Patricia Ríos"],
    }
    empresas    = ["Alpha Corp","Beta SA","Gamma Group","Delta Ltd","Epsilon Inc","Zeta Solutions","Eta Corp","Theta SA"]
    tipo_emp    = np.random.choice(["Corporativa","PYME","Subsidiaria"], n, p=[.4,.35,.25])
    regiones    = np.random.choice(["Norte","Sur","Centro","Oriente","Occidente"], n)
    categorias  = np.random.choice(["Hardware","Software","Red","Accesos","ERP","Correo","Impresión"], n)
    grupo_arr   = np.random.choice(grupos, n)
    tec_arr     = [np.random.choice(tecs_by_g[g]) for g in grupo_arr]
    emp_arr     = np.random.choice(empresas, n)

    sla_r_p = {"Critica":.72,"Alta":.80,"Media":.88,"Baja":.93}
    sla_f_p = {"Critica":.78,"Alta":.85,"Media":.90,"Baja":.95}
    sla_res = [np.random.random() < sla_r_p[p] for p in prios]
    sla_fr  = [np.random.random() < sla_f_p[p] for p in prios]

    rt_map = {"Critica":(2,8),"Alta":(4,24),"Media":(8,48),"Baja":(24,96)}
    res_hrs = [np.random.uniform(*rt_map[p]) for p in prios]
    f_res = [fd+timedelta(hours=rh) if e in ["Completada","Resuelta"] else pd.NaT
             for fd,rh,e in zip(fechas,res_hrs,estados)]
    same = [pd.notna(fr) and fc.date()==fr.date() for fc,fr in zip(fechas,f_res)]
    is_c = [e in ["Completada","Resuelta"] for e in estados]

    csat_a = [np.random.uniform(3.5,5.0) if ic else np.nan for ic in is_c]
    csat_r = [np.random.uniform(3.0,5.0) if ic else np.nan for ic in is_c]
    csat_s = [np.random.uniform(3.2,5.0) if ic else np.nan for ic in is_c]
    csat_g = [(a+r+s)/3 if not np.isnan(a) else np.nan for a,r,s in zip(csat_a,csat_r,csat_s)]

    df = pd.DataFrame({
        "id":range(1,n+1), "display_id":[f"REQ-{1000+i}" for i in range(n)],
        "asunto":[f"Ticket #{i+1}" for i in range(n)],
        "estado":estados,"prioridad":prios,"tipo":tipos,
        "categoria":categorias,"subcategoria":np.random.choice(["Nivel 1","Nivel 2","Nivel 3"],n),
        "grupo":grupo_arr,"tecnico":tec_arr,"solicitante":[f"Usuario {i}" for i in range(n)],
        "empresa":emp_arr,"tipo_empresa":tipo_emp,"region":regiones,
        "erp":np.random.choice(["SAP","Oracle","Odoo","N/A"],n,p=[.3,.2,.2,.3]),
        "corporativo":np.random.choice(["Sí","No"],n,p=[.3,.7]),
        "informativo":np.random.choice(["Sí","No"],n,p=[.15,.85]),
        "fecha_creacion":fechas,"fecha_resolucion":f_res,"fecha_cierre":f_res,
        "sla_resolucion":sla_res,"sla_fr":sla_fr,"tiempo_hrs":res_hrs,
        "mismo_dia":same,"is_closed":is_c,
        "csat_global":csat_g,"csat_atencion":csat_a,"csat_rapidez":csat_r,"csat_solucion":csat_s,
    })
    df["fecha_creacion"] = pd.to_datetime(df["fecha_creacion"])
    df["fecha_resolucion"] = pd.to_datetime(df["fecha_resolucion"])
    df["anio"]      = df["fecha_creacion"].dt.year
    df["mes"]       = df["fecha_creacion"].dt.month
    df["mes_label"] = df["fecha_creacion"].dt.strftime("%b %Y")
    df["dia_sem"]   = df["fecha_creacion"].dt.day_name()
    return df

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
_secrets = load_secrets()

defaults = {
    "page":           "diagnostico",      # Arrancar en diagnóstico hasta confirmar conexión
    "use_demo":       _secrets is None,
    "access_token":   _secrets["access_token"]  if _secrets else "",
    "refresh_token":  _secrets["refresh_token"] if _secrets else "",
    "api_domain":     _secrets["api_domain"]    if _secrets else "https://www.zohoapis.com",
    "sdp_portal":     _secrets["sdp_portal"]    if _secrets else "https://soporte.kashio.net",
    "sdp_app_name":   _secrets.get("sdp_app_name","itdesk") if _secrets else "itdesk",
    "client_id":      _secrets["client_id"]     if _secrets else "",
    "client_secret":  _secrets["client_secret"] if _secrets else "",
    "token_ok":       False,
    "last_refresh":   None,
    "df_main":        None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def get_client() -> ZohoSDPClient | None:
    if not st.session_state.access_token or not st.session_state.sdp_portal:
        return None
    return ZohoSDPClient(
        sdp_portal    = st.session_state.sdp_portal,
        access_token  = st.session_state.access_token,
        refresh_token = st.session_state.refresh_token,
        api_domain    = st.session_state.api_domain,
        client_id     = st.session_state.client_id,
        client_secret = st.session_state.client_secret,
        app_name      = st.session_state.get("sdp_app_name", "itdesk"),
    )

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_from_api(portal, token, date_from_str, date_to_str):
    """Wrapper cacheable para la API."""
    client = ZohoSDPClient(portal, token, "")
    date_from = date.fromisoformat(date_from_str) if date_from_str else None
    date_to   = date.fromisoformat(date_to_str)   if date_to_str   else None
    return client.get_all_requests(date_from, date_to)

def load_data(date_from=None, date_to=None) -> pd.DataFrame:
    if st.session_state.use_demo:
        return demo_data()
    client = get_client()
    if not client:
        return demo_data()
    bar = st.progress(0, text="Conectando con ServiceDesk Plus...")
    try:
        loaded = [0]
        def progress(done, total):
            pct = min(int(done / max(total,1) * 100), 99)
            bar.progress(pct, text=f"Cargando tickets... {done}/{total}")
            loaded[0] = done

        df = client.get_all_requests(date_from, date_to, progress_cb=progress)
        bar.progress(100, text=f"✅ {len(df)} tickets cargados")
        time.sleep(0.5)
        bar.empty()
        return df
    except Exception as e:
        bar.empty()
        st.error(f"Error al cargar datos: {e}")
        return demo_data()

# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────
def kpi(label, value, color="blue", sub="", icon=""):
    return f"""<div class="kpi-card kpi-{color}">
      <div class="kpi-label">{icon} {label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

def donut(val_pct, color):
    fig = go.Figure(go.Pie(
        values=[val_pct, 100-val_pct], hole=0.72,
        marker_colors=[color, "#1e293b"],
        textinfo="none", showlegend=False, hoverinfo="none",
    ))
    fig.update_layout(
        plot_bgcolor="#1e293b", paper_bgcolor="#1e293b",
        margin=dict(l=5,r=5,t=5,b=5), height=120,
        annotations=[dict(text=f"<b>{val_pct:.0f}%</b>", x=0.5, y=0.5,
            font=dict(size=19, color="#f1f5f9", family="Inter"), showarrow=False)]
    )
    return fig

def ph(title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
      <div><h1>{title}</h1><p>{subtitle}</p></div>
    </div>""", unsafe_allow_html=True)

def apply_filters(df, date_from, date_to, f):
    if df is None or len(df) == 0: return df
    mask = (df["fecha_creacion"].dt.date >= date_from) & (df["fecha_creacion"].dt.date <= date_to)
    df = df[mask].copy()
    for field, col, none_val in [
        ("grupo","grupo","Todos"),("tecnico","tecnico","Todos"),
        ("prioridad","prioridad","Todas"),("tipo","tipo","Todos"),
        ("empresa","empresa","Todas"),("region","region","Todas"),
        ("estado","estado","Todos"),("tipo_empresa","tipo_empresa","Todas"),
    ]:
        if f.get(field, none_val) != none_val and col in df.columns:
            df = df[df[col] == f[field]]
    return df

def sort_months(df, col="mes_label"):
    df = df.copy()
    df["_sk"] = pd.to_datetime(df[col], format="%b %Y", errors="coerce")
    return df.sort_values("_sk").drop(columns="_sk")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Header
        connected = not st.session_state.use_demo and bool(st.session_state.access_token)
        badge = '<span class="token-badge token-ok">● LIVE</span>' if connected else '<span class="token-badge token-exp">● DEMO</span>'
        st.markdown(f"""
        <div style="padding:1rem 0 1.5rem;border-bottom:1px solid #334155;margin-bottom:1rem;">
          <div style="font-size:1.25rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.02em;">🎯 KashIO Support</div>
          <div style="margin-top:4px;">{badge}</div>
          <div style="font-size:0.68rem;color:#475569;margin-top:2px;">Dashboard Supervisor · SDP On-Demand</div>
        </div>""", unsafe_allow_html=True)

        # Nav
        pages = [
            ("general",      "📊","Informe General"),
            ("sla_fr",       "⚡","SLA · 1ra Respuesta"),
            ("sla_res",      "✅","SLA · Resolución"),
            ("grupos",       "👥","Grupo Resolutor"),
            ("encuestas",    "⭐","Encuestas CSAT"),
            ("alertas",      "🚨","Alertas & Pendientes"),
            ("config",       "⚙️","Configuración API"),
            ("diagnostico",  "🔬","Diagnóstico API"),
        ]
        for pid, icon, label in pages:
            active = st.session_state.page == pid
            t = "primary" if active else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{pid}", use_container_width=True, type=t):
                st.session_state.page = pid
                st.rerun()

        st.markdown("<div style='border-top:1px solid #334155;margin:1rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#475569;margin-bottom:0.75rem;'>🔍 Filtros Globales</div>", unsafe_allow_html=True)

        # Dates
        df_raw = demo_data() if st.session_state.use_demo else (st.session_state.df_main or demo_data())
        min_d = df_raw["fecha_creacion"].min().date() if len(df_raw) else date.today()-timedelta(365)
        max_d = df_raw["fecha_creacion"].max().date() if len(df_raw) else date.today()

        c1, c2 = st.columns(2)
        with c1: d_from = st.date_input("Desde", value=min_d, min_value=min_d, max_value=max_d, key="f_from")
        with c2: d_to   = st.date_input("Hasta", value=max_d, min_value=min_d, max_value=max_d, key="f_to")

        opts = lambda col, none: [none] + sorted(df_raw[col].dropna().unique().tolist()) if len(df_raw) else [none]

        f = {
            "grupo":       st.selectbox("Grupo",          opts("grupo","Todos"),          key="f_g"),
            "tecnico":     st.selectbox("Técnico",         opts("tecnico","Todos"),        key="f_t"),
            "prioridad":   st.selectbox("Prioridad",       opts("prioridad","Todas"),      key="f_p"),
            "tipo":        st.selectbox("Tipo",            opts("tipo","Todos"),            key="f_ti"),
            "empresa":     st.selectbox("Empresa",         opts("empresa","Todas"),         key="f_e"),
            "tipo_empresa":st.selectbox("Tipo Empresa",    opts("tipo_empresa","Todas"),   key="f_te"),
            "region":      st.selectbox("Región",          opts("region","Todas"),          key="f_r"),
            "estado":      st.selectbox("Estado",          opts("estado","Todos"),          key="f_s"),
        }

        st.markdown("<div style='border-top:1px solid #334155;margin:0.8rem 0;'></div>", unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Actualizar", use_container_width=True, type="primary"):
                st.cache_data.clear()
                st.session_state.df_main = None
                st.session_state.last_refresh = datetime.now()
                st.rerun()
        with col_r2:
            demo_toggle = st.toggle("Demo", value=st.session_state.use_demo, key="demo_t")
            if demo_toggle != st.session_state.use_demo:
                st.session_state.use_demo = demo_toggle
                st.rerun()

        if st.session_state.last_refresh:
            st.markdown(f"<div style='font-size:0.62rem;color:#475569;text-align:center;'>🕐 {st.session_state.last_refresh.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

    return d_from, d_to, f

# ─────────────────────────────────────────────
# PÁGINAS
# ─────────────────────────────────────────────
def page_general(df):
    ph("📊 Informe General de Tickets", "Visión consolidada del área de soporte")
    if df is None or len(df) == 0:
        st.warning("Sin datos en el período."); return

    total   = len(df)
    cerr    = df["is_closed"].sum()
    pend    = total - cerr
    mismo   = df["mismo_dia"].sum()
    pct_md  = mismo/cerr*100 if cerr else 0
    sla_ok  = df[df["is_closed"]]["sla_resolucion"].sum() if cerr else 0
    pct_sla = sla_ok/cerr*100 if cerr else 0
    t_prom  = df[df["is_closed"] & df["tiempo_hrs"].notna()]["tiempo_hrs"].mean()
    t_str   = f"{t_prom:.1f}h" if not np.isnan(t_prom) else "N/A"

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(kpi("Total Tickets",     f"{total:,}", "blue",   "período seleccionado",            "🎫"), unsafe_allow_html=True)
    c2.markdown(kpi("Cerrados",          f"{cerr:,}",  "green",  f"{cerr/total*100:.0f}% del total","✅"), unsafe_allow_html=True)
    c3.markdown(kpi("Pendientes",        f"{pend:,}",  "yellow", "sin resolver",                    "⏳"), unsafe_allow_html=True)
    c4.markdown(kpi("Mismo día",         f"{mismo:,}", "cyan",   f"{pct_md:.0f}% de cerrados",      "⚡"), unsafe_allow_html=True)
    c5.markdown(kpi("SLA Resolución",    f"{pct_sla:.0f}%", "green" if pct_sla>=85 else "red", "cumplimiento","🎯"), unsafe_allow_html=True)
    c6.markdown(kpi("Tiempo Promedio",   t_str,        "blue",   "horas de resolución",             "⏱️"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Tendencia + pie
    col_l, col_r = st.columns([3,1])
    with col_l:
        dg = sort_months(df.groupby("mes_label").agg(
            total=("id","count"), cerrados=("is_closed","sum"), mismo_dia=("mismo_dia","sum")).reset_index())
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dg["mes_label"], y=dg["total"], name="Total",
            line=dict(color=CHART_T["blue"],width=2.5), fill="tozeroy", fillcolor="rgba(59,130,246,0.1)", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=dg["mes_label"], y=dg["cerrados"], name="Cerrados",
            line=dict(color=CHART_T["green"],width=2,dash="dot"), mode="lines+markers"))
        fig.add_trace(go.Scatter(x=dg["mes_label"], y=dg["mismo_dia"], name="Mismo día",
            line=dict(color=CHART_T["cyan"],width=1.5,dash="dash"), mode="lines+markers"))
        fig.update_layout(**clo("📈 Tendencia mensual", height=280))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with col_r:
        tc = df["tipo"].value_counts().reset_index(); tc.columns=["tipo","n"]
        fp = px.pie(tc, values="n", names="tipo",
            color_discrete_sequence=[CHART_T["blue"],CHART_T["green"],CHART_T["yellow"]])
        fp.update_traces(textposition="inside", textinfo="percent+label")
        fp.update_layout(**clo("Por tipo", height=280, showlegend=False))
        st.plotly_chart(fp, use_container_width=True, config={"displayModeBar":False})

    # Por empresa + tipo empresa
    c_a, c_b = st.columns(2)
    with c_a:
        de = df.groupby("empresa").agg(total=("id","count"),cerr=("is_closed","sum")).reset_index().sort_values("total",ascending=True).tail(10)
        fe = go.Figure()
        fe.add_trace(go.Bar(y=de["empresa"], x=de["total"], name="Total", orientation="h", marker_color=CHART_T["blue"]))
        fe.add_trace(go.Bar(y=de["empresa"], x=de["cerr"],  name="Cerrados", orientation="h", marker_color=CHART_T["green"]))
        fe.update_layout(**clo("🏢 Top 10 empresas", height=310), barmode="overlay")
        st.plotly_chart(fe, use_container_width=True, config={"displayModeBar":False})
    with c_b:
        if "tipo_empresa" in df.columns:
            dte = df.groupby(["tipo_empresa","tipo"]).size().reset_index(name="n")
            fte = px.bar(dte, x="tipo_empresa", y="n", color="tipo",
                color_discrete_map={"Incidente":CHART_T["red"],"Requerimiento":CHART_T["blue"],"Consulta":CHART_T["yellow"]},
                barmode="group")
            fte.update_layout(**clo("🏭 Por tipo empresa", height=310))
            st.plotly_chart(fte, use_container_width=True, config={"displayModeBar":False})

    # Región + día semana
    c_c, c_d = st.columns(2)
    with c_c:
        dr = df.groupby(["region","tipo"]).size().reset_index(name="n")
        fr = px.bar(dr, x="region", y="n", color="tipo",
            color_discrete_map={"Incidente":CHART_T["red"],"Requerimiento":CHART_T["blue"],"Consulta":CHART_T["yellow"]})
        fr.update_layout(**clo("🗺️ Por región", height=260))
        st.plotly_chart(fr, use_container_width=True, config={"displayModeBar":False})
    with c_d:
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow_es    = {"Monday":"Lun","Tuesday":"Mar","Wednesday":"Mié","Thursday":"Jue",
                     "Friday":"Vie","Saturday":"Sáb","Sunday":"Dom"}
        dd = df["dia_sem"].value_counts().reindex(dow_order).fillna(0).reset_index()
        dd.columns=["dia","n"]; dd["dia"]=dd["dia"].map(dow_es)
        fd = px.bar(dd, x="dia", y="n", color="n", color_continuous_scale=["#1e3a5f","#3b82f6"])
        fd.update_layout(**clo("📅 Día de semana", height=260, showlegend=False), coloraxis_showscale=False)
        st.plotly_chart(fd, use_container_width=True, config={"displayModeBar":False})

    # Tabla detalle
    st.markdown("<div class='section-title'>📋 Tickets Recientes</div>", unsafe_allow_html=True)
    cols = ["display_id","fecha_creacion","asunto","solicitante","tipo","estado","prioridad","tecnico","empresa"]
    cols = [c for c in cols if c in df.columns]
    d2 = df[cols].head(60).copy()
    d2["fecha_creacion"] = d2["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
    d2.columns = [c.replace("_"," ").title() for c in d2.columns]
    st.dataframe(d2, use_container_width=True, hide_index=True, height=300)


def page_sla_fr(df):
    ph("⚡ SLA · Primera Respuesta", "Cumplimiento del tiempo de primera respuesta")
    if df is None or len(df) == 0: st.warning("Sin datos."); return

    total = len(df)
    cum   = df["sla_fr"].sum()
    pct   = cum/total*100 if total else 0

    def tipo_pct(t):
        d = df[df["tipo"]==t]
        return d["sla_fr"].mean()*100 if len(d) else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, val, lbl, clr in [
        (c1, pct,               "Global",           CHART_T["green"] if pct>=85 else CHART_T["red"]),
        (c2, tipo_pct("Incidente"),   "Incidentes",  CHART_T["blue"]),
        (c3, tipo_pct("Requerimiento"),"Requerimientos",CHART_T["purple"]),
        (c4, tipo_pct("Consulta"),    "Consultas",   CHART_T["cyan"]),
    ]:
        with col:
            st.plotly_chart(donut(val, clr), use_container_width=True, config={"displayModeBar":False})
            st.markdown(f"<div class='donut-label'>{lbl}</div>", unsafe_allow_html=True)
    with c5:
        st.markdown(kpi("Incumplidos", f"{total-cum:,}", "red", f"{100-pct:.1f}% del total","❌"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    c_a, c_b = st.columns(2)
    with c_a:
        dg = df.groupby("tipo").agg(total=("id","count"), cum=("sla_fr","sum")).reset_index()
        dg["pct"] = (dg["cum"]/dg["total"]*100).round(1)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dg["tipo"], y=dg["total"], name="Total", marker_color=CHART_T["blue"]))
        fig.add_trace(go.Bar(x=dg["tipo"], y=dg["cum"],   name="1ra Rpta OK", marker_color=CHART_T["green"]))
        fig.add_trace(go.Scatter(x=dg["tipo"], y=dg["pct"], name="%", yaxis="y2",
            mode="markers+lines", marker=dict(color=CHART_T["yellow"],size=10),
            line=dict(color=CHART_T["yellow"],width=2)))
        fig.update_layout(**clo("Por tipo", height=290),
            yaxis2=dict(overlaying="y",side="right",ticksuffix="%",gridcolor="transparent",color=CHART_T["text"]),
            barmode="group")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with c_b:
        dg2 = df.groupby("prioridad").agg(total=("id","count"), cum=("sla_fr","sum")).reset_index()
        dg2["pct"] = (dg2["cum"]/dg2["total"]*100).round(1)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=dg2["prioridad"], y=dg2["total"], name="Total", marker_color=CHART_T["blue"]))
        fig2.add_trace(go.Bar(x=dg2["prioridad"], y=dg2["cum"],   name="Cumplido", marker_color=CHART_T["green"]))
        fig2.add_trace(go.Scatter(x=dg2["prioridad"], y=dg2["pct"], name="%", yaxis="y2",
            mode="markers+lines", marker=dict(color=CHART_T["yellow"],size=10),
            line=dict(color=CHART_T["yellow"],width=2)))
        fig2.update_layout(**clo("Por prioridad", height=290),
            yaxis2=dict(overlaying="y",side="right",ticksuffix="%",gridcolor="transparent",color=CHART_T["text"]),
            barmode="group")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    # Tendencia mensual
    dt = sort_months(df.groupby("mes_label").agg(total=("id","count"), cum=("sla_fr","sum")).reset_index())
    dt["pct"] = (dt["cum"]/dt["total"]*100).round(1)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=dt["mes_label"], y=dt["pct"], name="% SLA",
        mode="lines+markers", line=dict(color=CHART_T["green"],width=2.5),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.1)"))
    fig3.add_hline(y=85, line=dict(color=CHART_T["red"],width=1.5,dash="dash"),
                   annotation_text="Meta 85%", annotation_font_color=CHART_T["red"])
    fig3.update_layout(**clo("📈 Tendencia SLA 1ra Respuesta mensual", height=260))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})


def page_sla_res(df):
    ph("✅ SLA · Resolución", "Cumplimiento del tiempo de resolución final")
    if df is None or len(df) == 0: st.warning("Sin datos."); return

    dc = df[df["is_closed"]].copy()
    if len(dc) == 0: st.info("Sin tickets cerrados en el período."); return

    total = len(dc)
    cum   = dc["sla_resolucion"].sum()
    pct   = cum/total*100 if total else 0
    t_p   = dc["tiempo_hrs"].mean()

    def prio_pct(p):
        d = dc[dc["prioridad"]==p]
        return d["sla_resolucion"].mean()*100 if len(d) else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    donuts = [
        (c1, pct,             "Global",  CHART_T["green"] if pct>=85 else CHART_T["red"]),
        (c2, prio_pct("Critica"), "Crítica", CHART_T["red"]),
        (c3, prio_pct("Alta"),    "Alta",    CHART_T["orange"]),
        (c4, prio_pct("Media"),   "Media",   CHART_T["yellow"]),
    ]
    for col, val, lbl, clr in donuts:
        with col:
            st.plotly_chart(donut(val, clr), use_container_width=True, config={"displayModeBar":False})
            st.markdown(f"<div class='donut-label'>{lbl}</div>", unsafe_allow_html=True)
    with c5: st.markdown(kpi("Incumplido",  f"{100-pct:.0f}%", "red",  f"{total-cum:,} tickets","❌"), unsafe_allow_html=True)
    with c6: st.markdown(kpi("Tiempo Prom", f"{t_p:.1f}h" if not np.isnan(t_p) else "N/A", "blue","resolución","⏱️"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    c_a, c_b = st.columns(2)
    with c_a:
        dg = dc.groupby("tipo").agg(total=("id","count"), cum=("sla_resolucion","sum")).reset_index()
        dg["pct"] = (dg["cum"]/dg["total"]*100).round(1)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dg["tipo"], y=dg["total"], name="Total", marker_color=CHART_T["blue"]))
        fig.add_trace(go.Bar(x=dg["tipo"], y=dg["cum"],   name="SLA OK", marker_color=CHART_T["green"]))
        fig.add_trace(go.Scatter(x=dg["tipo"], y=dg["pct"], yaxis="y2", name="%",
            mode="markers+lines", marker=dict(color=CHART_T["yellow"],size=10),
            line=dict(color=CHART_T["yellow"],width=2)))
        fig.update_layout(**clo("Por tipo", height=290),
            yaxis2=dict(overlaying="y",side="right",ticksuffix="%",gridcolor="transparent",color=CHART_T["text"]),
            barmode="group")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with c_b:
        dt2 = dc.groupby("prioridad")["tiempo_hrs"].mean().reset_index()
        dt2["color"] = dt2["prioridad"].map(PRIORITY_COLORS).fillna("#64748b")
        fig2 = go.Figure(go.Bar(x=dt2["prioridad"], y=dt2["tiempo_hrs"],
            marker_color=dt2["color"].tolist(),
            text=dt2["tiempo_hrs"].round(1).astype(str)+"h", textposition="outside"))
        fig2.update_layout(**clo("⏱️ Tiempo Prom. por prioridad (hrs)", height=290))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    dt = sort_months(dc.groupby("mes_label").agg(total=("id","count"), cum=("sla_resolucion","sum")).reset_index())
    dt["pct"] = (dt["cum"]/dt["total"]*100).round(1)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=dt["mes_label"], y=dt["total"], name="Cerrados", marker_color=CHART_T["blue"], opacity=0.55))
    fig3.add_trace(go.Scatter(x=dt["mes_label"], y=dt["pct"], name="% SLA", yaxis="y2",
        mode="lines+markers", line=dict(color=CHART_T["green"],width=2.5), marker=dict(size=7)))
    fig3.add_hline(y=85, yref="y2", line=dict(color=CHART_T["red"],width=1.5,dash="dash"),
                   annotation_text="Meta 85%", annotation_font_color=CHART_T["red"])
    fig3.update_layout(**clo("📈 Tendencia SLA Resolución mensual", height=270),
        yaxis2=dict(overlaying="y",side="right",ticksuffix="%",gridcolor="transparent",color=CHART_T["text"]))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    st.markdown("<div class='section-title'>SLA por empresa × prioridad</div>", unsafe_allow_html=True)
    dpiv = dc.groupby(["empresa","prioridad"]).agg(
        pct=("sla_resolucion", lambda x: f"{x.mean()*100:.0f}%"),
        n=("id","count")
    ).reset_index()
    piv = dpiv.pivot_table(index="empresa", columns="prioridad", values=["pct","n"], aggfunc="first")
    st.dataframe(piv, use_container_width=True)


def page_grupos(df):
    ph("👥 Grupo Resolutor", "Desempeño de grupos y técnicos de soporte")
    if df is None or len(df) == 0: st.warning("Sin datos."); return

    tab1, tab2 = st.tabs(["📊 Por Grupo", "👤 Por Técnico"])

    with tab1:
        dg = df.groupby("grupo").agg(
            total=("id","count"), cerr=("is_closed","sum"),
            sla=("sla_resolucion","sum"), t_prom=("tiempo_hrs","mean"), md=("mismo_dia","sum")
        ).reset_index()
        dg["pct_sla"]  = (dg["sla"]/dg["cerr"].replace(0,1)*100).round(1)
        dg["pct_cerr"] = (dg["cerr"]/dg["total"]*100).round(1)

        c_a, c_b = st.columns(2)
        with c_a:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=dg["grupo"], y=dg["total"], name="Total", marker_color=CHART_T["blue"]))
            fig1.add_trace(go.Bar(x=dg["grupo"], y=dg["cerr"],  name="Cerrados+Resueltos", marker_color=CHART_T["green"]))
            fig1.add_trace(go.Scatter(x=dg["grupo"], y=dg["pct_sla"], name="% SLA", yaxis="y2",
                mode="lines+markers", line=dict(color=CHART_T["yellow"],width=2)))
            fig1.update_layout(**clo("Tickets por grupo vs SLA", height=300),
                yaxis2=dict(overlaying="y",side="right",ticksuffix="%",gridcolor="transparent",color=CHART_T["text"]),
                barmode="group")
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar":False})
        with c_b:
            fig2 = go.Figure(go.Bar(x=dg["grupo"], y=dg["t_prom"],
                marker_color=CHART_T["purple"],
                text=dg["t_prom"].round(1).astype(str)+"h", textposition="outside"))
            fig2.update_layout(**clo("⏱️ Tiempo prom. resolución (hrs)", height=300))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

        st.markdown("<div class='section-title'>Tabla por grupo</div>", unsafe_allow_html=True)
        d_show = dg[["grupo","total","cerr","pct_sla","t_prom","md"]].copy()
        d_show.columns=["Grupo","Total","Cerrados","SLA%","T.Prom(h)","Mismo Día"]
        d_show["T.Prom(h)"] = d_show["T.Prom(h)"].round(1)
        st.dataframe(d_show, use_container_width=True, hide_index=True)

    with tab2:
        dt = df.groupby(["tecnico","grupo"]).agg(
            total=("id","count"), cerr=("is_closed","sum"),
            sla=("sla_resolucion","sum"), t_prom=("tiempo_hrs","mean"), md=("mismo_dia","sum")
        ).reset_index()
        dt["pct_sla"] = (dt["sla"]/dt["cerr"].replace(0,1)*100).round(1)
        dt["pct_md"]  = (dt["md"]/dt["cerr"].replace(0,1)*100).round(1)
        dt = dt.sort_values("total", ascending=False)

        fig_t = go.Figure()
        fig_t.add_trace(go.Bar(y=dt["tecnico"], x=dt["total"], name="Total", orientation="h", marker_color=CHART_T["blue"]))
        fig_t.add_trace(go.Bar(y=dt["tecnico"], x=dt["cerr"],  name="Cerrados", orientation="h", marker_color=CHART_T["green"]))
        fig_t.update_layout(**clo("🏆 Desempeño por técnico", height=360), barmode="overlay")
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar":False})

        d_show = dt[["tecnico","grupo","total","cerr","pct_sla","t_prom","pct_md"]].copy()
        d_show.columns=["Técnico","Grupo","Total","Cerrados","SLA%","T.Prom(h)","%Mismo Día"]
        d_show["T.Prom(h)"] = d_show["T.Prom(h)"].round(1)
        st.dataframe(d_show, use_container_width=True, hide_index=True)


def page_encuestas(df):
    ph("⭐ Encuestas CSAT", "Satisfacción del usuario: atención, rapidez, solución y experiencia global")
    if df is None or len(df) == 0: st.warning("Sin datos."); return

    has_csat = "csat_global" in df.columns
    ds = df[df["csat_global"].notna()].copy() if has_csat else pd.DataFrame()

    if len(ds) == 0:
        st.info("No hay datos de encuestas CSAT en el período seleccionado (requiere integración con encuestas de SDP)."); return

    g  = ds["csat_global"].mean()
    a  = ds["csat_atencion"].mean()  if "csat_atencion" in ds else g
    r  = ds["csat_rapidez"].mean()   if "csat_rapidez"  in ds else g
    s  = ds["csat_solucion"].mean()  if "csat_solucion" in ds else g

    def cc(v): return "green" if v>=4 else "yellow" if v>=3 else "red"
    def ss(v): return "⭐"*round(v) if not np.isnan(v) else "N/A"

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("CSAT Global",   f"{g:.2f}", cc(g), ss(g), "🌐"), unsafe_allow_html=True)
    c2.markdown(kpi("Atención",      f"{a:.2f}", cc(a), ss(a), "🤝"), unsafe_allow_html=True)
    c3.markdown(kpi("Rapidez",       f"{r:.2f}", cc(r), ss(r), "⚡"), unsafe_allow_html=True)
    c4.markdown(kpi("Solución",      f"{s:.2f}", cc(s), ss(s), "✅"), unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    c_a, c_b = st.columns(2)
    with c_a:
        cats = ["Atención","Rapidez","Solución","Global"]
        vals = [a, r, s, g]
        fig_radar = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]],
            fill="toself", fillcolor="rgba(59,130,246,0.15)",
            line=dict(color=CHART_T["blue"],width=2), marker=dict(color=CHART_T["blue"],size=8)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,5],
                gridcolor=CHART_T["grid"], color=CHART_T["text"]),
                angularaxis=dict(color=CHART_T["text"]), bgcolor=CHART_T["paper"]),
            paper_bgcolor=CHART_T["paper"], font=dict(color=CHART_T["text"],family="Inter"),
            showlegend=False, height=290, margin=dict(l=40,r=40,t=35,b=35),
            title=dict(text="⭐ Radar CSAT", font=dict(color="#e2e8f0",size=13))
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})
    with c_b:
        dt = ds.groupby("tecnico").agg(avg=("csat_global","mean"), n=("csat_global","count")).reset_index()
        dt = dt.sort_values("avg", ascending=True)
        fig_t = go.Figure(go.Bar(
            y=dt["tecnico"], x=dt["avg"], orientation="h",
            marker=dict(color=dt["avg"],
                colorscale=[[0,CHART_T["red"]],[0.5,CHART_T["yellow"]],[1,CHART_T["green"]]],
                cmin=1, cmax=5),
            text=dt["avg"].round(2), textposition="outside"
        ))
        fig_t.update_layout(**clo("CSAT por técnico", height=290))
        fig_t.update_xaxes(range=[0,5.5])
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar":False})

    c_c, c_d = st.columns(2)
    with c_c:
        ds["stars"] = ds["csat_global"].round().astype(int).clip(1,5)
        sc = ds["stars"].value_counts().sort_index()
        fig_s = go.Figure(go.Bar(
            x=[f"{'⭐'*i}" for i in sc.index], y=sc.values,
            marker_color=[CHART_T["red"],CHART_T["orange"],CHART_T["yellow"],CHART_T["cyan"],CHART_T["green"]][:len(sc)]
        ))
        fig_s.update_layout(**clo("Distribución de calificaciones", height=250, showlegend=False))
        st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar":False})
    with c_d:
        dm = sort_months(ds.groupby("mes_label").agg(avg=("csat_global","mean")).reset_index())
        fig_m = go.Figure(go.Scatter(x=dm["mes_label"], y=dm["avg"],
            mode="lines+markers", line=dict(color=CHART_T["yellow"],width=2.5),
            marker=dict(size=8), fill="tozeroy", fillcolor="rgba(245,158,11,0.1)"))
        fig_m.add_hline(y=4.0, line=dict(color=CHART_T["green"],width=1.5,dash="dash"),
                        annotation_text="Meta 4.0", annotation_font_color=CHART_T["green"])
        fig_m.update_layout(**clo("Tendencia CSAT mensual", height=250))
        fig_m.update_yaxes(range=[0,5.5])
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar":False})


def page_alertas(df):
    ph("🚨 Alertas & Tickets Pendientes", "Vista operativa en tiempo real — tickets críticos, vencidos y en riesgo de SLA")
    if df is None or len(df) == 0: st.warning("Sin datos."); return

    now    = datetime.now()
    do_    = df[~df["is_closed"]].copy()
    d_crit = do_[do_["prioridad"]=="Critica"]
    d_alta = do_[do_["prioridad"]=="Alta"]
    d_old  = do_[do_["fecha_creacion"] < pd.Timestamp(now-timedelta(hours=48))]

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(kpi("Abiertos Totales", str(len(do_)),    "yellow","sin resolver",    "⏳"), unsafe_allow_html=True)
    c2.markdown(kpi("Críticos",         str(len(d_crit)), "red",   "prioridad crítica","🔴"), unsafe_allow_html=True)
    c3.markdown(kpi("Alta Prioridad",   str(len(d_alta)), "orange","prioridad alta",   "🟠"), unsafe_allow_html=True)
    c4.markdown(kpi(">48h sin cerrar",  str(len(d_old)),  "red",   "antigüedad alta",  "⚠️"), unsafe_allow_html=True)

    if len(d_crit)>0: st.markdown(f'<div class="alert-critical">🔴 <b>{len(d_crit)} ticket(s) crítico(s)</b> abiertos — requieren atención inmediata</div>', unsafe_allow_html=True)
    if len(d_old)>0:  st.markdown(f'<div class="alert-warning">⚠️ <b>{len(d_old)} ticket(s)</b> con más de 48 horas abiertos</div>', unsafe_allow_html=True)
    if len(d_crit)==0 and len(d_old)==0:
        st.markdown('<div class="alert-info">✅ Sin alertas críticas en este momento</div>', unsafe_allow_html=True)

    c_a, c_b = st.columns(2)
    with c_a:
        dp = do_["prioridad"].value_counts().reset_index(); dp.columns=["p","n"]
        colors = [PRIORITY_COLORS.get(p,"#64748b") for p in dp["p"]]
        fig1 = go.Figure(go.Bar(x=dp["p"], y=dp["n"], marker_color=colors,
            text=dp["n"], textposition="outside"))
        fig1.update_layout(**clo("Por prioridad", height=250, showlegend=False))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar":False})
    with c_b:
        dg = do_.groupby("grupo").size().reset_index(name="n").sort_values("n",ascending=True)
        fig2 = go.Figure(go.Bar(y=dg["grupo"], x=dg["n"], orientation="h",
            marker_color=CHART_T["orange"], text=dg["n"], textposition="outside"))
        fig2.update_layout(**clo("Por grupo", height=250, showlegend=False))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    # Tabla críticos
    st.markdown("<div class='section-title'>🔴 Críticos Abiertos</div>", unsafe_allow_html=True)
    if len(d_crit)>0:
        dc2 = d_crit[["display_id","fecha_creacion","asunto","solicitante","empresa","tecnico","grupo","estado"]].copy()
        dc2["Hrs Abierto"] = d_crit["fecha_creacion"].apply(
            lambda x: f"{(now-x.to_pydatetime()).total_seconds()/3600:.0f}h" if pd.notna(x) else "N/A").values
        dc2["fecha_creacion"] = dc2["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
        dc2.columns=["ID","Fecha","Asunto","Solicitante","Empresa","Técnico","Grupo","Estado","Hrs Abierto"]
        st.dataframe(dc2, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Sin tickets críticos abiertos")

    # Tabla >48h
    st.markdown("<div class='section-title'>⚠️ Tickets +48h Abiertos</div>", unsafe_allow_html=True)
    if len(d_old)>0:
        do2 = d_old[["display_id","fecha_creacion","asunto","solicitante","empresa","prioridad","tecnico","grupo"]].copy()
        do2["Hrs Abierto"] = d_old["fecha_creacion"].apply(
            lambda x: round((now-x.to_pydatetime()).total_seconds()/3600,0) if pd.notna(x) else 0).values
        do2["fecha_creacion"] = do2["fecha_creacion"].dt.strftime("%d/%m/%Y %H:%M")
        do2.columns=["ID","Fecha","Asunto","Solicitante","Empresa","Prioridad","Técnico","Grupo","Hrs Abierto"]
        do2 = do2.sort_values("Hrs Abierto", ascending=False)
        st.dataframe(do2, use_container_width=True, hide_index=True)


def page_config():
    ph("⚙️ Configuración API · ServiceDesk Plus On-Demand")

    # Estado del token
    secrets = load_secrets()
    if secrets:
        st.markdown("""
        <div class="alert-info">
        🔑 <b>Tokens cargados desde secrets.toml</b> — La app está preconfigurada con tu acceso OAuth Zoho.
        Puedes sobreescribir los valores a continuación si necesitas usar otros tokens.
        </div>""", unsafe_allow_html=True)

    # Test de conexión rápido
    if st.button("🧪 Probar conexión actual", type="primary"):
        client = get_client()
        if not client:
            st.error("Sin portal o token configurado")
        else:
            with st.spinner("Conectando..."):
                ok, msg, _ = client.test_connection()
            if ok: st.success(f"✅ {msg}")
            else:  st.error(f"❌ {msg}")

    st.markdown("---")
    st.markdown("### 🔧 Configuración manual / actualización de token")

    with st.form("cfg_form"):
        col1, col2 = st.columns(2)
        with col1:
            portal = st.text_input("Portal SDP (URL base)", value=st.session_state.sdp_portal,
                placeholder="https://sdpondemand.manageengine.com")
            api_d  = st.text_input("API Domain", value=st.session_state.api_domain,
                placeholder="https://www.zohoapis.com")
        with col2:
            at = st.text_input("Access Token",  value=st.session_state.access_token,  type="password")
            rt = st.text_input("Refresh Token", value=st.session_state.refresh_token, type="password")

        col3, col4 = st.columns(2)
        with col3:
            cid  = st.text_input("Client ID (opcional — para auto-refresh)",  value=st.session_state.client_id)
        with col4:
            csec = st.text_input("Client Secret (opcional)", value=st.session_state.client_secret, type="password")

        s1, s2, _ = st.columns([1,1,2])
        with s1: save = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
        with s2: ref  = st.form_submit_button("🔁 Renovar token", use_container_width=True)

        if save:
            st.session_state.sdp_portal     = portal
            st.session_state.api_domain     = api_d
            st.session_state.access_token   = at
            st.session_state.refresh_token  = rt
            st.session_state.client_id      = cid
            st.session_state.client_secret  = csec
            st.session_state.use_demo       = False
            st.success("✅ Configuración guardada. Desactiva el modo Demo en el sidebar.")

        if ref:
            c = ZohoSDPClient(portal, at, rt, api_d, cid, csec)
            ok, msg = c.refresh_access_token()
            if ok:
                st.session_state.access_token = c.access_token
                st.success(f"✅ {msg} — Nuevo token guardado en sesión")
            else:
                st.error(f"❌ {msg}")

    st.markdown("---")
    st.markdown("""
    ### 📖 Referencia rápida OAuth — ServiceDesk Plus On-Demand

    | Campo | Valor configurado |
    |-------|-------------------|
    | Token type | `Zoho-oauthtoken` (Bearer) |
    | Header | `Authorization: Zoho-oauthtoken {access_token}` |
    | Scope | `SDPOnDemand.requests.READ` |
    | Expiración access token | 1 hora — usa refresh_token para renovar |
    | Endpoint tickets | `{portal}/api/v3/requests` |
    | Refresh endpoint | `https://accounts.zoho.com/oauth/v2/token` |

    ### 📦 secrets.toml (para Streamlit Cloud)
    ```toml
    [zoho]
    access_token  = "1000.xxx..."
    refresh_token = "1000.yyy..."
    api_domain    = "https://www.zohoapis.com"
    sdp_portal    = "https://sdpondemand.manageengine.com"
    # client_id   = ""   # opcional
    # client_secret = "" # opcional
    ```
    > En Streamlit Cloud: **Settings → Secrets** → pega el bloque `[zoho]`

    ### 🗺️ Mapeo de campos UDF
    Edita el método `_parse()` en `ZohoSDPClient` si tus campos adicionales
    usan claves distintas:
    ```python
    "empresa":      udf_get("udf_sline_1", "Empresa"),
    "tipo_empresa": udf_get("udf_sline_2", "Tipo de Empresa"),
    "region":       udf_get("udf_sline_3", "Región"),
    ```
    """)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    d_from, d_to, filters = render_sidebar()

    # Cargar datos una sola vez por sesión / cambio de filtros
    if st.session_state.page not in ("config", "diagnostico"):
        if st.session_state.df_main is None or st.session_state.use_demo:
            raw = load_data(d_from, d_to)
            if not st.session_state.use_demo:
                st.session_state.df_main = raw
        else:
            raw = st.session_state.df_main

        df = apply_filters(raw, d_from, d_to, filters)
    else:
        df = None

    page = st.session_state.page
    if   page == "general":      page_general(df)
    elif page == "sla_fr":       page_sla_fr(df)
    elif page == "sla_res":      page_sla_res(df)
    elif page == "grupos":       page_grupos(df)
    elif page == "encuestas":    page_encuestas(df)
    elif page == "alertas":      page_alertas(df)
    elif page == "config":       page_config()
    elif page == "diagnostico":  page_diagnostico()

if __name__ == "__main__":
    main()


# ─────────────────────────────────────────────
# PÁGINA DE DIAGNÓSTICO — AGREGA AL ROUTER
# ─────────────────────────────────────────────
def page_diagnostico():
    ph("🔬 Diagnóstico de API", "Verifica la conexión real con ServiceDesk Plus On-Demand")

    st.markdown("""
    <div class="alert-info">
    ℹ️ Esta página hace llamadas <b>reales</b> al API REST de SDP (no usa conector).
    Úsala para verificar que la conexión y los tokens funcionan correctamente.
    </div>""", unsafe_allow_html=True)

    # ── PASO 1: VERIFICAR URL DEL PORTAL ──
    st.markdown("### Paso 1 — URL del portal SDP")
    st.markdown("""
    Tu portal SDP On-Demand tiene una URL única. Puedes encontrarla:
    - Entrando a SDP desde el navegador: la URL del browser **es** tu portal
    - Preguntando al admin de Zoho en el panel de Zoho Developer Console
    
    Ejemplos:
    - `https://kashio.sdpondemand.manageengine.com`
    - `https://helpdesk.tuempresa.com` (si tienes dominio personalizado)
    """)

    portal_input = st.text_input(
        "URL base del portal SDP",
        value=st.session_state.get("sdp_portal", "https://soporte.kashio.net"),
        placeholder="https://soporte.kashio.net",
        key="diag_portal"
    )
    app_name_input = st.text_input(
        "Nombre de la app SDP (parte de la URL: /app/itdesk/...)",
        value=st.session_state.get("sdp_app_name", "itdesk"),
        placeholder="itdesk",
        key="diag_appname"
    )
    token_input = st.text_input(
        "Access Token (pega uno nuevo si expiró)",
        value=st.session_state.get("access_token", ""),
        type="password",
        key="diag_token"
    )

    if st.button("🧪 Ejecutar diagnóstico completo", type="primary"):
        if not portal_input:
            st.error("⚠️ Ingresa la URL del portal primero"); return
        if not token_input:
            st.error("⚠️ Ingresa el access token"); return

        portal = portal_input.rstrip("/")
        token  = token_input.strip()
        headers = {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Test 1: Ping al portal
        st.markdown("#### Test 1 — Conectividad al portal")
        with st.spinner("Probando conexión..."):
            try:
                import requests as req, json as js
                r = req.get(portal, timeout=10, allow_redirects=True)
                st.success(f"✅ Portal accesible — HTTP {r.status_code}")
            except Exception as e:
                st.error(f"❌ No se pudo conectar al portal: {e}")
                st.stop()

        # Test 2: Auth endpoint /api/v3/requests con 1 registro
        st.markdown("#### Test 2 — Autenticación OAuth (GET /api/v3/requests)")
        app_name = app_name_input.strip() or "itdesk"
        candidates = [
            f"{portal}/app/{app_name}/api/v3/requests",
            f"{portal}/api/v3/requests",
            f"{portal}/app/itdesk/api/v3/requests",
        ]

        working_url = None
        for url in candidates:
            with st.spinner(f"Probando `{url}`..."):
                try:
                    r = req.get(url, headers=headers,
                               params={"input_data": js.dumps({"list_info":{"row_count":1,"start_index":1}})},
                               timeout=15)
                    code = r.status_code
                    try: body = r.json()
                    except: body = {"raw": r.text[:500]}

                    col_s, col_c = st.columns([3,1])
                    with col_c:
                        if code == 200: st.success(f"HTTP {code}")
                        elif code == 401: st.error(f"HTTP {code} — Token expirado/inválido")
                        elif code == 403: st.error(f"HTTP {code} — Sin permisos (scope)")
                        elif code == 404: st.warning(f"HTTP {code} — URL no encontrada")
                        else: st.warning(f"HTTP {code}")
                    with col_s:
                        st.code(f"URL: {url}", language="text")

                    with st.expander(f"Ver respuesta completa — {url}"):
                        st.json(body if isinstance(body, dict) else {"response": str(body)[:1000]})

                    if code == 200 and "requests" in body:
                        working_url = url
                        st.success(f"🎉 URL correcta encontrada: `{url}`")
                        total = body.get("list_info", {}).get("total_count", "?")
                        st.info(f"📊 Total de tickets en SDP: **{total}**")
                        break
                except Exception as e:
                    st.error(f"Error al llamar `{url}`: {e}")

        if not working_url:
            st.error("❌ Ninguna URL funcionó. Revisa los pasos de solución abajo.")

        # Test 3: Ver estructura de 1 ticket real
        if working_url:
            st.markdown("#### Test 3 — Estructura de un ticket real")
            try:
                r = req.get(working_url, headers=headers,
                           params={"input_data": js.dumps({"list_info":{"row_count":1,"start_index":1}})},
                           timeout=15)
                tickets = r.json().get("requests", [])
                if tickets:
                    t = tickets[0]
                    st.success(f"✅ Ticket de muestra: #{t.get('display_id', t.get('id'))}")

                    # Mostrar campos relevantes
                    campos = {
                        "subject":       t.get("subject"),
                        "status":        t.get("status", {}).get("name") if isinstance(t.get("status"), dict) else t.get("status"),
                        "priority":      t.get("priority", {}).get("name") if isinstance(t.get("priority"), dict) else t.get("priority"),
                        "request_type":  t.get("request_type", {}).get("name") if isinstance(t.get("request_type"), dict) else t.get("request_type"),
                        "group":         t.get("group", {}).get("name") if isinstance(t.get("group"), dict) else t.get("group"),
                        "technician":    t.get("technician", {}).get("name") if isinstance(t.get("technician"), dict) else t.get("technician"),
                        "created_time":  t.get("created_time", {}).get("display_value") if isinstance(t.get("created_time"), dict) else t.get("created_time"),
                        "udf_fields":    t.get("udf_fields", {}),
                        "additional_fields": t.get("additional_fields", []),
                    }
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Campos principales detectados:**")
                        for k, v in campos.items():
                            if k not in ("udf_fields", "additional_fields"):
                                st.markdown(f"- `{k}`: `{v}`")
                    with c2:
                        st.markdown("**Campos adicionales (UDF):**")
                        udf = campos["udf_fields"] or {}
                        if udf:
                            for k, v in list(udf.items())[:10]:
                                st.markdown(f"- `{k}`: `{v}`")
                        else:
                            st.markdown("*(sin UDF en este ticket)*")
                        adf = campos["additional_fields"] or []
                        if adf:
                            st.markdown("**Additional fields:**")
                            for f in adf[:5]:
                                st.markdown(f"- `{f.get('label')}`: `{f.get('value')}`")

                    with st.expander("Ver JSON completo del ticket"):
                        st.json(t)

                    # Guardar URL correcta
                    st.session_state.sdp_portal    = portal_input
                    st.session_state.sdp_app_name  = app_name_input.strip() or "itdesk"
                    st.session_state.access_token  = token_input
                    st.session_state.use_demo      = False
                    st.success("✅ Configuración guardada. Ve al dashboard — usa el sidebar.")
            except Exception as e:
                st.error(f"Error leyendo ticket: {e}")

    # ── GUÍA DE SOLUCIÓN ──
    st.markdown("---")
    st.markdown("### 🛠️ Solución de problemas comunes")

    with st.expander("❌ HTTP 401 — Token expirado"):
        st.markdown("""
        El `access_token` de Zoho dura **1 hora**. Para renovarlo:

        **Opción A — Zoho Developer Console (manual):**
        1. Ve a [api-console.zoho.com](https://api-console.zoho.com)
        2. Selecciona tu aplicación
        3. Ve a **Try API** o **OAuth Playground**
        4. Usa el `refresh_token` para obtener un nuevo `access_token`

        **Opción B — cURL:**
        ```bash
        curl -X POST https://accounts.zoho.com/oauth/v2/token \\
          -d "grant_type=refresh_token" \\
          -d "client_id=TU_CLIENT_ID" \\
          -d "client_secret=TU_CLIENT_SECRET" \\
          -d "refresh_token=1000.159e561771bacfd8c4d32875dbcfe502.ec64bf5f2696f3b7602fa9e73197a664"
        ```
        """)

    with st.expander("❌ HTTP 404 — URL del portal incorrecta"):
        st.markdown("""
        La URL del portal tiene este formato para SDP On-Demand:
        ```
        https://sdpondemand.manageengine.com/app/{PORTAL_NAME}/api/v3/requests
        ```
        Tu `PORTAL_NAME` es el nombre único de tu organización en ManageEngine.
        
        **¿Cómo encontrarlo?**
        - Abre SDP en el navegador
        - La URL dice: `https://sdpondemand.manageengine.com/app/`**`kashio`**`/...`
        - Ese `kashio` es tu portal name
        """)

    with st.expander("❌ HTTP 403 — Sin permisos"):
        st.markdown("""
        El scope del token debe incluir `SDPOnDemand.requests.READ`.
        Verifica en Zoho Developer Console que tu aplicación OAuth tiene ese scope habilitado.
        """)

    with st.expander("🔑 ¿Dónde están los campos UDF en mi SDP?"):
        st.markdown("""
        Los campos adicionales (empresa, región, etc.) pueden aparecer de dos formas en la respuesta JSON:
        
        **Forma 1 — udf_fields:**
        ```json
        "udf_fields": {
          "udf_sline_1": "Empresa Alpha",
          "udf_sline_2": "Corporativa"
        }
        ```
        
        **Forma 2 — additional_fields:**
        ```json
        "additional_fields": [
          {"label": "Empresa", "value": "Empresa Alpha"},
          {"label": "Región",  "value": "Norte"}
        ]
        ```
        
        El diagnóstico de arriba te muestra exactamente qué formato usa tu SDP.
        Luego ajustamos el parser en `app.py`.
        """)
