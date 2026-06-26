import streamlit as st
from PIL import Image

from services.scanner import scan_website
from services.form_analyzer import analyze_forms
from services.security import analyze_security
from services.accessibility import analyze_accessibility
from services.performance import analyze_performance

from utils.report_generator import generate_report
from utils.pdf_generator import generate_pdf


# =====================================================
# Page Configuration
# =====================================================

st.set_page_config(
    page_title="SiteVerify",
    page_icon="🌐",
    layout="wide"
)

# =====================================================
# Custom CSS — Professional Redesign
# =====================================================

st.markdown("""
<style>

/* ── Base & Background ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #F0F4FF !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

[data-testid="stMain"] {
    background: #F0F4FF;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

/* ── Hero Header ── */
.sv-hero {
    background: linear-gradient(135deg, #0A0F1E 0%, #0D1B3E 50%, #0F2460 100%);
    border-radius: 20px;
    padding: 52px 48px 44px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

.sv-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
    border-radius: 50%;
}

.sv-hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(16,185,129,0.10) 0%, transparent 70%);
    border-radius: 50%;
}

.sv-hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #93C5FD;
    margin-bottom: 18px;
}

.sv-hero h1 {
    font-size: 48px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin: 0 0 12px !important;
    padding: 0 !important;
}

.sv-hero h1 span {
    background: linear-gradient(90deg, #60A5FA, #34D399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sv-hero-sub {
    color: #94A3B8;
    font-size: 16px;
    line-height: 1.6;
    max-width: 560px;
    margin: 0;
}

/* ── URL Input Block ── */
.sv-input-block {
    background: white;
    border-radius: 16px;
    padding: 28px 32px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 28px;
}

.sv-input-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Override Streamlit input */
[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border: 2px solid #E2E8F0 !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
    background: #F8FAFF !important;
    transition: border-color 0.2s !important;
    color: #0F172A !important;
}

[data-testid="stTextInput"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
}

/* ── Primary Scan Button ── */
.stButton > button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 52px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.45) !important;
    background: linear-gradient(135deg, #1D4ED8, #1E40AF) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Section Headers ── */
.sv-section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 36px 0 20px;
}

.sv-section-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}

.sv-section-title {
    font-size: 22px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.02em;
    margin: 0;
}

/* ── Score Cards (top 4) ── */
.sv-score-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.sv-score-card {
    background: white;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border-top: 4px solid;
    position: relative;
    overflow: hidden;
}

.sv-score-card::after {
    content: '';
    position: absolute;
    top: -20px; right: -20px;
    width: 80px; height: 80px;
    border-radius: 50%;
    opacity: 0.06;
}

.sv-score-card.overall  { border-top-color: #3B82F6; }
.sv-score-card.overall::after  { background: #3B82F6; }
.sv-score-card.security { border-top-color: #10B981; }
.sv-score-card.security::after { background: #10B981; }
.sv-score-card.access   { border-top-color: #8B5CF6; }
.sv-score-card.access::after   { background: #8B5CF6; }
.sv-score-card.perf     { border-top-color: #F59E0B; }
.sv-score-card.perf::after     { background: #F59E0B; }

.sv-score-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 8px;
}

.sv-score-value {
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    color: #0F172A;
}

.sv-score-denom {
    font-size: 18px;
    font-weight: 400;
    color: #CBD5E1;
}

.sv-score-badge {
    display: inline-block;
    margin-top: 10px;
    padding: 3px 10px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
}

.badge-blue   { background: #EFF6FF; color: #2563EB; }
.badge-green  { background: #ECFDF5; color: #059669; }
.badge-purple { background: #F5F3FF; color: #7C3AED; }
.badge-amber  { background: #FFFBEB; color: #D97706; }
.badge-red    { background: #FEF2F2; color: #DC2626; }

/* ── Info Cards ── */
.sv-info-card {
    background: white;
    border-radius: 16px;
    padding: 24px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}

.sv-info-card h3 {
    font-size: 15px;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 16px;
}

.sv-info-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    margin-bottom: 8px;
}

.sv-info-key {
    font-size: 12px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    min-width: 80px;
}

.sv-info-val {
    font-size: 14px;
    color: #1E293B;
    font-weight: 500;
}

/* ── Stat Strip ── */
.sv-stat-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}

.sv-stat-pill {
    background: white;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    text-align: center;
}

.sv-stat-num {
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.03em;
    line-height: 1;
}

.sv-stat-lbl {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 4px;
}

/* ── Finding Items ── */
.sv-findings-list {
    list-style: none;
    padding: 0; margin: 0;
}

.sv-finding-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 14px;
    color: #334155;
    line-height: 1.5;
}

.sv-finding-item:last-child { border-bottom: none; }

.sv-finding-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3B82F6;
    flex-shrink: 0;
    margin-top: 7px;
}

/* ── Health Banner ── */
.sv-health-banner {
    border-radius: 14px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.sv-health-banner.excellent { background: #ECFDF5; border-left: 5px solid #10B981; }
.sv-health-banner.good      { background: #EFF6FF; border-left: 5px solid #3B82F6; }
.sv-health-banner.average   { background: #FFFBEB; border-left: 5px solid #F59E0B; }
.sv-health-banner.poor      { background: #FEF2F2; border-left: 5px solid #EF4444; }

.sv-health-banner-score {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
}

.sv-health-banner.excellent .sv-health-banner-score { color: #059669; }
.sv-health-banner.good .sv-health-banner-score      { color: #2563EB; }
.sv-health-banner.average .sv-health-banner-score   { color: #D97706; }
.sv-health-banner.poor .sv-health-banner-score      { color: #DC2626; }

.sv-health-label {
    font-size: 14px;
    font-weight: 600;
    color: #475569;
}

/* ── Summary Footer Cards ── */
.sv-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 12px;
}

.sv-summary-card {
    border-radius: 14px;
    padding: 22px 20px;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 4px solid;
}

.sv-summary-card.sec  { border-left-color: #10B981; }
.sv-summary-card.acc  { border-left-color: #8B5CF6; }
.sv-summary-card.prf  { border-left-color: #F59E0B; }

.sv-summary-card-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 10px;
}

.sv-summary-score-big {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0F172A;
    font-variant-numeric: tabular-nums;
    line-height: 1;
}

.sv-summary-level {
    font-size: 13px;
    color: #64748B;
    margin-top: 4px;
}

/* ── Recommendations ── */
.sv-rec-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 14px;
    color: #334155;
    line-height: 1.5;
}

.sv-rec-item:last-child { border-bottom: none; }

.sv-rec-icon {
    width: 22px; height: 22px;
    background: #EFF6FF;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
    flex-shrink: 0;
}

/* ── Export Card ── */
.sv-export-card {
    background: linear-gradient(135deg, #0A0F1E, #0F2460);
    border-radius: 16px;
    padding: 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    overflow: hidden;
    position: relative;
}

.sv-export-card::before {
    content: '';
    position: absolute;
    top: -40px; right: 80px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%);
    border-radius: 50%;
}

.sv-export-title {
    font-size: 20px;
    font-weight: 700;
    color: white;
    margin-bottom: 4px;
}

.sv-export-sub {
    font-size: 13px;
    color: #94A3B8;
}

/* ── Streamlit overrides ── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 12px;
    padding: 16px 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

[data-testid="metric-container"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #94A3B8 !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    letter-spacing: -0.03em !important;
}

[data-testid="stMetricDelta"] {
    font-size: 12px !important;
}

/* Spinner */
[data-testid="stSpinner"] {
    background: white;
    border-radius: 12px;
    padding: 12px 16px;
}

/* Tabs look better */
[data-baseweb="tab-list"] {
    background: #F0F4FF;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}

[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Alert / info box */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Expander */
[data-testid="stExpander"] {
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* Divider spacing */
hr {
    margin: 36px 0 !important;
    border-color: #E2E8F0 !important;
}

/* Column gap */
[data-testid="column"] {
    padding: 0 6px !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# Hero Header
# =====================================================

st.markdown("""
<div class="sv-hero">
    <div class="sv-hero-eyebrow">⚡ Automated Website Intelligence</div>
    <h1>Site<span>Verify</span></h1>
    <p class="sv-hero-sub">
        Deep-scan any website for security vulnerabilities, accessibility gaps,
        performance bottlenecks, and form structure — then export a professional audit report.
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# URL Input
# =====================================================

st.markdown('<div class="sv-input-block">', unsafe_allow_html=True)
st.markdown('<div class="sv-input-label">🌐 Enter website URL</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])

with col_input:
    website = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        label_visibility="collapsed"
    )

with col_btn:
    scan = st.button("🚀 Scan Website")

st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# Scan Website
# =====================================================

if scan:

    if website.strip() == "":
        st.error("⚠️ Please enter a valid website URL before scanning.")
        st.stop()

    with st.spinner("Scanning website — this may take a moment..."):
        scan_result = scan_website(website)

    if not scan_result["success"]:
        st.error(f"❌ Scan failed: {scan_result['error']}")
        st.stop()

    html = scan_result["html"]

    form_report        = analyze_forms(html)
    security_report    = analyze_security(html, scan_result["url"])
    accessibility_report = analyze_accessibility(html)
    performance_report = analyze_performance(html)

    report = generate_report(
        scan_result,
        form_report,
        security_report,
        accessibility_report,
        performance_report
    )

    # ── Helper: score → badge class
    def score_badge(score, thresholds=(80, 60, 40)):
        if score >= thresholds[0]: return "badge-green"
        if score >= thresholds[1]: return "badge-amber"
        return "badge-red"


    # =====================================================
    # Score Dashboard
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#EFF6FF">📊</div>
        <p class="sv-section-title">Audit Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    overall_score  = report["overall_score"]
    sec_score      = report["security"]["security_score"]
    acc_score      = report["accessibility"]["accessibility_score"]
    perf_score     = report["performance"]["performance_score"]

    st.markdown(f"""
    <div class="sv-score-grid">
        <div class="sv-score-card overall">
            <div class="sv-score-label">Overall Score</div>
            <div class="sv-score-value">{overall_score}<span class="sv-score-denom">/100</span></div>
            <span class="sv-score-badge badge-blue">{report["grade"]} Grade</span>
        </div>
        <div class="sv-score-card security">
            <div class="sv-score-label">Security</div>
            <div class="sv-score-value">{sec_score}<span class="sv-score-denom">/100</span></div>
            <span class="sv-score-badge {score_badge(sec_score)}">{report["security"]["security_level"]}</span>
        </div>
        <div class="sv-score-card access">
            <div class="sv-score-label">Accessibility</div>
            <div class="sv-score-value">{acc_score}<span class="sv-score-denom">/100</span></div>
            <span class="sv-score-badge {score_badge(acc_score)}">{report["accessibility"]["accessibility_level"]}</span>
        </div>
        <div class="sv-score-card perf">
            <div class="sv-score-label">Performance</div>
            <div class="sv-score-value">{perf_score}<span class="sv-score-denom">/100</span></div>
            <span class="sv-score-badge {score_badge(perf_score)}">{report["performance"]["performance_rating"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # =====================================================
    # Website Information + Screenshot
    # =====================================================

    left, right = st.columns([2, 1])

    with left:
        st.markdown("""
        <div class="sv-section-header">
            <div class="sv-section-icon" style="background:#F0FDF4">🌐</div>
            <p class="sv-section-title">Website Information</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sv-info-card">
            <div class="sv-info-row">
                <span class="sv-info-key">Title</span>
                <span class="sv-info-val">{report['website']['title']}</span>
            </div>
            <div class="sv-info-row">
                <span class="sv-info-key">URL</span>
                <span class="sv-info-val" style="font-family:monospace;font-size:13px;color:#2563EB">{report['website']['url']}</span>
            </div>
            <div class="sv-info-row">
                <span class="sv-info-key">Status</span>
                <span class="sv-info-val">{report['status']}</span>
            </div>
            <div class="sv-info-row">
                <span class="sv-info-key">Grade</span>
                <span class="sv-info-val"><span class="sv-score-badge badge-blue" style="font-size:13px;padding:4px 14px">{report["grade"]}</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="sv-section-header">
            <div class="sv-section-icon" style="background:#FFF7ED">📸</div>
            <p class="sv-section-title">Screenshot</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            image = Image.open(report["website"]["screenshot"])
            st.image(image, use_container_width=True)
        except:
            st.markdown("""
            <div class="sv-info-card" style="text-align:center;padding:32px;color:#94A3B8">
                <div style="font-size:36px;margin-bottom:8px">🖼</div>
                <div style="font-size:13px">Screenshot unavailable</div>
            </div>
            """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Quick Statistics
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#F0F4FF">📈</div>
        <p class="sv-section-title">Quick Statistics</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sv-stat-strip">
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{report["forms"]["forms_found"]}</div>
            <div class="sv-stat-lbl">Forms</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{report["forms"]["total_inputs"]}</div>
            <div class="sv-stat-lbl">Input Fields</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{report["forms"]["total_buttons"]}</div>
            <div class="sv-stat-lbl">Buttons</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{report["performance"]["links"]}</div>
            <div class="sv-stat-lbl">Links</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Form Intelligence
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#FFF7ED">📝</div>
        <p class="sv-section-title">Form Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    forms = report["forms"]

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Forms Found",      forms["forms_found"])
    col2.metric("Email Fields",     forms["email_fields"])
    col3.metric("Password Fields",  forms["password_fields"])
    col4.metric("Search Fields",    forms["search_fields"])
    col5.metric("Hidden Fields",    forms["hidden_fields"])
    col6.metric("Checkboxes",       forms["checkbox_fields"])

    if forms["form_details"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Detected Forms**")
        st.dataframe(forms["form_details"], use_container_width=True)
    else:
        st.success("✅ No forms detected on this website.")


    st.divider()


    # =====================================================
    # Security Analysis
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#ECFDF5">🔒</div>
        <p class="sv-section-title">Security Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    security = report["security"]

    sec_left, sec_right = st.columns([1, 2])

    with sec_left:
        st.markdown(f"""
        <div class="sv-info-card" style="text-align:center;padding:32px">
            <div class="sv-score-label" style="margin-bottom:8px">Security Score</div>
            <div style="font-size:64px;font-weight:900;color:#10B981;letter-spacing:-0.04em;font-variant-numeric:tabular-nums;line-height:1">
                {sec_score}
            </div>
            <div style="font-size:16px;color:#CBD5E1;margin-bottom:12px">/100</div>
            <span class="sv-score-badge {score_badge(sec_score)}" style="font-size:13px;padding:5px 16px">
                {security["security_level"]}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with sec_right:
        findings_html = "".join([
            f'<li class="sv-finding-item"><div class="sv-finding-dot" style="background:#10B981"></div>{item}</li>'
            for item in security["findings"]
        ])
        st.markdown(f"""
        <div class="sv-info-card">
            <h3>Security Findings</h3>
            <ul class="sv-findings-list">{findings_html}</ul>
        </div>
        """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Accessibility
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#F5F3FF">♿</div>
        <p class="sv-section-title">Accessibility Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    accessibility = report["accessibility"]

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Accessibility Score",  f"{acc_score}/100")
    a2.metric("Missing Alt Tags",     accessibility["missing_alt"])
    a3.metric("Unlabelled Inputs",    accessibility["unlabeled_inputs"])
    a4.metric("Empty Buttons",        accessibility["empty_buttons"])

    acc_findings_html = "".join([
        f'<li class="sv-finding-item"><div class="sv-finding-dot" style="background:#8B5CF6"></div>{item}</li>'
        for item in accessibility["findings"]
    ])
    st.markdown(f"""
    <div class="sv-info-card" style="margin-top:16px">
        <h3>Accessibility Findings</h3>
        <ul class="sv-findings-list">{acc_findings_html}</ul>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Performance Analysis
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#FFFBEB">⚡</div>
        <p class="sv-section-title">Performance Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    performance = report["performance"]

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Performance Score", f"{perf_score}/100")
    p2.metric("HTML Size",         f"{performance['html_size_kb']} KB")
    p3.metric("Images",            performance["images"])
    p4.metric("Scripts",           performance["scripts"])

    p5, p6, p7 = st.columns(3)
    p5.metric("Stylesheets", performance["stylesheets"])
    p6.metric("Links",        performance["links"])
    p7.metric("Forms",        performance["forms"])

    perf_findings_html = "".join([
        f'<li class="sv-finding-item"><div class="sv-finding-dot" style="background:#F59E0B"></div>{item}</li>'
        for item in performance["findings"]
    ])
    st.markdown(f"""
    <div class="sv-info-card" style="margin-top:16px">
        <h3>Performance Findings</h3>
        <ul class="sv-findings-list">{perf_findings_html}</ul>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Website Health
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#F0FDF4">💻</div>
        <p class="sv-section-title">Website Health</p>
    </div>
    """, unsafe_allow_html=True)

    score = report["overall_score"]

    if score >= 90:
        health_cls, health_msg = "excellent", "Excellent — this website is in great shape."
    elif score >= 80:
        health_cls, health_msg = "good",      "Good — minor improvements could polish things further."
    elif score >= 70:
        health_cls, health_msg = "average",   "Average — several areas need attention."
    else:
        health_cls, health_msg = "poor",      "Below average — significant improvements required."

    st.markdown(f"""
    <div class="sv-health-banner {health_cls}">
        <div>
            <div class="sv-health-label">Overall Website Score</div>
            <div style="font-size:14px;color:#64748B;margin-top:4px">{health_msg}</div>
            <div style="margin-top:10px">
                <span class="sv-score-badge badge-blue" style="font-size:13px;padding:5px 16px">
                    Grade {report["grade"]} · {report["status"]}
                </span>
            </div>
        </div>
        <div class="sv-health-banner-score">{score}</div>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Recommendations
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#EFF6FF">💡</div>
        <p class="sv-section-title">Recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    recommendations = report["recommendations"]

    if recommendations:
        recs_html = "".join([
            f"""<div class="sv-rec-item">
                    <div class="sv-rec-icon">✦</div>
                    <span>{rec}</span>
                </div>"""
            for rec in recommendations
        ])
        st.markdown(f'<div class="sv-info-card">{recs_html}</div>', unsafe_allow_html=True)
    else:
        st.success("✅ No recommendations — website looks healthy.")


    st.divider()


    # =====================================================
    # Raw Report (Developer View)
    # =====================================================

    with st.expander("🛠️ Raw JSON Report (Developer View)"):
        st.json(report)


    st.divider()


    # =====================================================
    # Export Audit Report
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#FEF2F2">📄</div>
        <p class="sv-section-title">Export Audit Report</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sv-export-card">
        <div>
            <div class="sv-export-title">Download Full PDF Report</div>
            <div class="sv-export-sub">A professional audit document with all findings, scores, and recommendations.</div>
        </div>
        <div style="font-size:48px;opacity:0.4">📋</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📄 Generate PDF Report", key="generate_pdf"):
        with st.spinner("Compiling your audit report..."):
            pdf_path = generate_pdf(report)

        st.success("✅ PDF generated successfully!")

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Download Audit Report",
                data=pdf_file,
                file_name="SiteVerify_Report.pdf",
                mime="application/pdf",
                key="download_pdf"
            )


    st.divider()


    # =====================================================
    # Scan Summary
    # =====================================================

    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#F0F4FF">📋</div>
        <p class="sv-section-title">Scan Summary</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sv-summary-grid">
        <div class="sv-summary-card sec">
            <div class="sv-summary-card-title">🔒 Security</div>
            <div class="sv-summary-score-big">{sec_score}<span style="font-size:16px;font-weight:400;color:#CBD5E1">/100</span></div>
            <div class="sv-summary-level">{report["security"]["security_level"]}</div>
        </div>
        <div class="sv-summary-card acc">
            <div class="sv-summary-card-title">♿ Accessibility</div>
            <div class="sv-summary-score-big">{acc_score}<span style="font-size:16px;font-weight:400;color:#CBD5E1">/100</span></div>
            <div class="sv-summary-level">{report["accessibility"]["accessibility_level"]}</div>
        </div>
        <div class="sv-summary-card prf">
            <div class="sv-summary-card-title">⚡ Performance</div>
            <div class="sv-summary-score-big">{perf_score}<span style="font-size:16px;font-weight:400;color:#CBD5E1">/100</span></div>
            <div class="sv-summary-level">{report["performance"]["performance_rating"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    st.divider()


    # =====================================================
    # Footer
    # =====================================================

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0A0F1E, #0D1B3E);
        border-radius: 16px;
        padding: 36px 40px;
        color: #94A3B8;
        margin-top: 8px;
    ">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
            <span style="font-size:22px">🌐</span>
            <span style="font-size:18px;font-weight:800;color:white;letter-spacing:-0.02em">SiteVerify</span>
        </div>
        <div style="font-size:13px;color:#64748B;margin-bottom:18px">
            Intelligent Website Audit & Form Analysis Platform
        </div>
        <div style="display:flex;gap:24px;flex-wrap:wrap">
            <span style="font-size:12px;color:#475569">Python</span>
            <span style="font-size:12px;color:#475569">Streamlit</span>
            <span style="font-size:12px;color:#475569">Selenium</span>
            <span style="font-size:12px;color:#475569">BeautifulSoup</span>
            <span style="font-size:12px;color:#475569">ReportLab</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
