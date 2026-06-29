"""
JN Resolusi — KPM / Jemaah Nazir Government Portal Design System
Modern · Professional · Sleek · Live Government Concept
"""
from pathlib import Path
import streamlit as st

# Logo paths (relative to workspace root)
_WS_ROOT = Path(__file__).parent.parent
LOGO_DARK  = str(_WS_ROOT / "KPMJN-Hitam.png")   # black text logo → light backgrounds
LOGO_LIGHT = str(_WS_ROOT / "KPMJN-Putih.png")   # white text logo → dark backgrounds

# ═══════════════════════════════════════════════════════════════════
# KPM GOVERNMENT COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════
PRIMARY       = "#003399"   # Malaysian gov blue
PRIMARY_DARK  = "#002266"
PRIMARY_LIGHT = "#E8EEF9"
SIDEBAR_BG    = "#0A1628"   # deep navy
STEEL_BLUE    = "#2B5278"   # branding accent (replaces crimson for non-danger)
BG            = "#F0F2F6"
CARD_BG       = "#FFFFFF"
TEXT          = "#1A1A1A"
TEXT_SEC      = "#5F6368"
TEXT_MUTED    = "#9AA0A6"
BORDER        = "#DADCE0"
SUCCESS       = "#1E8E3E"
WARNING       = "#F9AB00"
DANGER        = "#D93025"
CRIMSON       = "#C41E3A"   # danger ONLY — never branding
ACCENT        = "#174EA6"

DI_COLORS_CSS = {
    "EXTREME DISCREPANCY":  "#C41E3A",
    "SEVERE DISCREPANCY":   "#E65100",
    "MODERATE DISCREPANCY": "#F9AB00",
    "MINOR DISCREPANCY":    "#2B5278",
    "DATA ALIGNED":         "#1E8E3E",
}

DI_ICONS = {
    "EXTREME DISCREPANCY": "🔴",
    "SEVERE DISCREPANCY":  "🟠",
    "MODERATE DISCREPANCY": "🟡",
    "MINOR DISCREPANCY":   "🔵",
    "DATA ALIGNED":        "🟢",
}


def inject_css():
    """Inject global CSS — clean Malaysian government portal standard."""
    st.markdown(f"""
    <style>
    /* ═══════════════════════════════════════════════════════════════
       JN RESOLUSI — KPM/JN Government Portal Design System
       Font: Inter · Clean · Professional · Accessible
    ═══════════════════════════════════════════════════════════════ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], button, input, select, textarea,
    .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, li, span, div {{
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    }}

    /* ── Base background ────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] {{
        background: {BG} !important;
        background-image: none !important;
    }}
    [data-testid="stAppViewContainer"] > .main {{ background: transparent !important; }}
    .main .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1280px !important;
    }}

    /* ── SIDEBAR — Solid dark navy ──────────────────────────────── */
    section[data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, {SIDEBAR_BG} 0%, #0F1F3D 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #E8EAED !important;
    }}
    /* Active nav — steel blue, not crimson */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] label[data-selected="true"],
    section[data-testid="stSidebar"] .stRadio label[data-selected="true"] {{
        background: {STEEL_BLUE}22 !important;
        border-left: 3px solid {STEEL_BLUE} !important;
        border-radius: 0 8px 8px 0 !important;
    }}
    section[data-testid="stSidebar"] button:hover {{
        background: rgba(255,255,255,0.08) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        color: #FFFFFF !important;
    }}

    /* ── HEADERS ────────────────────────────────────────────────── */
    h1 {{ font-size: 1.8rem !important; font-weight: 700 !important; color: {PRIMARY_DARK} !important; letter-spacing: -0.02em !important; }}
    h2 {{ font-size: 1.4rem !important; font-weight: 600 !important; color: {TEXT} !important; }}
    h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; color: {TEXT} !important; }}

    /* ── STAT CARDS — Elevated glassmorphism ─────────────────────── */
    .jn-stat-card {{
        background: {CARD_BG} !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06) !important;
        border: 1px solid {BORDER} !important;
        transition: box-shadow 0.2s ease, transform 0.15s ease !important;
    }}
    .jn-stat-card:hover {{
        box-shadow: 0 8px 24px rgba(0,51,153,0.08), 0 2px 8px rgba(0,0,0,0.06) !important;
        transform: translateY(-2px) !important;
    }}
    .jn-stat-label {{
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: {TEXT_SEC} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        margin-bottom: 0.25rem !important;
    }}
    .jn-stat-value {{
        font-size: 2.0rem !important;
        font-weight: 700 !important;
        color: {PRIMARY} !important;
        line-height: 1.2 !important;
    }}
    .jn-stat-sub {{
        font-size: 0.8rem !important;
        color: {TEXT_MUTED} !important;
        margin-top: 0.25rem !important;
    }}

    /* ── CONTENT CARDS ──────────────────────────────────────────── */
    .jn-card {{
        background: {CARD_BG} !important;
        border-radius: 16px !important;
        padding: 1.75rem !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06) !important;
        border: 1px solid {BORDER} !important;
        margin-bottom: 1.25rem !important;
    }}
    .jn-card-header {{
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: {PRIMARY_DARK} !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 2px solid {PRIMARY_LIGHT} !important;
    }}

    /* ── DI BADGES ──────────────────────────────────────────────── */
    .jn-badge {{
        display: inline-block !important;
        padding: 0.35rem 0.85rem !important;
        border-radius: 20px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }}
    .jn-badge-extreme  {{ background: #FDE8EC !important; color: {CRIMSON} !important; }}
    .jn-badge-severe   {{ background: #FFF3E0 !important; color: #E65100 !important; }}
    .jn-badge-moderate {{ background: #FFF8E1 !important; color: #B45309 !important; }}
    .jn-badge-minor    {{ background: #E8EEF9 !important; color: {STEEL_BLUE} !important; }}
    .jn-badge-aligned  {{ background: #E6F4EA !important; color: #1E8E3E !important; }}

    /* ── BUTTONS ────────────────────────────────────────────────── */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 0.55rem 1.5rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {PRIMARY} !important;
        color: #FFFFFF !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: {PRIMARY_DARK} !important;
        box-shadow: 0 4px 12px rgba(0,51,153,0.3) !important;
    }}

    /* ── FILE UPLOADER — fix double "upload" text ───────────────── */
    [data-testid="stFileUploader"] button span {{
        display: none !important;
    }}
    section[data-testid="stFileUploadDropzone"] {{
        border-radius: 12px !important;
        border: 2px dashed {BORDER} !important;
        padding: 1.5rem !important;
    }}
    section[data-testid="stFileUploadDropzone"]:hover {{
        border-color: {PRIMARY} !important;
    }}

    /* ── TABLES ──────────────────────────────────────────────────── */
    .jn-table {{
        width: 100% !important;
        border-collapse: collapse !important;
        background: {CARD_BG} !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    }}
    .jn-table th {{
        background: {PRIMARY_LIGHT} !important;
        color: {PRIMARY_DARK} !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
        padding: 0.75rem 1rem !important;
    }}
    .jn-table td {{
        padding: 0.65rem 1rem !important;
        border-bottom: 1px solid {BORDER} !important;
        font-size: 0.88rem !important;
    }}
    .jn-table tr:hover td {{
        background: #F8FAFD !important;
    }}

    /* ── METRICS ROW ────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: {CARD_BG} !important;
        border-radius: 14px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
        border: 1px solid {BORDER} !important;
    }}

    /* ── FORM INPUTS ────────────────────────────────────────────── */
    input, textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] {{
        border-radius: 10px !important;
        border: 1.5px solid {BORDER} !important;
        transition: border-color 0.2s ease !important;
    }}
    input:focus, textarea:focus {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 3px rgba(0,51,153,0.10) !important;
    }}

    /* ── RISK SIGNAL BAR ────────────────────────────────────────── */
    .jn-risk-bar {{
        background: {CARD_BG} !important;
        border-radius: 14px !important;
        padding: 1rem 1.5rem !important;
        margin-bottom: 1.25rem !important;
        border: 1px solid {BORDER} !important;
        display: flex !important;
        align-items: center !important;
        gap: 1.25rem !important;
    }}
    .jn-risk-bar.alert-high {{
        border-left: 4px solid {CRIMSON} !important;
        background: #FFF5F5 !important;
    }}
    .jn-risk-bar.alert-mid {{
        border-left: 4px solid {WARNING} !important;
        background: #FFFCF5 !important;
    }}
    .jn-risk-bar.alert-low {{
        border-left: 4px solid {SUCCESS} !important;
        background: #F5FFF7 !important;
    }}
    .jn-risk-gauge {{
        font-size: 2rem !important;
        font-weight: 800 !important;
        min-width: 60px !important;
    }}
    .jn-risk-info {{
        flex: 1 !important;
    }}
    .jn-risk-info .label {{
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}
    .jn-risk-info .summary {{
        font-size: 0.85rem !important;
        color: {TEXT_SEC} !important;
    }}
    .jn-risk-breakdown {{
        display: flex !important;
        gap: 0.75rem !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }}

    /* ── DI MINIBAR (case log) ──────────────────────────────────── */
    .jn-di-minibar {{
        width: 80px !important;
        height: 6px !important;
        border-radius: 3px !important;
        background: #E8EAED !important;
        overflow: hidden !important;
        display: inline-block !important;
        vertical-align: middle !important;
        margin-right: 0.5rem !important;
    }}
    .jn-di-minibar-fill {{
        height: 100% !important;
        border-radius: 3px !important;
        transition: width 0.3s ease !important;
    }}

    /* ── FILTER CHIPS ───────────────────────────────────────────── */
    .jn-filter-chips {{
        display: flex !important;
        gap: 0.5rem !important;
        flex-wrap: wrap !important;
        margin-bottom: 1rem !important;
    }}
    .jn-chip {{
        padding: 0.35rem 0.85rem !important;
        border-radius: 20px !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        border: 1.5px solid {BORDER} !important;
        background: {CARD_BG} !important;
        color: {TEXT_SEC} !important;
        transition: all 0.15s ease !important;
    }}
    .jn-chip:hover {{
        border-color: {STEEL_BLUE} !important;
        color: {STEEL_BLUE} !important;
    }}
    .jn-chip.active {{
        background: {STEEL_BLUE} !important;
        color: #FFFFFF !important;
        border-color: {STEEL_BLUE} !important;
    }}

    /* ── EMPTY STATES — purposeful icons, no emoji ──────────────── */
    .jn-empty-state {{
        text-align: center !important;
        padding: 3rem 1.5rem !important;
        color: {TEXT_MUTED} !important;
    }}
    .jn-empty-state .jn-empty-icon {{
        font-size: 2.5rem !important;
        margin-bottom: 0.75rem !important;
        opacity: 0.5 !important;
    }}
    .jn-empty-state .jn-empty-text {{
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: {TEXT_SEC} !important;
    }}

    /* ── SIDEBAR LOGO ───────────────────────────────────────────── */
    .jn-sidebar-logo {{
        text-align: center !important;
        padding: 0.5rem 0 1rem 0 !important;
    }}
    .jn-sidebar-logo img {{
        max-width: 180px !important;
        height: auto !important;
    }}

    /* ── ALERT BOX ──────────────────────────────────────────────── */
    .jn-alert {{
        border-left: 4px solid {PRIMARY} !important;
        background: {PRIMARY_LIGHT} !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
        margin: 1rem 0 !important;
    }}
    .jn-alert-danger  {{ border-left-color: {DANGER} !important; background: #FDECEC !important; }}
    .jn-alert-success {{ border-left-color: {SUCCESS} !important; background: #E6F4EA !important; }}
    .jn-alert-warning {{ border-left-color: {WARNING} !important; background: #FFF8E1 !important; }}

    /* ── APP HEADER BAR ─────────────────────────────────────────── */
    .jn-header-bar {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 1rem 0 !important;
        border-bottom: 2px solid {BORDER} !important;
        margin-bottom: 1.5rem !important;
    }}
    .jn-header-title {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: {PRIMARY_DARK} !important;
    }}
    .jn-header-sub {{
        font-size: 0.85rem !important;
        color: {TEXT_SEC} !important;
        font-weight: 400 !important;
    }}

    /* ── RESPONSIVE ─────────────────────────────────────────────── */
    @media (max-width: 768px) {{
        .jn-stat-card {{ padding: 1rem !important; }}
        .jn-stat-value {{ font-size: 1.5rem !important; }}
        .main .block-container {{ padding: 0.5rem !important; }}
    }}

    /* ── HIDE STREAMLIT BRANDING ───────────────────────────────── */
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    </style>
    """, unsafe_allow_html=True)


def get_logo_for_theme():
    """Return appropriate logo path based on dark/light context."""
    return LOGO_LIGHT  # default for sidebar (dark bg)


def render_sidebar_header():
    """Render KPMJN logo + title in sidebar."""
    import base64
    logo_path = get_logo_for_theme()
    try:
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="jn-sidebar-logo">
            <img src="data:image/png;base64,{data}" alt="KPM Jemaah Nazir">
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("### 🛡️ JN RESOLUSI")


def render_sidebar_footer():
    """Render sidebar footer with version info."""
    st.markdown("""
    <div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid rgba(255,255,255,0.1);font-size:0.7rem;color:#9AA0A6;">
    JN Resolusi v2.0 · PRESTIJ-25<br>
    © 2025 KPM Jemaah Nazir
    </div>
    """, unsafe_allow_html=True)


def stat_card(label: str, value, sub: str = "", color: str = None):
    """Render a single stat card."""
    c = color or PRIMARY
    st.markdown(f"""
    <div class="jn-stat-card">
        <div class="jn-stat-label">{label}</div>
        <div class="jn-stat-value" style="color:{c}">{value}</div>
        <div class="jn-stat-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def di_badge(classification: str):
    """Render a DI classification badge with severity icon."""
    mapping = {
        "EXTREME DISCREPANCY": "extreme",
        "SEVERE DISCREPANCY": "severe",
        "MODERATE DISCREPANCY": "moderate",
        "MINOR DISCREPANCY": "minor",
        "DATA ALIGNED": "aligned",
    }
    icons = {
        "EXTREME DISCREPANCY": "🔴",
        "SEVERE DISCREPANCY": "🟠",
        "MODERATE DISCREPANCY": "🟡",
        "MINOR DISCREPANCY": "🔵",
        "DATA ALIGNED": "🟢",
    }
    cls = mapping.get(classification, "aligned")
    icon = icons.get(classification, "⚪")
    st.markdown(f'<span class="jn-badge jn-badge-{cls}">{icon} {classification}</span>', unsafe_allow_html=True)


def alert_box(text: str, kind: str = "info"):
    """Render an alert box."""
    cls_map = {"info": "", "danger": " jn-alert-danger", "success": " jn-alert-success", "warning": " jn-alert-warning"}
    st.markdown(f'<div class="jn-alert{cls_map.get(kind, "")}">{text}</div>', unsafe_allow_html=True)
