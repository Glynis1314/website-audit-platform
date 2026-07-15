import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from html import escape
from utils.db import get_scan_history, get_scan_by_id, delete_scan, get_aggregate_stats
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="SiteVerify - Scan History",
    page_icon="📄",
    layout="wide"
)

# Load CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("styles/main.css")
render_sidebar(active_page="pages/4_📄_History.py")

# =====================================================
# Console UI Helpers
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
    <div class="sv-gauge-card" style="padding: 12px; border-radius: 6px; background-color: var(--panel-alt);">
        <div class="sv-gauge-label" style="font-size: 11px; margin-bottom: 8px;">{label}</div>
        <div class="sv-gauge-svg" style="width: 70px; height: 70px;">
            <svg width="70" height="70" viewBox="0 0 100 100">
                <circle class="sv-gauge-bg" cx="50" cy="50" r="45" style="stroke-width: 10;"></circle>
                <circle class="sv-gauge-value-arc" cx="50" cy="50" r="45" 
                        style="--gauge-offset: {offset}; stroke: {color}; stroke-width: 10;"></circle>
            </svg>
            <div style="position: absolute; top: 0; left: 0; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 14px; font-weight: 700; color: var(--text-primary);">
                {int(score)}
            </div>
        </div>
    </div>
    """

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="sv-section-header">
    <div class="sv-section-icon">📄</div>
    <p class="sv-section-title">Audit History Log</p>
</div>
""", unsafe_allow_html=True)

# System Status Bar
st.markdown("""
<div class="sv-status-bar">
    <span class="sv-status-dot cyan"></span>
    <span>SYSTEM: AUDIT RECORD INSPECTION MODE // DB CONNECTIONS NORMAL</span>
</div>
""", unsafe_allow_html=True)

# Fetch stats and history
stats = get_aggregate_stats()
history = get_scan_history()

# =====================================================
# Summary Statistics Banner
# =====================================================
if stats["total_scans"] > 0:
    st.markdown(f"""
    <div class="sv-stat-strip">
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{stats['total_scans']}</div>
            <div class="sv-stat-lbl">Total Scans</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{stats['unique_domains']}</div>
            <div class="sv-stat-lbl">Unique Domains</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{stats['avg_score']}<span style="font-size:12px;font-weight:400;color:var(--text-muted);">/100</span></div>
            <div class="sv-stat-lbl">Avg Health Score</div>
        </div>
        <div class="sv-stat-pill">
            <div class="sv-stat-num">{stats['highest_score']}<span style="font-size:12px;font-weight:400;color:var(--text-muted);">/100</span></div>
            <div class="sv-stat-lbl">Highest Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No audit scan history available yet. Run your first audit from the Home page!")
    st.stop()

# =====================================================
# History Grid and Details Panel
# =====================================================
left_col, right_col = st.columns([3, 2])

with left_col:
    st.markdown("### Recorded Audits")
    
    # Create DataFrame for display
    df = pd.DataFrame(history)
    df["Clean URL"] = df["url"].apply(lambda x: x.replace("https://", "").replace("http://", "").split("/")[0])
    
    # Filter tools
    search = st.text_input("🔍 Search by domain or title", "").strip().lower()
    if search:
        df = df[df["Clean URL"].str.contains(search) | df["title"].str.lower().str.contains(search)]
        
    if df.empty:
        st.info("No scans match the search criteria.")
    else:
        # Create pretty list select
        df_display = df[["id", "Clean URL", "overall_score", "grade", "timestamp"]].copy()
        df_display.columns = ["ID", "Domain", "Score", "Grade", "Scan Date"]
        
        # Display as a dataframe with selection
        st.write("Select a row below to inspect the historical audit details or download its PDF:")
        
        selected_row = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Determine selection
        selected_scan_id = None
        if selected_row and len(selected_row.get("selection", {}).get("rows", [])) > 0:
            selected_idx = selected_row["selection"]["rows"][0]
            selected_scan_id = int(df_display.iloc[selected_idx]["ID"])
        else:
            # Default to the most recent scan
            selected_scan_id = int(df_display.iloc[0]["ID"])

with right_col:
    st.markdown("### Historical Audit Inspector")
    if selected_scan_id:
        scan_data = get_scan_by_id(selected_scan_id)
        if scan_data:
            report = scan_data["report"]
            st.markdown(f"""
            <div class="sv-info-card" style="border-left: 4px solid #3B82F6;">
                <h4>{escape(scan_data['title'] or 'Untitled')}</h4>
                <p style="font-family:monospace;font-size:11px;color:#3B82F6;margin-bottom:8px;">{escape(scan_data['url'] or '')}</p>
                <div style="font-size:12px;color:#94A3B8;">Audited on: {escape(scan_data['timestamp'] or '')}</div>
                <hr style="border-color:#334155; margin:12px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:24px; font-weight:800; color:white;">{scan_data['overall_score']}</span>
                        <span style="font-size:12px; color:#64748B;">/100</span>
                    </div>
                    <span class="sv-score-badge badge-blue">{escape(scan_data['grade'] or '')} Grade</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sub-scores
            st.markdown("##### Category Subscores")
            gauges_html = f"""
            <div class="sv-gauge-grid" style="grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px;">
                {render_gauge("Security", report['security']['security_score'])}
                {render_gauge("Access", report['accessibility']['accessibility_score'])}
                {render_gauge("Perf", report['performance']['performance_score'])}
                {render_gauge("SEO", report['seo']['seo_score'])}
            </div>
            """
            st.markdown(gauges_html, unsafe_allow_html=True)
            
            # Action buttons
            b1, b2 = st.columns(2)
            
            # Load screenshot
            st.markdown("##### Screenshot at Scan Time")
            try:
                img = Image.open(scan_data["screenshot_path"])
                st.image(img, width=None)
            except Exception:
                st.markdown("*(Screenshot unavailable)*")
                
            # Delete scan button
            with b2:
                if st.button("🗑️ Delete Audit Record", type="secondary", key=f"del_{selected_scan_id}"):
                    delete_scan(selected_scan_id)
                    st.success("Record deleted successfully!")
                    st.rerun()
                    
            with b1:
                # Let user jump to this website scan URL by setting session state and rerunning
                if st.button("🚀 Re-Run Audit Now", type="primary", key=f"rerun_{selected_scan_id}"):
                    st.session_state["website"] = scan_data["url"]
                    st.switch_page("pages/2_📊_Dashboard.py")
        else:
            st.warning("Selected scan details could not be loaded.")
    else:
        st.info("Select an audit from the table to inspect details.")

# =====================================================
# Overall Performance Chart across all domains
# =====================================================
st.divider()
st.markdown("### Score Comparisons")

if len(history) > 1:
    comp_df = pd.DataFrame(history)
    comp_df["timestamp"] = pd.to_datetime(comp_df["timestamp"])
    
    # Bar chart of recent scans
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=comp_df["title"].apply(lambda x: (x[:15] + '...') if x and len(x) > 15 else x),
        y=comp_df["overall_score"],
        marker_color='#5EEAD4',
        name="Overall Score"
    ))
    fig.update_layout(
        title="Comparison of Audited Sites Scores",
        xaxis=dict(
            title="Website Title",
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
        height=280,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, width='stretch')
