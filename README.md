# KashIO Support Dashboard — Streamlit

Dashboard supervisor de soporte basado en ServiceDesk Plus.

## 🚀 Despliegue en Streamlit Cloud

### Paso 1: Repositorio GitHub
```
kashio-dashboard/
├── app.py
├── requirements.txt
└── .streamlit/
    └── secrets.toml   ← (no commitear, usar Secrets en Streamlit Cloud)
```

### Paso 2: Secrets en Streamlit Cloud
En tu app de Streamlit Cloud, ve a **Settings → Secrets** y agrega:
```toml
SDP_URL = "https://tuinstancia.sdpondemand.com"
SDP_KEY = "tu_technician_key_aqui"
```

### Paso 3: Activar secrets en app.py
Si usas secrets de Streamlit Cloud, reemplaza la inicialización:
```python
# En session_state init, agrega:
if not st.session_state.sdp_url:
    st.session_state.sdp_url = st.secrets.get("SDP_URL", "")
if not st.session_state.sdp_key:
    st.session_state.sdp_key = st.secrets.get("SDP_KEY", "")
```

## 📊 Páginas del Dashboard

| Página | Descripción |
|--------|-------------|
| 📊 Informe General | KPIs globales, tendencias, por empresa/región/tipo |
| ⚡ SLA 1ra Respuesta | Cumplimiento SLA de primera respuesta |
| ✅ SLA Resolución | Cumplimiento SLA de resolución final |
| 👥 Grupo Resolutor | Desempeño de técnicos y grupos |
| ⭐ Encuestas CSAT | Satisfacción del usuario (4 dimensiones) |
| 🚨 Alertas | Tickets críticos y vencidos en tiempo real |
| ⚙️ Configuración | Setup de la API de SDP |

## 🔑 Medidas calculadas (equivalentes DAX)
- Total Tickets, Cerrados, Pendientes
- % Cerrados mismo día
- SLA Resolución % / SLA 1ra Respuesta %
- Tiempo promedio resolución (hrs)
- CSAT Global, Atención, Rapidez, Solución
- Tickets críticos abiertos / >48h sin resolver

## 🔧 Campos UDF personalizados
Edita `_parse_requests()` en `app.py` si tus campos UDF tienen nombres distintos.
