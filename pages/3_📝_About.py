import streamlit as st
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="About SiteVerify",
    page_icon="📝",
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
render_sidebar(active_page="pages/3_📝_About.py")

# =====================================================
# About Page
# =====================================================

st.markdown("""
<div class="sv-hero">
    <div class="sv-hero-eyebrow">ABOUT THE PROJECT // DOCUMENTATION</div>
    <h1>Site<span>Verify</span></h1>
    <p class="sv-hero-sub">
        This project is a comprehensive website analysis tool built with Python and Streamlit. 
        It provides a deep scan of any website to identify potential issues and areas for improvement.
    </p>
</div>
""", unsafe_allow_html=True)

# System Status Bar
st.markdown("""
<div class="sv-status-bar">
    <span class="sv-status-dot cyan"></span>
    <span>SYSTEM: SYSTEM INFORMATION MODE // DOCUMENTATION LOADS STABLE</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sv-info-card">
    <h3>Project Overview</h3>
    <p>
        SiteVerify is designed to help web developers, designers, and website owners to get a quick and detailed overview of their website's health. It covers several key areas of website analysis:
    </p>
    <ul>
        <li><b>Security Analysis</b>: Checks for common security vulnerabilities and best practices.</li>
        <li><b>Accessibility Analysis</b>: Evaluates the website's accessibility for users with disabilities.</li>
        <li><b>Performance Analysis</b>: Measures the website's performance and provides recommendations for improvement.</li>
        <li><b>Form Analysis</b>: Analyzes the forms on the website to ensure they are user-friendly and functional.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sv-info-card">
    <h3>Technologies Used</h3>
    <p>
        The following technologies were used to build this application:
    </p>
    <ul>
        <li><b>Python</b>: The core programming language for the application.</li>
        <li><b>Streamlit</b>: The web framework used to build the user interface.</li>
        <li><b>Selenium</b>: For web scraping and browser automation.</li>
        <li><b>BeautifulSoup</b>: For parsing HTML and XML documents.</li>
        <li><b>ReportLab</b>: For generating PDF reports.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sv-info-card">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
        <span style="font-family:var(--font-display);font-size:16px;font-weight:700;color:var(--text-primary);">SITEVERIFY WEB AUDIT SUITE v2.0</span>
    </div>
    <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px;line-height:1.5;">
        Intelligent Website Audit & Form Analysis Platform.
    </div>
</div>
""", unsafe_allow_html=True)
