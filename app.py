# -*- coding: utf-8 -*-
"""
Dashboard d'analyse de la maintenance aéronautique — Air France
Auteur : généré avec Claude
"""
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from utils import auth, charts, icons
from utils.data_cleaning import clean_data, load_raw_data

APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "assets" / "air_france_logo.jpg"
DATA_PATH = APP_DIR / "dataset.csv"

st.set_page_config(
    page_title="Air France · Maintenance Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME / CSS
# ----------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        :root {
            --af-blue-dark: #002157;
            --af-blue: #0c3577;
            --af-red: #ee2932;
            --af-bg: #f4f6fb;
            --af-card: #ffffff;
        }

        .stApp { background: var(--af-bg); }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--af-blue-dark) 0%, var(--af-blue) 100%);
        }
        section[data-testid="stSidebar"] * { color: #eef2fb !important; }
        section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] input {
            background-color: rgba(255,255,255,0.08) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15); }

        .af-header {
            display:flex; align-items:center; justify-content:space-between;
            background: var(--af-card);
            border-radius: 16px;
            padding: 18px 28px;
            margin-bottom: 22px;
            box-shadow: 0 2px 14px rgba(12,53,119,0.08);
            border-bottom: 3px solid var(--af-red);
        }
        .af-header-title { font-size: 1.5rem; font-weight: 800; color: var(--af-blue-dark); margin:0; }
        .af-header-subtitle { font-size: 0.85rem; color: #5b6b8c; margin:0; font-weight:500; }
        .af-header-user { text-align:right; font-size:0.85rem; color:#5b6b8c; }
        .af-header-user b { color: var(--af-blue-dark); }

        .af-card {
            background: var(--af-card);
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 2px 10px rgba(12,53,119,0.07);
            border-left: 4px solid var(--af-blue);
            height: 100%;
        }
        .af-card.accent-red { border-left-color: var(--af-red); }
        .af-kpi-label { font-size:0.78rem; text-transform:uppercase; letter-spacing:0.04em; color:#7183a6; font-weight:600; margin:0 0 6px 0;}
        .af-kpi-value { font-size:1.65rem; font-weight:800; color: var(--af-blue-dark); margin:0; }
        .af-kpi-row { display:flex; align-items:center; gap:10px; }

        .af-section-title {
            font-size:1.05rem; font-weight:700; color: var(--af-blue-dark);
            margin: 6px 0 14px 0; display:flex; align-items:center; gap:8px;
        }

        div[data-testid="stTabs"] button[role="tab"] { font-weight:600; color:#5b6b8c; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--af-blue-dark) !important; border-bottom-color: var(--af-red) !important; }

        .af-login-wrapper { max-width: 420px; margin: 6vh auto 0 auto; }
        .af-login-card {
            background: var(--af-card); border-radius: 18px; padding: 36px 34px 28px 34px;
            box-shadow: 0 10px 40px rgba(0,33,87,0.15); border-top: 4px solid var(--af-red);
            text-align:center;
        }
        .af-login-title { font-size:1.3rem; font-weight:800; color: var(--af-blue-dark); margin:14px 0 2px 0; }
        .af-login-subtitle { font-size:0.85rem; color:#7183a6; margin-bottom:22px; }
        .af-login-hint { font-size:0.75rem; color:#9aa7c2; margin-top:16px; }

        .stButton>button {
            background: var(--af-blue-dark); color:white; border-radius:8px; border:none;
            font-weight:600; padding:0.5rem 1.2rem; transition: background 0.2s ease;
        }
        .stButton>button:hover { background: var(--af-red); color:white; }

        footer, #MainMenu { visibility:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(icons.ICON_CSS, unsafe_allow_html=True)


def logo_base64() -> str:
    with open(LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ----------------------------------------------------------------------------
# DONNÉES
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_clean_data():
    raw = load_raw_data(str(DATA_PATH))
    cleaned, report = clean_data(raw)
    return cleaned, report


# ----------------------------------------------------------------------------
# PAGE DE LOGIN
# ----------------------------------------------------------------------------
def render_login() -> None:
    inject_css()
    logo_b64 = logo_base64()
    st.markdown(
        f"""
        <div class="af-login-wrapper">
          <div class="af-login-card">
            <img src="data:image/jpeg;base64,{logo_b64}" width="150" />
            <div style="margin-top:10px;">{icons.icon_login(42)}</div>
            <div class="af-login-title">Maintenance Analytics</div>
            <div class="af-login-subtitle">Connectez-vous pour accéder au tableau de bord</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Identifiant", placeholder="admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter", use_container_width=True)

        if submitted:
            if auth.login(username, password):
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

        st.markdown(
            '<div class="af-login-hint" style="text-align:center;">'
            "Démo : admin / airfrance2025 · technicien / maintenance</div>",
            unsafe_allow_html=True,
        )


# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
def render_header() -> None:
    logo_b64 = logo_base64()
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(
            f"""
            <div class="af-header">
              <div style="display:flex; align-items:center; gap:18px;">
                <img src="data:image/jpeg;base64,{logo_b64}" height="42" />
                <div>
                  <p class="af-header-title">Maintenance Analytics</p>
                  <p class="af-header-subtitle">Suivi des opérations de maintenance — Flotte Air France</p>
                </div>
              </div>
              <div class="af-header-user">Connecté en tant que<br/><b>{st.session_state.display_name}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.write("")
        if st.button("Déconnexion", use_container_width=True):
            auth.logout()
            st.rerun()


# ----------------------------------------------------------------------------
# SIDEBAR — FILTRES
# ----------------------------------------------------------------------------
def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        f'{icons.icon_gauge(24)}<span style="font-weight:700;font-size:1.05rem;">Filtres</span></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Période", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )

    def multi(label, col):
        options = sorted(df[col].dropna().unique().tolist())
        return st.sidebar.multiselect(label, options, default=[])

    types_avion = multi("Type d'avion", "type_avion")
    composants = multi("Composant", "composant")
    types_maint = multi("Type de maintenance", "type_maintenance")
    techniciens = multi("Technicien", "technicien")
    statuts = multi("Statut", "statut")

    st.sidebar.markdown("---")
    if st.sidebar.button("Réinitialiser les filtres", use_container_width=True):
        st.rerun()

    out = df.copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        out = out[(out["date"].dt.date >= start) & (out["date"].dt.date <= end)]
    if types_avion:
        out = out[out["type_avion"].isin(types_avion)]
    if composants:
        out = out[out["composant"].isin(composants)]
    if types_maint:
        out = out[out["type_maintenance"].isin(types_maint)]
    if techniciens:
        out = out[out["technicien"].isin(techniciens)]
    if statuts:
        out = out[out["statut"].isin(statuts)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{len(out)} intervention(s) sélectionnée(s) sur {len(df)}")
    return out


# ----------------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------------
def kpi_card(label: str, value: str, icon_svg: str, accent: bool = False) -> str:
    accent_cls = "accent-red" if accent else ""
    return f"""
    <div class="af-card {accent_cls}">
      <div class="af-kpi-row">{icon_svg}<p class="af-kpi-label">{label}</p></div>
      <p class="af-kpi-value">{value}</p>
    </div>
    """


def render_kpis(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Aucune donnée pour les filtres sélectionnés.")
        return

    cout_total = df["cout"].sum()
    duree_moy = df["duree_heures"].mean()
    n_total = len(df)
    n_corrective = (df["type_maintenance"] == "Corrective").sum()
    n_preventive = (df["type_maintenance"] == "Preventive").sum()
    ratio = (n_corrective / n_preventive) if n_preventive else 0
    cout_moy_composant = df.groupby("composant")["cout"].mean().mean()
    taux_conformite = (df["statut"] == "Termine").mean() * 100

    cols = st.columns(6)
    values = [
        ("Coût total", f"{cout_total:,.0f} €".replace(",", " "), icons.icon_euro()),
        ("Durée moyenne", f"{duree_moy:.1f} h", icons.icon_clock()),
        ("Interventions", f"{n_total:,}".replace(",", " "), icons.icon_wrench()),
        ("Corrective / Préventive", f"{ratio:.2f}", icons.icon_gauge()),
        ("Coût moyen / composant", f"{cout_moy_composant:,.0f} €".replace(",", " "), icons.icon_plane()),
        ("Taux de conformité", f"{taux_conformite:.0f} %", icons.icon_check()),
    ]
    for col, (label, value, icon_svg) in zip(cols, values):
        with col:
            st.markdown(kpi_card(label, value, icon_svg, accent=(label == "Taux de conformité")), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# ONGLETS DE CONTENU
# ----------------------------------------------------------------------------
def render_overview_tab(df: pd.DataFrame) -> None:
    render_kpis(df)
    st.markdown("<br/>", unsafe_allow_html=True)
    if df.empty:
        return
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.plotly_chart(charts.cost_over_time(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.maintenance_type_distribution(df), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(charts.status_breakdown(df), use_container_width=True)
    with c4:
        st.plotly_chart(charts.cost_by_aircraft(df), use_container_width=True)


def render_visualisations_tab(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Aucune donnée pour les filtres sélectionnés.")
        return
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(charts.interventions_by_component(df), use_container_width=True)
    with c2:
        st.pyplot(charts.avg_duration_by_type(df), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.pyplot(charts.top_technicians(df), use_container_width=True)
    with c4:
        st.pyplot(charts.heatmap_component_month(df), use_container_width=True)


def render_data_tab(df: pd.DataFrame, report: dict) -> None:
    st.markdown(
        f'<div class="af-section-title">{icons.icon_check(20)} Rapport de nettoyage des données</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Lignes brutes", report["rows_before"])
    c2.metric("Doublons supprimés", report["duplicates_removed"])
    c3.metric("Outliers plafonnés", report["outliers_capped"])
    with st.expander("Détail des étapes de nettoyage"):
        for step in report["steps"]:
            st.write(f"• {step}")

    st.markdown(
        f'<div class="af-section-title" style="margin-top:20px;">{icons.icon_wrench(20)} Données filtrées</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(df, use_container_width=True, height=420)
    st.download_button(
        "Exporter en CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="maintenance_air_france_filtre.csv",
        mime="text/csv",
    )


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main() -> None:
    auth.init_session_state()

    if not auth.is_authenticated():
        render_login()
        return

    inject_css()
    render_header()

    df_clean, report = get_clean_data()
    df_filtered = render_filters(df_clean)

    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Visualisations", "Données & Qualité"])
    with tab1:
        render_overview_tab(df_filtered)
    with tab2:
        render_visualisations_tab(df_filtered)
    with tab3:
        render_data_tab(df_filtered, report)


if __name__ == "__main__":
    main()
