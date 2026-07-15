import streamlit as st
from PIL import Image
import plotly.graph_objects as go
import pandas as pd
from html import escape
from components.sidebar import render_sidebar
from utils.impact_simulator import simulate_fixes

from services.scanner import scan_website
from services.form_analyzer import analyze_forms
from services.security import analyze_security
from services.accessibility import analyze_accessibility
from services.performance import analyze_performance
from services.seo import analyze_seo
from services.links import audit_links

from utils.report_generator import generate_report
from utils.pdf_generator import generate_pdf
from utils.db import save_scan, get_url_history

st.set_page_config(
    page_title="SiteVerify - Dashboard",
    page_icon="📊",
    layout="wide"
)
# Render sidebar navigation
render_sidebar(active_page="pages/2_📊_Dashboard.py")

# =====================================================
# Custom CSS Loading
# =====================================================
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("styles/main.css")

# =====================================================
# Console Dashboard UI Helpers
# =====================================================
def render_gauge(label, score):
    offset = int(283 * (1 - score / 100))
    if score >= 85:
        color = "var(--signal-cyan)"
    elif score >= 65:
        color = "var(--signal-amber)"
    else:
        color = "var(--signal-red)"
        
    return f"""
    <div class="sv-gauge-card">
        <div class="sv-gauge-label">{label}</div>
        <div class="sv-gauge-svg">
            <svg width="100" height="100" viewBox="0 0 100 100">
                <circle class="sv-gauge-bg" cx="50" cy="50" r="45"></circle>
                <circle class="sv-gauge-value-arc" cx="50" cy="50" r="45" 
                        style="--gauge-offset: {offset}; stroke: {color};"></circle>
            </svg>
            <div style="position: absolute; top: 0; left: 0; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 20px; font-weight: 700; color: var(--text-primary);">
                {int(score)}
            </div>
        </div>
    </div>
    """

def render_console_table(headers, rows):
    th_html = "".join([f"<th>{h}</th>" for h in headers])
    tr_html = ""
    for row in rows:
        tds = ""
        for cell in row:
            cell_str = str(cell)
            if "✅" in cell_str:
                cell_str = f'<span class="sv-console-checkmark">{cell_str}</span>'
            elif "❌" in cell_str:
                cell_str = f'<span class="sv-console-missing">{cell_str}</span>'
            tds += f"<td>{cell_str}</td>"
        tr_html += f"<tr>{tds}</tr>"
        
    return f"""
    <table class="sv-console-table">
        <thead>
            <tr>{th_html}</tr>
        </thead>
        <tbody>
            {tr_html}
        </tbody>
    </table>
    """

def render_log_item(text):
    text_lower = text.lower()
    if "error" in text_lower or "risk" in text_lower or "missing" in text_lower or "insecure" in text_lower or "failed" in text_lower:
        severity = "critical"
        icon = "[FAIL]"
    elif "warning" in text_lower or "concern" in text_lower or "notice" in text_lower:
        severity = "warning"
        icon = "[WARN]"
    else:
        severity = "passed"
        icon = "[PASS]"
        
    return f"""
    <div class="sv-log-item {severity}">
        <span class="sv-log-icon">{icon}</span>
        <span>{escape(text)}</span>
    </div>
    """

if "website" not in st.session_state:
    st.warning("Please go to the Home page and enter a URL to scan.")
    st.stop()

website = st.session_state["website"]

# =====================================================
# Website Scanning Orchestration
# =====================================================
status_bar_placeholder = st.empty()

if "report" not in st.session_state or st.session_state.get("last_scanned_url") != website:
    status_bar_placeholder.markdown("""
    <div class="sv-status-bar">
        <span class="sv-status-dot amber"></span>
        <span>SYSTEM: RUNNING SCANNER OPERATIONS // COLLECTING TARGET PAYLOADS</span>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Scanning website and extracting browser profiles. Please wait..."):
        scan_result = scan_website(website)

        if not scan_result["success"]:
            status_bar_placeholder.markdown("""
            <div class="sv-status-bar">
                <span class="sv-status-dot red"></span>
                <span>SYSTEM: ERROR // SCAN OPERATION FAILED</span>
            </div>
            """, unsafe_allow_html=True)
            st.error(f"❌ Scan failed: {scan_result['error']}")
            st.info("Ensure the URL is accessible and Chrome can run on the target host.")
            st.stop()
        
        # Store the raw scan result for later pages
        st.session_state["scan_result"] = scan_result
        
        html = scan_result["html"]
        target_url = scan_result["url"]
        timing_data = scan_result.get("performance_timings")
        
        # Load the full report once for all pages
        st.session_state["report"] = generate_report(
            scan_result,
            analyze_forms(html),
            analyze_security(html, target_url),
            analyze_accessibility(html),
            analyze_performance(html, timing_data),
            analyze_seo(html),
            audit_links(html, target_url)
        )
        st.session_state["last_scanned_url"] = website

report = st.session_state["report"]

status_bar_placeholder.markdown("""
<div class="sv-status-bar">
    <span class="sv-status-dot cyan"></span>
    <span>SYSTEM: ANALYZER MODE // DATA READOUT COMPLETE // INSTRUMENT PANEL ONLINE</span>
</div>
""", unsafe_allow_html=True)

# Save scan report to SQLite history
if "scan_saved" not in st.session_state or st.session_state.get("scan_saved_url") != website:
    try:
        save_scan(
            url=report["website"]["url"],
            title=report["website"]["title"],
            overall_score=report["overall_score"],
            grade=report["grade"],
            status=report["status"],
            screenshot_path=report["website"]["screenshot"],
            report_dict=report
        )
        st.session_state["scan_saved"] = True
        st.session_state["scan_saved_url"] = website
    except Exception as e:
        st.warning(f"Could not persist scan results: {str(e)}")

# Score helper
def score_badge(score, thresholds=(85, 65, 45)):
    if score >= thresholds[0]:
        return "badge-green"
    if score >= thresholds[1]:
        return "badge-amber"
    return "badge-red"

# =====================================================
# Main Header Section
# =====================================================
st.markdown("""
<div class="sv-section-header">
    <div class="sv-section-icon">📊</div>
    <p class="sv-section-title">Audit Results Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── Summary Layout (Metrics & Radar Chart)
top_left, top_right = st.columns([3, 2])

with top_left:
    overall_score = report["overall_score"]
    sec_score = report["security"]["security_score"]
    acc_score = report["accessibility"]["accessibility_score"]
    perf_score = report["performance"]["performance_score"]
    seo_score = report["seo"]["seo_score"]

    gauges_html = f"""
    <div class="sv-gauge-grid">
        {render_gauge("Overall Score", overall_score)}
        {render_gauge("Security", sec_score)}
        {render_gauge("Accessibility", acc_score)}
        {render_gauge("Performance", perf_score)}
        {render_gauge("SEO Audit", seo_score)}
    </div>
    """
    st.markdown(gauges_html, unsafe_allow_html=True)

with top_right:
    # Plotly Radar Chart
    categories = ['Security', 'Accessibility', 'Performance', 'SEO']
    scores = [sec_score, acc_score, perf_score, seo_score]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Categories',
        line_color='#5EEAD4',
        fillcolor='rgba(94, 234, 212, 0.15)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#8291A8", family="IBM Plex Mono", size=10),
                linecolor="#1F2937",
                gridcolor="#1F2937"
            ),
            angularaxis=dict(
                tickfont=dict(color="#E2E8F0", size=11, family="Space Grotesk"),
                linecolor="#1F2937"
            ),
            bgcolor="#121A2B"
        ),
        showlegend=False,
        margin=dict(l=45, r=45, t=35, b=35),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

# =====================================================
# Metadata and Screenshot Section
# =====================================================
info_left, info_right = st.columns([3, 2])

with info_left:
    st.markdown("""
    <div class="sv-section-header">
        <div class="sv-section-icon" style="background:#F0FDF4">🌐</div>
        <p class="sv-section-title">Website Information</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sv-info-card">
        <div class="sv-info-row">
            <span class="sv-info-key">Page Title</span>
            <span class="sv-info-val">{escape(report['website']['title'] or 'Untitled')}</span>
        </div>
        <div class="sv-info-row">
            <span class="sv-info-key">Scan URL</span>
            <span class="sv-info-val" style="font-family:monospace;font-size:12px;color:#2563EB;">{escape(report['website']['url'] or '')}</span>
        </div>
        <div class="sv-info-row">
            <span class="sv-info-key">Scan Timestamp</span>
            <span class="sv-info-val">{escape(report.get('timestamp', 'N/A'))}</span>
        </div>
        <div class="sv-info-row">
            <span class="sv-info-key">Audit Grade</span>
            <span class="sv-info-val"><span class="sv-score-badge badge-blue" style="font-size:12px;padding:3px 10px">{escape(report["grade"])}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with info_right:
    try:
        image = Image.open(report["website"]["screenshot"])
        st.image(image, caption="Visual Viewport Capture", use_container_width=True)
    except Exception:
        st.markdown("""
        <div class="sv-info-card" style="text-align:center;padding:32px;color:#94A3B8">
            <div style="font-size:36px;margin-bottom:8px">🖼</div>
            <div style="font-size:13px">Screenshot Unavailable</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =====================================================
# Tabbed Breakdown Sections
# =====================================================
tab_sec, tab_acc, tab_perf, tab_seo, tab_forms, tab_links, tab_sim = st.tabs([
    "🔒 Security & SSL",
    "♿ Accessibility",
    "⚡ Performance & Timings",
    "🔍 SEO & Social Info",
    "📝 Form Intelligence",
    "🔗 Link Audit",
    "🧪 Fix Impact Simulator"
])

# ── 1. Security & SSL Tab
with tab_sec:
    sec_col1, sec_col2 = st.columns([1, 2])
    
    with sec_col1:
        # SSL Check
        ssl_info = report["security"].get("ssl_details", {})
        st.markdown("### SSL Certificate Profile")
        if ssl_info.get("valid"):
            st.success("✅ Certificate is Valid and Trusted")
            st.markdown(f"""
            - **Issuer:** `{ssl_info['issuer']}`
            - **Expiry Date:** `{ssl_info['expiry']}`
            - **Days Remaining:** `{ssl_info['remaining_days']} days`
            """)
        else:
            st.error("❌ Invalid or Expired Certificate")
            st.markdown(f"**Error Details:** `{ssl_info.get('error', 'Insecure Connection')}`")
            
        # Form alerts
        st.markdown("### Endpoint Security")
        st.markdown(f"- Insecure Forms (HTTP): **{report['security']['insecure_forms']}**")
        st.markdown(f"- External action forms: **{report['security']['external_forms']}**")
        st.markdown(f"- Password autocomplete enabled: **{report['security']['autocomplete_enabled']}**")

    with sec_col2:
        st.markdown("### Security Response Headers")
        headers = report["security"].get("security_headers", {})
        
        header_statuses = []
        for h_name, h_val in headers.items():
            present = h_val is not None
            icon = "✅ Present" if present else "❌ Missing"
            val_text = f"`{h_val}`" if present else "*(Not Configured)*"
            header_statuses.append({"Header": h_name, "Status": icon, "Value": val_text})
        
        st.markdown(render_console_table(["Header", "Status", "Value"], [[item["Header"], item["Status"], item["Value"]] for item in header_statuses]), unsafe_allow_html=True)
        
        st.markdown("### Security Findings & Anomalies")
        sec_findings = report["security"]["findings"]
        if sec_findings:
            logs_html = "".join([render_log_item(item) for item in sec_findings])
            st.markdown(logs_html, unsafe_allow_html=True)
        else:
            st.success("No security issues found.")

# ── 2. Accessibility Tab
with tab_acc:
    acc_c1, acc_c2 = st.columns([1, 2])
    with acc_c1:
        st.metric("Missing Alt Attributes", report["accessibility"]["missing_alt"])
        st.metric("Unlabeled Input Controls", report["accessibility"]["unlabeled_inputs"])
        st.metric("Empty HTML Buttons", report["accessibility"]["empty_buttons"])
    with acc_c2:
        st.markdown("### Accessibility Findings")
        acc_findings = report["accessibility"]["findings"]
        if acc_findings:
            logs_html = "".join([render_log_item(item) for item in acc_findings])
            st.markdown(logs_html, unsafe_allow_html=True)

# ── 3. Performance Tab
with tab_perf:
    perf_col1, perf_col2 = st.columns([1, 2])
    
    with perf_col1:
        st.markdown("### Page Asset Profile")
        st.markdown(f"- **Total HTML Size:** {report['performance']['html_size_kb']} KB")
        st.markdown(f"- **Images count:** {report['performance']['images']}")
        st.markdown(f"- **Stylesheets:** {report['performance']['stylesheets']} (External: {report['performance'].get('external_css', 0)}, Inline: {report['performance'].get('inline_css', 0)})")
        st.markdown(f"- **Scripts:** {report['performance']['scripts']} (External: {report['performance'].get('external_js', 0)}, Inline: {report['performance'].get('inline_js', 0)})")
        st.markdown(f"- **Internal/External Links:** {report['performance']['links']}")

    with perf_col2:
        st.markdown("### W3C Timing Profile (Navigation API)")
        metrics = report["performance"].get("metrics", {})
        if metrics and metrics.get("page_load_ms", 0) > 0:
            st.info(f"⚡ Full Load cycle completed in **{round(metrics['page_load_ms']/1000, 3)}s**")
            
            # Format timeline list for display
            timeline_items = [
                {"Metric Phase": "DNS Domain Lookup", "Latency (ms)": f"{metrics['dns_lookup_ms']} ms"},
                {"Metric Phase": "TCP Handshake Delay", "Latency (ms)": f"{metrics['tcp_handshake_ms']} ms"},
                {"Metric Phase": "Time to First Byte (TTFB)", "Latency (ms)": f"{metrics['ttfb_ms']} ms"},
                {"Metric Phase": "Server response download", "Latency (ms)": f"{metrics['server_response_ms']} ms"},
                {"Metric Phase": "DOM Processing latency", "Latency (ms)": f"{metrics['dom_processing_ms']} ms"},
                {"Metric Phase": "Total Execution Cycle Time", "Latency (ms)": f"{metrics['page_load_ms']} ms"}
            ]
            st.markdown(render_console_table(["Metric Phase", "Latency (ms)"], [[item["Metric Phase"], item["Latency (ms)"]] for item in timeline_items]), unsafe_allow_html=True)
        else:
            st.warning("W3C Navigation timings are unavailable (most likely blocked or cached by host).")

        st.markdown("### Performance Recommendations Detail")
        perf_findings = report["performance"]["findings"]
        if perf_findings:
            logs_html = "".join([render_log_item(item) for item in perf_findings])
            st.markdown(logs_html, unsafe_allow_html=True)

# ── 4. SEO & Social Metadata Tab
with tab_seo:
    seo_col1, seo_col2 = st.columns([1, 2])
    with seo_col1:
        st.markdown("### Basic SEO Configuration")
        seo_meta = report["seo"]
        st.markdown(f"**Title Tag:** `{seo_meta.get('title') or '(Missing)'}`")
        st.markdown(f"**Meta Description:** `{(seo_meta.get('meta_description') or 'Missing meta description.')}`")
        st.markdown(f"**Canonical Tag:** `{'✅ Present' if seo_meta.get('has_canonical') else '❌ Missing'}`")
        st.markdown(f"**Viewport Responsiveness:** `{'✅ Configured' if seo_meta.get('has_viewport') else '❌ Missing'}`")
        
        st.markdown("### Social Card Configurations")
        st.markdown(f"**Open Graph Tags:** `{'✅ Configured' if seo_meta.get('has_og_tags') else '❌ Missing og:title/og:image'}`")
        st.markdown(f"**Twitter Metadata:** `{'✅ Present' if seo_meta.get('has_twitter_card') else '❌ Missing twitter:card'}`")
        
    with seo_col2:
        st.markdown("### Heading Architecture")
        headings_list = [
            ["H1 (Primary)", seo_meta.get("h1_count", 0)],
            ["H2 (Secondary)", seo_meta.get("h2_count", 0)],
            ["H3 (Tertiary)", seo_meta.get("h3_count", 0)]
        ]
        st.markdown(render_console_table(["Heading Tag", "Occurrences"], headings_list), unsafe_allow_html=True)
        
        st.markdown("### SEO Gaps Identified")
        seo_findings = seo_meta.get("findings", [])
        if seo_findings:
            logs_html = "".join([render_log_item(item) for item in seo_findings])
            st.markdown(logs_html, unsafe_allow_html=True)

# ── 5. Form Intelligence Tab
with tab_forms:
    forms = report["forms"]
    fc1, fc2 = st.columns([1, 3])
    with fc1:
        st.metric("Total Forms", forms["forms_found"])
        st.metric("Inputs", forms["total_inputs"])
        st.metric("Buttons", forms["total_buttons"])
    with fc2:
        st.markdown("### Fields Type Summary")
        st.markdown(f"- Email Inputs: **{forms['email_fields']}**")
        st.markdown(f"- Password Inputs: **{forms['password_fields']}**")
        st.markdown(f"- Search Inputs: **{forms['search_fields']}**")
        st.markdown(f"- Hidden Inputs: **{forms['hidden_fields']}**")
        st.markdown(f"- Checkboxes: **{forms['checkbox_fields']}**")
        
        if forms["form_details"]:
            st.markdown("### Form Details Grid")
            st.dataframe(pd.DataFrame(forms["form_details"]), use_container_width=True)
        else:
            st.success("No interactive forms detected on this URL.")

# ── 6. Link Audit Tab
with tab_links:
    links_info = report["links"]
    st.markdown("### Anchor Links Summary")
    st.markdown(f"**Total Links Extracted:** `{links_info['total_links_found']}`")
    st.markdown(f"**Tested Links:** `{links_info['links_tested']}` (Audited unique links limit to top 30)")
    
    col_l1, col_l2 = st.columns(2)
    col_l1.metric("Working Links Checked", links_info["working_links"])
    col_l2.metric("Broken Links Checked", links_info["broken_links_count"])
    
    if links_info["broken_links"]:
        st.markdown("### Broken Link Registry")
        st.dataframe(pd.DataFrame(links_info["broken_links"]), use_container_width=True)
    else:
        st.success("✅ Clean Link Audit: No broken links detected among the scanned URLs.")

# ── 7. Fix Impact Simulator Tab
with tab_sim:
    all_deductions = []
    for cat in ["security", "accessibility", "performance", "seo"]:
        for d in report.get(cat, {}).get("deductions", []):
            all_deductions.append(d)
            
    all_deductions.sort(key=lambda x: x["points"], reverse=True)
    
    if "fixed_ids" not in st.session_state:
        st.session_state["fixed_ids"] = set()
        
    st.markdown("### Hypothetical Fixes Prioritization List")
    st.markdown("Check the issues you plan to address to preview the projected score impact:")
    
    sim_col1, sim_col2 = st.columns([3, 2])
    
    with sim_col1:
        if not all_deductions:
            st.success("No deductions detected! Your site scores 100% in all categories.")
        else:
            new_fixed_ids = set()
            for d in all_deductions:
                key = f"sim_{d['id']}_{d['category']}"
                default_val = d["id"] in st.session_state["fixed_ids"]
                checked = st.checkbox(
                    label=f"{d['label']} (+{d['points']} pts)",
                    value=default_val,
                    key=key,
                    help=f"Category: {d['category'].upper()} | ID: {d['id']}"
                )
                if checked:
                    new_fixed_ids.add(d["id"])
            st.session_state["fixed_ids"] = new_fixed_ids
            
    with sim_col2:
        projected = simulate_fixes(report, st.session_state["fixed_ids"])
        
        st.markdown("### Score Projection Panel")
        
        # Display overall comparison card
        st.markdown(f"""
        <div class="sv-info-card" style="border-left: 4px solid var(--signal-cyan); text-align: center; margin-bottom: 24px;">
            <div style="font-family: var(--font-display); font-size: 14px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 8px;">Overall Performance</div>
            <div style="display: flex; justify-content: center; align-items: baseline; gap: 16px;">
                <div>
                    <div style="font-size: 11px; color: var(--text-muted);">CURRENT</div>
                    <div style="font-family: var(--font-mono); font-size: 32px; font-weight: 700; color: var(--text-muted);">{report['overall_score']}</div>
                </div>
                <div style="font-size: 24px; color: var(--text-muted);">➔</div>
                <div>
                    <div style="font-size: 11px; color: var(--signal-cyan);">PROJECTED</div>
                    <div style="font-family: var(--font-mono); font-size: 42px; font-weight: 700; color: var(--signal-cyan);">{projected['overall_score']}</div>
                </div>
            </div>
            <div style="margin-top: 8px; font-family: var(--font-display); font-size: 14px; font-weight: 600; color: var(--signal-cyan);">
                {projected['grade']} Grade · {projected['status']}
            </div>
            {f'<div style="margin-top: 12px; font-family: var(--font-mono); font-size: 13px; color: var(--signal-cyan);">+{round(projected["overall_score"] - report["overall_score"], 1)} points improvement</div>' if projected["overall_score"] > report["overall_score"] else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Category projections
        def render_comp_row(label, current_score, projected_score):
            if projected_score >= 85:
                color = "var(--signal-cyan)"
            elif projected_score >= 65:
                color = "var(--signal-amber)"
            else:
                color = "var(--signal-red)"
                
            delta_str = f"+{int(projected_score - current_score)}" if projected_score > current_score else "0"
            delta_style = "color: var(--signal-cyan);" if projected_score > current_score else "color: var(--text-muted);"
            
            return f"""
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--grid-line); padding: 8px 0; font-family: var(--font-mono); font-size: 13px;">
                <span style="font-family: var(--font-body); font-weight: 600; color: var(--text-primary);">{label}</span>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="color: var(--text-muted);">{int(current_score)}</span>
                    <span style="color: var(--text-muted);">➔</span>
                    <span style="font-weight: 700; color: {color};">{int(projected_score)}</span>
                    <span style="font-size: 11px; {delta_style}">({delta_str})</span>
                </div>
            </div>
            """
            
        st.markdown(f"""
        <div class="sv-info-card">
            <h4 style="margin-top: 0; color: var(--text-primary); font-family: var(--font-display);">Category Projections</h4>
            {render_comp_row("Security", report['security']['security_score'], projected['security_score'])}
            {render_comp_row("Accessibility", report['accessibility']['accessibility_score'], projected['accessibility_score'])}
            {render_comp_row("Performance", report['performance']['performance_score'], projected['performance_score'])}
            {render_comp_row("SEO Audit", report['seo']['seo_score'], projected['seo_score'])}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 16px; line-height: 1.4;">
            Toggle fixes to see their impact on your score. This does not re-scan the site — check the boxes for issues you plan to fix, then re-run the audit after making changes to confirm.
        </div>
        """, unsafe_allow_html=True)

st.divider()

# =====================================================
# Recommendations Section
# =====================================================
st.markdown("""
<div class="sv-section-header">
    <div class="sv-section-icon" style="background:#EFF6FF">💡</div>
    <p class="sv-section-title">Prioritized Recommendations</p>
</div>
""", unsafe_allow_html=True)

recs = report["recommendations"]
if recs:
    recs_html = "".join([render_log_item(rec) for rec in recs])
    st.markdown(recs_html, unsafe_allow_html=True)
else:
    st.success("✅ Perfect Profile! No recommendations needed.")

st.divider()

# =====================================================
# Scan History Comparison (Same URL)
# =====================================================
st.markdown("""
<div class="sv-section-header">
    <div class="sv-section-icon" style="background:#F3F4F6">📈</div>
    <p class="sv-section-title">Historical Scan Tracking (Current Site)</p>
</div>
""", unsafe_allow_html=True)

try:
    hist = get_url_history(report["website"]["url"])
    if len(hist) > 1:
        hist_df = pd.DataFrame(hist)
        hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
        
        hist_fig = go.Figure()
        hist_fig.add_trace(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["overall_score"],
            mode="lines+markers",
            name="Overall Score",
            line=dict(color="#5EEAD4", width=3),
            marker=dict(size=8, color="#5EEAD4")
        ))
        hist_fig.update_layout(
            title="Overall Score Trend (Successive Scans)",
            xaxis=dict(
                title="Time of Scan",
                gridcolor="#1F2937",
                linecolor="#1F2937",
                tickfont=dict(color="#8291A8", family="IBM Plex Mono")
            ),
            yaxis=dict(
                title="Overall Score",
                gridcolor="#1F2937",
                linecolor="#1F2937",
                range=[0, 105],
                tickfont=dict(color="#8291A8", family="IBM Plex Mono")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#121A2B',
            font=dict(color="#E2E8F0", family="Space Grotesk"),
            height=250,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(hist_fig, use_container_width=True)
    else:
        st.info("ℹ️ This is the first recorded scan for this site. Successive scans will build a historical trend chart.")
except Exception as e:
    st.warning(f"Unable to show history comparison graph: {str(e)}")

st.divider()

# =====================================================
# Export Audit Report
# =====================================================
st.markdown("""
<div class="sv-export-card">
    <div>
        <div class="sv-export-title">Compile & Download Full PDF Report</div>
        <div class="sv-export-sub">Generates a professional executive-ready PDF report including all detailed audits, SSL configurations, SEO checks, and recommendations.</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("📄 Generate PDF Report", key="generate_pdf"):
    with st.spinner("Compiling PDF assets..."):
        pdf_path = generate_pdf(report)
    st.success("✅ PDF compiled successfully!")
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_file,
            file_name=f"SiteVerify_Audit_{website.replace('https://','').replace('http://','').replace('/','')}.pdf",
            mime="application/pdf"
        )

# Developer View Expander
with st.expander("🛠️ Raw JSON Report Document (Developer Debugger View)"):
    st.json(report)

# =====================================================
# Footer
# =====================================================
st.markdown("""
<div style="
    background-color: var(--panel);
    border-radius: 8px;
    padding: 24px;
    color: var(--text-muted);
    margin-top: 20px;
    border: 1px solid var(--grid-line);
    font-family: var(--font-body);
">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <span style="font-size:16px;font-weight:700;color:var(--text-primary);font-family:var(--font-display);">SITEVERIFY WEB AUDIT INSTRUMENT v2.0</span>
    </div>
    <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;line-height:1.5;">
        Fully modular diagnostic engine providing accessibility checks, SEO indexes, core performance timing indices, SSL trust verification, and deep form profiling.
    </div>
    <div style="display:flex;gap:20px;flex-wrap:wrap;font-size:11px;color:var(--signal-cyan);font-family:var(--font-mono);">
        <span>[PYTHON]</span>
        <span>[STREAMLIT]</span>
        <span>[SELENIUM_HEADLESS]</span>
        <span>[BS4_PARSER]</span>
        <span>[PLOTLY_CHARTS]</span>
        <span>[SQLITE_STORE]</span>
    </div>
</div>
""", unsafe_allow_html=True)
