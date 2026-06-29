"""
JN Resolusi — Smart Cross-Reference & Audit Engine (Streamlit Edition)
MoE Agentic AI — PRESTIJ Programme 2025
Neon PostgreSQL + Streamlit Cloud
"""
import os
import io
import uuid
import json
import base64
from datetime import datetime, timezone, timedelta
from typing import Optional

import streamlit as st
import pandas as pd
from passlib.context import CryptContext
from jose import jwt, JWTError

from agents import run_agent_a, run_agent_b, run_agent_c
from database import JNDatabase
from styles import (
    inject_css, LOGO_DARK, LOGO_LIGHT,
    stat_card, di_badge, alert_box, render_sidebar_header, render_sidebar_footer,
    PRIMARY, PRIMARY_DARK, SUCCESS, WARNING, DANGER, DI_COLORS_CSS,
)

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JN Resolusi — Sistem Audit Pintar MOE",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
JWT_SECRET = os.environ.get("JWT_SECRET", "jnresolusi-dev-secret-2025-changeme")
JWT_ALGO = "HS256"
JWT_EXPIRE_HOURS = 24
ALLOWED_DOMAINS = {"@moe.gov.my", "@moe-dl.edu.my"}
DEFAULT_ADMIN_EMAIL = "admin@moe.gov.my"
DEFAULT_ADMIN_PASSWORD = "admin1234"

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

DI_COLORS = {
    "EXTREME DISCREPANCY": "#C62828",
    "SEVERE DISCREPANCY": "#E65100",
    "MODERATE DISCREPANCY": "#F9AB00",
    "MINOR DISCREPANCY": "#003399",
    "DATA ALIGNED": "#1E8E3E",
}

ROLE_LABELS = {
    "admin": "Pentadbir",
    "penyelaras_jn": "Penyelaras JN",
    "peneraju_sektor": "Peneraju Sektor",
}

# ═══════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════
inject_css()

# Persist DB across reruns
@st.cache_resource
def _get_db() -> JNDatabase:
    db = JNDatabase()
    db.init_schema()
    db.seed_audit_records()
    db.seed_admin_user()
    return db

db = _get_db()

# ═══════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════════

def _create_token(email: str, role: str) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": email, "role": role, "exp": expire},
        JWT_SECRET, algorithm=JWT_ALGO,
    )

def _decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        return None

def _is_authenticated() -> bool:
    return "jwt_token" in st.session_state

def _get_user() -> dict:
    token = st.session_state.get("jwt_token", "")
    payload = _decode_token(token)
    return payload or {}

def _require_auth():
    if not _is_authenticated():
        st.stop()

def _role_can_write(role: str) -> bool:
    return role in ("admin", "penyelaras_jn")

def _role_is_admin(role: str) -> bool:
    return role == "admin"


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        render_sidebar_header()

        if _is_authenticated():
            user = _get_user()
            email = user.get("sub", "?")
            role = user.get("role", "?")

            st.markdown(f"""
            <div style="text-align:center;padding:0.5rem 0;margin-top:0.5rem;">
                <div style="font-size:0.85rem;font-weight:600;color:#FFFFFF;">{email}</div>
                <div style="margin-top:0.3rem;">
                    <span style="background:{PRIMARY};color:#FFF;padding:0.2rem 0.7rem;
                    border-radius:12px;font-size:0.7rem;font-weight:600;">
                        {ROLE_LABELS.get(role, role)}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Navigation — radio for stable sidebar (no collapse)
            page_options = {
                "📊  Dashboard": "Dashboard",
                "📤  Hantar Payload": "Hantar Payload",
                "📋  Log Kes": "Log Kes",
                "📄  Ringkasan Eksekutif": "Ringkasan Eksekutif",
                "📁  Muat Naik CSV": "Muat Naik CSV",
            }
            if _role_is_admin(role):
                page_options["👥  Pengurusan Pengguna"] = "Pengurusan Pengguna"
            page_options["ℹ️  Maklumat Sistem"] = "Maklumat Sistem"

            current_page = st.session_state.get("page", "Dashboard")
            labels = list(page_options.keys())
            values = list(page_options.values())
            default_idx = values.index(current_page) if current_page in values else 0
            selected = st.sidebar.radio(
                "Navigasi", labels,
                index=default_idx,
                key="nav_radio",
                label_visibility="collapsed",
            )
            st.session_state["page"] = page_options[selected]

            st.divider()

            if st.sidebar.button("🚪  Log Keluar", use_container_width=True, type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

            render_sidebar_footer()
        else:
            st.session_state["page"] = "Log Masuk"


# ═══════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════

def page_login():
    st.markdown("""
    <div style="max-width:440px;margin:3rem auto;">
    """, unsafe_allow_html=True)

    # Logo centered
    try:
        with open(LOGO_DARK, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <img src="data:image/png;base64,{logo_b64}" style="max-width:220px;" alt="KPM JN">
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem;">
        <h1 style="font-size:1.5rem;font-weight:700;color:#003399;margin:0;">JN RESOLUSI</h1>
        <p style="color:#5F6368;font-size:0.9rem;">Sistem Audit Pintar KPM · Jemaah Nazir</p>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Emel", placeholder="nama@moe.gov.my", key="login_email")
    password = st.text_input("Kata Laluan", type="password", key="login_password")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐  Log Masuk", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Sila isi emel dan kata laluan.")
            else:
                domain = "@" + email.split("@")[-1] if "@" in email else ""
                if domain not in ALLOWED_DOMAINS:
                    st.error(f"⚠️ Hanya emel {', '.join(ALLOWED_DOMAINS)} dibenarkan.")
                else:
                    user = db.get_user_by_email(email)
                    if user and pwd_context.verify(password, user["password_hash"]):
                        token = _create_token(email, user["role"])
                        st.session_state["jwt_token"] = token
                        st.session_state["page"] = "Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Emel atau kata laluan tidak sah.")

    st.markdown("""
    <div style="text-align:center;margin-top:1.5rem;font-size:0.75rem;color:#9AA0A6;">
    PRESTIJ-25 · MoE Agentic AI<br>
    Hanya pegawai KPM dibenarkan akses
    </div>
    </div>
    """, unsafe_allow_html=True)


def page_dashboard():
    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">📊 Dashboard</span><br><span class="jn-header-sub">JN Resolusi · Pemantauan Audit Nasional</span></div></div>', unsafe_allow_html=True)

    case_count = db.get_case_count()
    avg_di = db.get_avg_di()
    di_summary = db.get_di_summary()

    # Stat cards row
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        with st.container():
            stat_card("Jumlah Kes", str(case_count), "kes direkodkan", PRIMARY)
    with col2:
        with st.container():
            stat_card("Purata DI", f"{avg_di:.4f}", "Discrepancy Index", WARNING)
    with col3:
        with st.container():
            extreme = di_summary.get("EXTREME DISCREPANCY", 0)
            stat_card("Kritikal", str(extreme), "kes EXTREME", DANGER)
    with col4:
        with st.container():
            aligned = di_summary.get("DATA ALIGNED", 0)
            stat_card("Selaras", str(aligned), "kes aligned", SUCCESS)

    st.markdown("<br>", unsafe_allow_html=True)

    # DI Distribution
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown('<div class="jn-card"><div class="jn-card-header">📈 Taburan Discrepancy Index</div>', unsafe_allow_html=True)
        if di_summary:
            import plotly.express as px
            labels = list(di_summary.keys())
            values = list(di_summary.values())
            colors = [DI_COLORS.get(l, "#999") for l in labels]
            fig = px.bar(x=labels, y=values, color=labels,
                         color_discrete_sequence=colors,
                         labels={"x": "", "y": "Bilangan Kes"})
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10), height=350,
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Tiada data kes setakat ini.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="jn-card"><div class="jn-card-header">🛡️ Status Sistem</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:0.5rem;font-weight:500;">Backend DB</td><td style="color:{SUCCESS};font-weight:600;">✅ {db.backend.upper()}</td></tr>
        <tr><td style="padding:0.5rem;font-weight:500;">Agent A</td><td style="color:{SUCCESS};">✅ Online</td></tr>
        <tr><td style="padding:0.5rem;font-weight:500;">Agent B</td><td style="color:{SUCCESS};">✅ Online</td></tr>
        <tr><td style="padding:0.5rem;font-weight:500;">Agent C</td><td style="color:{SUCCESS};">✅ Online</td></tr>
        <tr><td style="padding:0.5rem;font-weight:500;">JWT Auth</td><td style="color:{SUCCESS};">✅ Aktif</td></tr>
        <tr><td style="padding:0.5rem;font-weight:500;">RBAC</td><td style="color:{SUCCESS};">✅ Aktif</td></tr>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Recent cases
    st.markdown('<div class="jn-card"><div class="jn-card-header">📋 Kes Terkini</div>', unsafe_allow_html=True)
    cases = db.get_cases(limit=10)
    if cases:
        rows = []
        for c in cases:
            rows.append({
                "Case ID": c["case_id"],
                "Sekolah": c["school_name"],
                "Negeri": c["state"],
                "DI": f"{c['discrepancy_index']:.4f}",
                "Klasifikasi": c["di_classification"],
                "Masa": c["timestamp"][:16] if c["timestamp"] else "-",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={
                         "Klasifikasi": st.column_config.TextColumn(width="medium"),
                     })
    else:
        st.info("Belum ada kes diproses.")
    st.markdown('</div>', unsafe_allow_html=True)


def page_hantar_payload():
    user = _get_user()
    if not _role_can_write(user.get("role", "")):
        st.error("⛔ Akses terhad. Hanya admin / penyelaras_jn boleh menghantar payload.")
        return

    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">📤 Hantar Payload</span><br><span class="jn-header-sub">Saluran masuk data Matrix · Agent A→B→C Pipeline</span></div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="jn-card"><div class="jn-card-header">📝 Maklumat Payload</div>', unsafe_allow_html=True)
        source_system_id = st.text_input("Source System ID *", placeholder="cth: MATRIX-001")
        source_system_name = st.text_input("Source System Name *", placeholder="cth: Aduan Awam")
        source_version = st.text_input("Source Version", placeholder="cth: 1.0")
        school_id = st.text_input("School ID *", placeholder="cth: SBP001")
        operational_score = st.slider("Skor Operasi (%)", 0.0, 100.0, 75.0, 0.5)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="jn-card"><div class="jn-card-header">📄 Teks & Dokumen</div>', unsafe_allow_html=True)
        raw_text = st.text_area("Teks Aduan / Laporan *", height=200,
                                placeholder="Masukkan teks laporan atau aduan...")
        uploaded_file = st.file_uploader("Muat naik dokumen (DOCX/PDF/TXT)",
                                         type=["txt", "docx", "pdf"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".txt"):
                    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                    st.success(f"✅ Fail TXT dibaca: {len(raw_text)} aksara")
                elif uploaded_file.name.endswith(".docx"):
                    from docx import Document as DocxDocument
                    doc = DocxDocument(uploaded_file)
                    raw_text = "\n".join([p.text for p in doc.paragraphs])
                    st.success(f"✅ Fail DOCX dibaca: {len(raw_text)} aksara")
                elif uploaded_file.name.endswith(".pdf"):
                    from pypdf import PdfReader
                    reader = PdfReader(uploaded_file)
                    raw_text = "\n".join([p.extract_text() or "" for p in reader.pages])
                    st.success(f"✅ Fail PDF dibaca: {len(raw_text)} aksara")
            except Exception as e:
                st.warning(f"⚠️ Gagal baca fail: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀  Hantar & Proses (Agent A → B → C)", use_container_width=True, type="primary"):
        if not source_system_id or not school_id or not raw_text:
            st.error("⚠️ Sila isi Source System ID, School ID, dan Teks Aduan.")
        else:
            with st.spinner("🔄 Memproses payload melalui Agent Pipeline..."):
                import time

                # Agent A — Semantic Ingestion
                agent_a = run_agent_a(school_id, raw_text, source_system_id)
                payload_id = str(uuid.uuid4())

                st.markdown("**🔍 Agent A — Semantic Ingestion** ✅")
                st.caption(f"Kategori: {agent_a['mapped_category']} | Severiti: {agent_a['severity']}")

                # Save payload
                db.insert_payload({
                    "id": payload_id,
                    "source_system_id": source_system_id,
                    "source_system_name": source_system_name,
                    "source_version": source_version,
                    "school_id": school_id,
                    "raw_text_extracted": raw_text[:5000],
                    "operational_score": operational_score,
                    "mapped_category": agent_a["mapped_category"],
                    "severity_level": agent_a["severity"],
                    "extracted_entities": json.dumps(agent_a.get("extracted_entities", []), ensure_ascii=False),
                })

                time.sleep(0.3)

                # Agent B — Discrepancy Index
                agent_b = run_agent_b(school_id, operational_score, agent_a, source_system_id)

                st.markdown(f"**📊 Agent B — Discrepancy Index** ✅ — DI: {agent_b['discrepancy_index']:.4f}")
                di_badge(agent_b["di_classification"])

                time.sleep(0.3)

                # Agent C — Executive Brief
                agent_c = run_agent_c(school_id, source_system_name, agent_a, agent_b)

                st.markdown(f"**📄 Agent C — Executive Brief** ✅")
                alert_box(f"Status: {agent_c['alert_status_label']}",
                          "danger" if "SEGERA" in agent_c['alert_status_label'] else "info")

                # Save discrepancy
                db.insert_discrepancy({
                    "id": str(uuid.uuid4()),
                    "case_id": agent_b["case_id"],
                    "school_id": school_id,
                    "school_name": agent_c["school_name"],
                    "state": agent_c["state"],
                    "source_system_name": source_system_name,
                    "audit_score_reference": agent_b["audit_data_snapshot"]["audit_score"],
                    "operational_score_reported": operational_score,
                    "score_delta": agent_b["score_delta"],
                    "discrepancy_index": agent_b["discrepancy_index"],
                    "di_classification": agent_b["di_classification"],
                    "flags": json.dumps(agent_b["flags"], ensure_ascii=False),
                    "anomaly_detected": 1 if agent_b["anomaly_detected"] else 0,
                    "confidence_score": agent_b["confidence_score"],
                    "agent_a_result": json.dumps(agent_a, ensure_ascii=False),
                    "agent_c_result": json.dumps(agent_c, ensure_ascii=False),
                    "brief_content": json.dumps(agent_c, ensure_ascii=False),
                })

                st.success(f"✅ Payload berjaya diproses! Case ID: **{agent_b['case_id']}**")
                st.balloons()

                # Show brief
                with st.expander("📄 Lihat Ringkasan Eksekutif", expanded=True):
                    st.code(agent_c["executive_directive_text"], language=None)


def page_log_kes():
    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">📋 Log Kes</span><br><span class="jn-header-sub">Semua kes diproses oleh sistem</span></div></div>', unsafe_allow_html=True)

    cases = db.get_cases(limit=200)
    if not cases:
        st.info("📭 Tiada kes direkodkan. Hantar payload untuk bermula.")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        classifications = list(set(c["di_classification"] for c in cases))
        filter_class = st.selectbox("Tapis Klasifikasi", ["Semua"] + sorted(classifications))
    with col2:
        states = list(set(c["state"] for c in cases if c["state"]))
        filter_state = st.selectbox("Tapis Negeri", ["Semua"] + sorted(states))
    with col3:
        search_term = st.text_input("Cari Sekolah / Case ID", placeholder="Taip untuk mencari...")

    filtered = cases
    if filter_class != "Semua":
        filtered = [c for c in filtered if c["di_classification"] == filter_class]
    if filter_state != "Semua":
        filtered = [c for c in filtered if c["state"] == filter_state]
    if search_term:
        q = search_term.lower()
        filtered = [c for c in filtered if q in c.get("school_name", "").lower() or q in c.get("case_id", "").lower()]

    st.caption(f"Menunjukkan {len(filtered)} / {len(cases)} kes")

    # Build dataframe for native Streamlit table
    display_data = []
    for c in filtered:
        di_val = c["discrepancy_index"] or 0
        di_class = c["di_classification"] or "DATA ALIGNED"
        display_data.append({
            "Case ID": c["case_id"],
            "Sekolah": c["school_name"],
            "Negeri": c["state"],
            "Skor Audit": f"{c['audit_score_reference']:.1f}" if c['audit_score_reference'] else "-",
            "Skor Lapor": f"{c['operational_score_reported']:.1f}" if c['operational_score_reported'] else "-",
            "Δ": f"{c['score_delta']:.1f}" if c['score_delta'] else "-",
            "DI": di_val,
            "Klasifikasi": di_class,
            "Masa": c["timestamp"][:16] if c["timestamp"] else "-",
        })

    df = pd.DataFrame(display_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "DI": st.column_config.NumberColumn("DI", format="%.4f"),
            "Klasifikasi": st.column_config.TextColumn("Klasifikasi", width="medium"),
        },
    )

    # Export
    if st.button("📥 Eksport CSV", use_container_width=False):
        export_df = pd.DataFrame([{
            "case_id": c["case_id"], "school_name": c["school_name"], "state": c["state"],
            "audit_score": c["audit_score_reference"], "operational_score": c["operational_score_reported"],
            "score_delta": c["score_delta"], "discrepancy_index": c["discrepancy_index"],
            "di_classification": c["di_classification"], "timestamp": c["timestamp"],
        } for c in filtered])
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Muat Turun CSV", csv, "jn_resolusi_cases.csv", "text/csv")


def page_ringkasan_eksekutif():
    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">📄 Ringkasan Eksekutif</span><br><span class="jn-header-sub">Laporan terperinci untuk setiap kes</span></div></div>', unsafe_allow_html=True)

    cases = db.get_cases(limit=200)
    if not cases:
        st.info("Tiada kes untuk dipapar.")
        return

    case_ids = [c["case_id"] for c in cases]
    selected = st.selectbox("Pilih Case ID", case_ids)

    if selected:
        case = db.get_case_by_id(selected)
        if case:
            di_class = case["di_classification"] or "DATA ALIGNED"
            color = DI_COLORS.get(di_class, "#999")

            st.markdown(f"""
            <div class="jn-card">
            <div class="jn-card-header" style="display:flex;justify-content:space-between;align-items:center;">
                <span>📋 {case['case_id']}</span>
                <span class="jn-badge jn-badge-{di_class.lower().replace(' ','_')[:10]}">{di_class}</span>
            </div>
            <table style="width:100%;border-collapse:collapse;font-size:0.9rem;">
            <tr><td style="padding:0.4rem;font-weight:500;width:180px;">🏫 Sekolah</td><td><strong>{case['school_name']}</strong></td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">📍 Negeri</td><td>{case['state']}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">📊 Skor Audit</td><td>{case['audit_score_reference']}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">📤 Skor Dilapor</td><td>{case['operational_score_reported']}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">Δ Delta</td><td>{case['score_delta']}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">📈 Discrepancy Index</td><td style="color:{color};font-weight:700;font-size:1.2rem;">{case['discrepancy_index']:.4f}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">🔍 Anomali</td><td>{'⚠️ YA' if case['anomaly_detected'] else '✅ TIDAK'}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">🎯 Keyakinan</td><td>{case['confidence_score']:.2%}</td></tr>
            <tr><td style="padding:0.4rem;font-weight:500;">🕐 Masa</td><td>{case['timestamp']}</td></tr>
            </table>
            </div>
            """, unsafe_allow_html=True)

            # Brief content
            try:
                brief = json.loads(case.get("brief_content", "{}"))
                if brief:
                    st.markdown("### 📄 Ringkasan Eksekutif")
                    st.code(brief.get("executive_directive_text", ""), language=None)

                    st.markdown("### ⚡ Tindakan Penguatkuasaan")
                    for a in brief.get("enforcement_actions", []):
                        st.markdown(f"- {a}")

                    st.markdown("### 💡 Syor Polisi")
                    for p in brief.get("policy_recommendations", []):
                        st.markdown(f"- {p}")
            except Exception:
                st.info("Tiada ringkasan tersedia untuk kes ini.")


def page_muat_naik_csv():
    user = _get_user()
    if not _role_can_write(user.get("role", "")):
        st.error("⛔ Akses terhad.")
        return

    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">📁 Muat Naik CSV</span><br><span class="jn-header-sub">Pemprosesan pukal (bulk) melalui fail CSV</span></div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="jn-alert">
    <strong>Format CSV:</strong> <code>source_system_id, source_system_name, school_id, raw_text, operational_score</code><br>
    Pastikan header disertakan pada baris pertama.
    </div>
    """, unsafe_allow_html=True)

    csv_file = st.file_uploader("Pilih fail CSV", type=["csv"])

    if csv_file:
        try:
            df = pd.read_csv(csv_file)
            st.markdown(f"**{len(df)} baris dikesan.**")
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)

            if st.button("🚀  Proses Semua (Batch)", use_container_width=True, type="primary"):
                progress = st.progress(0)
                status_text = st.empty()
                success_count = 0

                for idx, row in df.iterrows():
                    sid = str(row.get("source_system_id", f"CSV-{idx}"))
                    sname = str(row.get("source_system_name", "CSV Upload"))
                    school = str(row.get("school_id", "UNKNOWN"))
                    text = str(row.get("raw_text", ""))
                    score = float(row.get("operational_score", 50))

                    try:
                        agent_a = run_agent_a(school, text, sid)
                        agent_b = run_agent_b(school, score, agent_a, sid)
                        agent_c = run_agent_c(school, sname, agent_a, agent_b)

                        db.insert_payload({
                            "id": str(uuid.uuid4()), "source_system_id": sid,
                            "source_system_name": sname, "source_version": "CSV",
                            "school_id": school, "raw_text_extracted": text[:5000],
                            "operational_score": score, "mapped_category": agent_a["mapped_category"],
                            "severity_level": agent_a["severity"],
                            "extracted_entities": json.dumps(agent_a.get("extracted_entities", []), ensure_ascii=False),
                        })
                        db.insert_discrepancy({
                            "id": str(uuid.uuid4()), "case_id": agent_b["case_id"],
                            "school_id": school, "school_name": agent_c["school_name"],
                            "state": agent_c["state"], "source_system_name": sname,
                            "audit_score_reference": agent_b["audit_data_snapshot"]["audit_score"],
                            "operational_score_reported": score, "score_delta": agent_b["score_delta"],
                            "discrepancy_index": agent_b["discrepancy_index"],
                            "di_classification": agent_b["di_classification"],
                            "flags": json.dumps(agent_b["flags"], ensure_ascii=False),
                            "anomaly_detected": 1 if agent_b["anomaly_detected"] else 0,
                            "confidence_score": agent_b["confidence_score"],
                            "agent_a_result": json.dumps(agent_a, ensure_ascii=False),
                            "agent_c_result": json.dumps(agent_c, ensure_ascii=False),
                            "brief_content": json.dumps(agent_c, ensure_ascii=False),
                        })
                        success_count += 1
                    except Exception as e:
                        st.warning(f"Baris {idx} gagal: {e}")

                    progress.progress((idx + 1) / len(df))
                    status_text.text(f"Diproses: {idx + 1}/{len(df)}")

                st.success(f"✅ Selesai! {success_count}/{len(df)} baris berjaya diproses.")
                st.balloons()

        except Exception as e:
            st.error(f"❌ Gagal membaca CSV: {e}")


def page_pengurusan_pengguna():
    user = _get_user()
    if not _role_is_admin(user.get("role", "")):
        st.error("⛔ Hanya admin boleh mengakses halaman ini.")
        return

    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">👥 Pengurusan Pengguna</span><br><span class="jn-header-sub">Tambah / lihat pengguna sistem</span></div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown('<div class="jn-card"><div class="jn-card-header">➕ Tambah Pengguna</div>', unsafe_allow_html=True)
        new_email = st.text_input("Emel *", placeholder="pegawai@moe.gov.my", key="new_user_email")
        new_password = st.text_input("Kata Laluan *", type="password", key="new_user_password")
        new_role = st.selectbox("Peranan *", ["penyelaras_jn", "peneraju_sektor", "admin"],
                                format_func=lambda x: ROLE_LABELS.get(x, x))

        if st.button("✅  Tambah Pengguna", use_container_width=True, type="primary"):
            if not new_email or not new_password:
                st.error("Sila isi emel dan kata laluan.")
            else:
                domain = "@" + new_email.split("@")[-1] if "@" in new_email else ""
                if domain not in ALLOWED_DOMAINS:
                    st.error(f"⚠️ Hanya emel {', '.join(ALLOWED_DOMAINS)} dibenarkan.")
                else:
                    try:
                        h = pwd_context.hash(new_password)
                        uid = db.create_user(new_email, h, new_role)
                        st.success(f"✅ Pengguna ditambah! ID: {uid[:8]}...")
                    except Exception as e:
                        st.error(f"❌ Gagal: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="jn-card"><div class="jn-card-header">📋 Senarai Pengguna</div>', unsafe_allow_html=True)
        users = db.list_users()
        if users:
            rows = []
            for u in users:
                rows.append({
                    "Emel": u["email"],
                    "Peranan": ROLE_LABELS.get(u["role"], u["role"]),
                    "Aktif": "✅" if u["is_active"] else "❌",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Tiada pengguna.")
        st.markdown('</div>', unsafe_allow_html=True)


def page_maklumat_sistem():
    st.markdown('<div class="jn-header-bar"><div><span class="jn-header-title">ℹ️ Maklumat Sistem</span><br><span class="jn-header-sub">Seni bina & teknologi</span></div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="jn-card">
    <div class="jn-card-header">🛡️ JN Resolusi — Sistem Audit Pintar MOE</div>

    ### 🎯 Visi
    **Supreme Truth & Audit Node** — Platform pemantauan dan audit silang pintar
    untuk sekolah-sekolah KPM Malaysia.

    ### 🏗️ Seni Bina
    | Lapisan | Teknologi |
    |---------|-----------|
    | Frontend & Backend | **Streamlit** (Python) |
    | Pangkalan Data | **Neon PostgreSQL** (Serverless) |
    | Autentikasi | **JWT** + RBAC 3 peranan |
    | Pipeline AI | **Agent A → B → C** (Semantic → DI → Executive Brief) |

    ### 🤖 Agent Pipeline
    - **Agent A** — Semantic Ingestion & Category Mapping (NER-style)
    - **Agent B** — Discrepancy Index & Anomaly Detection
    - **Agent C** — Executive Brief & Enforcement Recommendations

    ### 🔐 Keselamatan
    - JWT Authentication (HS256)
    - RBAC: admin / penyelaras_jn / peneraju_sektor
    - Domain restriction: @moe.gov.my / @moe-dl.edu.my
    - Password hashing: sha256_crypt

    ### 📊 Formula Discrepancy Index
    > **DI = |Skor Audit − Skor Operasi| / 100**

    | Julat | Klasifikasi |
    |-------|-------------|
    | ≥ 0.75 | EXTREME DISCREPANCY |
    | ≥ 0.50 | SEVERE DISCREPANCY |
    | ≥ 0.25 | MODERATE DISCREPANCY |
    | ≥ 0.10 | MINOR DISCREPANCY |
    | < 0.10 | DATA ALIGNED |

    ### 📦 Versi
    - **JN Resolusi v2.0** (Streamlit + Neon PostgreSQL)
    - PRESTIJ-25 · MoE Agentic AI
    - © 2025 KPM Jemaah Nazir
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════

def main():
    # Init session state
    if "page" not in st.session_state:
        st.session_state["page"] = "Log Masuk" if not _is_authenticated() else "Dashboard"

    page = st.session_state.get("page", "Log Masuk")

    # Route: Login page (no sidebar auth needed)
    if page == "Log Masuk":
        page_login()
        return

    # All other pages require authentication
    if not _is_authenticated():
        st.session_state["page"] = "Log Masuk"
        st.rerun()
        return

    render_sidebar()

    # Route to page
    pages = {
        "Dashboard": page_dashboard,
        "Hantar Payload": page_hantar_payload,
        "Log Kes": page_log_kes,
        "Ringkasan Eksekutif": page_ringkasan_eksekutif,
        "Muat Naik CSV": page_muat_naik_csv,
        "Pengurusan Pengguna": page_pengurusan_pengguna,
        "Maklumat Sistem": page_maklumat_sistem,
    }

    handler = pages.get(page, page_dashboard)
    handler()


if __name__ == "__main__":
    main()
