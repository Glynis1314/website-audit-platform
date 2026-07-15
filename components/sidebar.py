import streamlit as st

def _render_brand():
    """Render the sidebar brand/logo."""
    st.sidebar.markdown(
        """
        <div class="sv-sidebar-brand" style="border-bottom: 1px solid var(--grid-line); padding-bottom: 16px; margin-bottom: 16px;">
            <h2 style="margin:0; font-family: var(--font-display); color: var(--signal-cyan); font-weight: 700; font-size: 1.4rem; letter-spacing: -0.02em;">SITE//VERIFY</h2>
            <p style="margin:0; font-family: var(--font-mono); font-size:0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em;">SYS_DIAG_CONSOLE</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar(active_page: str | None = None):
    """Render sidebar navigation using built-in page links."""
    _render_brand()
    
    st.sidebar.page_link("app.py", label="SYS_HOME", icon=":material/circle:")
    st.sidebar.markdown("<div style='border-top: 1px solid var(--grid-line); margin: 2px 0;'></div>", unsafe_allow_html=True)
    st.sidebar.page_link("pages/2_📊_Dashboard.py", label="DIAG_DASHBOARD", icon=":material/circle:")
    st.sidebar.markdown("<div style='border-top: 1px solid var(--grid-line); margin: 2px 0;'></div>", unsafe_allow_html=True)
    st.sidebar.page_link("pages/4_📄_History.py", label="AUDIT_LOGS", icon=":material/circle:")
    st.sidebar.markdown("<div style='border-top: 1px solid var(--grid-line); margin: 2px 0;'></div>", unsafe_allow_html=True)
    st.sidebar.page_link("pages/3_📝_About.py", label="SYS_INFO", icon=":material/circle:")

    # Footer with status
    st.sidebar.markdown(
        '''
        <div class="sv-sidebar-footer" style="font-family: var(--font-mono); font-size: 10px; color: var(--text-muted); border-top: 1px solid var(--grid-line); padding-top: 16px; margin-top: 32px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span>SYS_SCANNER</span>
                <span style="color: var(--signal-cyan); font-weight: bold;">READY</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>CONSOLE_VER</span>
                <span>v1.2.0</span>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
