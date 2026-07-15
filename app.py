import streamlit as st
from utils.db import get_aggregate_stats, init_db
from components.sidebar import render_sidebar
from services.scanner import scan_website

# Initialize DB on application startup
try:
    init_db()
except Exception:
    pass

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="SiteVerify - Web Auditor",
    page_icon="🌐",
    layout="wide"
)

# =====================================================
# Custom CSS
# =====================================================
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("styles/main.css")
render_sidebar(active_page="app.py")

# =====================================================
# Hero Header
# =====================================================
st.markdown("""
<div class="sv-hero">
    <div class="sv-hero-eyebrow">DIAGNOSTIC WORKSTATION // SITEVERIFY_v1.2.0</div>
    <h1>Site<span>Verify</span></h1>
    <p class="sv-hero-sub">
        Perform automated diagnostics on any target domain. Assess SSL integrity, HTTP security headers, 
        W3C performance timings, search-engine SEO compliance, accessibility, and form architecture.
    </p>
</div>
""", unsafe_allow_html=True)

# System Status Bar
st.markdown("""
<div class="sv-status-bar">
    <span class="sv-status-dot cyan"></span>
    <span>SYSTEM: IDLE // READY FOR SCANNER INPUT</span>
</div>
""", unsafe_allow_html=True)

# =====================================================
# URL Input
# =====================================================
with st.container(border=True):
    st.markdown('<div class="sv-input-label">[SYS_INPUT] Enter target website URL</div>', unsafe_allow_html=True)
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        website = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            label_visibility="collapsed"
        )
    with col_btn:
        scan = st.button("🚀 Run Site Audit")

# =====================================================
# Scan Website Orchestration
# =====================================================
if scan:
    if website.strip() == "":
        st.error("⚠️ Please enter a valid website URL before scanning.")
        st.stop()
    else:
        st.session_state["website"] = website.strip()
        st.success(f"Launching scanner engine for {website}...")
        st.switch_page("pages/2_📊_Dashboard.py")

# =====================================================
# Aggregate Statistics Banner (Landing Page Stats)
# =====================================================
st.markdown("<br><br>", unsafe_allow_html=True)
try:
    stats = get_aggregate_stats()
    if stats["total_scans"] > 0:
        st.markdown(f"""
        <div class="sv-input-label" style="text-align: center; margin-bottom: 16px;">
            Auditing Platform Statistics
        </div>
        <div class="sv-stat-strip">
            <div class="sv-stat-pill">
                <div class="sv-stat-num">{stats['total_scans']}</div>
                <div class="sv-stat-lbl">Audits Conducted</div>
            </div>
            <div class="sv-stat-pill">
                <div class="sv-stat-num">{stats['unique_domains']}</div>
                <div class="sv-stat-lbl">Domains Profiled</div>
            </div>
            <div class="sv-stat-pill">
                <div class="sv-stat-num">{stats['avg_score']}<span style="font-size:12px;font-weight:400;color:var(--text-muted);">/100</span></div>
                <div class="sv-stat-lbl">Avg Health Index</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
except Exception:
    pass
