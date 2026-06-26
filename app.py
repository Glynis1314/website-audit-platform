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
# Custom CSS
# =====================================================

st.markdown("""
<style>

.main{
    background:#f5f7fb;
}

h1{
    color:#0f172a;
}

.stButton>button{
    width:100%;
    height:52px;
    border-radius:10px;
    font-size:17px;
    font-weight:bold;
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:12px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# Header
# =====================================================

st.title("🌐 SiteVerify")

st.caption(
    "Intelligent Website Audit & Form Analysis Platform"
)

st.info("""
SiteVerify performs automated website inspection using Selenium,
analyzing website structure, forms, security, accessibility,
and performance to generate a comprehensive audit report.
""")


# =====================================================
# URL Input
# =====================================================

website = st.text_input(
    "Website URL",
    placeholder="https://example.com"
)

scan = st.button(
    "🚀 Scan Website"
)


# =====================================================
# Scan Website
# =====================================================

if scan:

    if website.strip() == "":

        st.error(
            "Please enter a valid website URL."
        )

        st.stop()

    with st.spinner("Scanning website..."):

        scan_result = scan_website(
            website
        )

    if not scan_result["success"]:

        st.error(
            scan_result["error"]
        )

        st.stop()

    html = scan_result["html"]

    form_report = analyze_forms(
        html
    )

    security_report = analyze_security(
        html,
        scan_result["url"]
    )

    accessibility_report = analyze_accessibility(
        html
    )

    performance_report = analyze_performance(
        html
    )

    report = generate_report(

        scan_result,

        form_report,

        security_report,

        accessibility_report,

        performance_report

    )
    # =====================================================
    # Website Score Dashboard
    # =====================================================

    st.divider()

    st.header("📊 Website Audit Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Overall Score",
            f"{report['overall_score']}/100"
        )

        st.caption(
            f"Grade : {report['grade']}"
        )

    with col2:

        st.metric(
            "Security",
            f"{report['security']['security_score']}/100"
        )

        st.caption(
            report["security"]["security_level"]
        )

    with col3:

        st.metric(
            "Accessibility",
            f"{report['accessibility']['accessibility_score']}/100"
        )

        st.caption(
            report["accessibility"]["accessibility_level"]
        )

    with col4:

        st.metric(
            "Performance",
            f"{report['performance']['performance_score']}/100"
        )

        st.caption(
            report["performance"]["performance_rating"]
        )



    st.divider()



    # =====================================================
    # Website Information
    # =====================================================

    left, right = st.columns([2, 1])

    with left:

        st.subheader("🌐 Website Information")

        st.write(
            f"**Title:** {report['website']['title']}"
        )

        st.write(
            f"**URL:** {report['website']['url']}"
        )

        st.write(
            f"**Overall Status:** {report['status']}"
        )

        st.success(
            f"Website Grade : {report['grade']}"
        )


    with right:

        st.subheader("📸 Screenshot")

        try:

            image = Image.open(

                report["website"]["screenshot"]

            )

            st.image(

                image,

                use_container_width=True

            )

        except:

            st.warning(

                "Screenshot unavailable."

            )



    st.divider()



    # =====================================================
    # Quick Statistics
    # =====================================================

    st.subheader("📈 Quick Statistics")

    stat1, stat2, stat3, stat4 = st.columns(4)

    stat1.metric(

        "Forms",

        report["forms"]["forms_found"]

    )

    stat2.metric(

        "Input Fields",

        report["forms"]["total_inputs"]

    )

    stat3.metric(

        "Buttons",

        report["forms"]["total_buttons"]

    )

    stat4.metric(

        "Links",

        report["performance"]["links"]

    )



    st.divider()

    # =====================================================
    # Form Intelligence
    # =====================================================

    st.header("📝 Form Intelligence")

    forms = report["forms"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Forms Found",
        forms["forms_found"]
    )

    col2.metric(
        "Email Fields",
        forms["email_fields"]
    )

    col3.metric(
        "Password Fields",
        forms["password_fields"]
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Search Fields",
        forms["search_fields"]
    )

    col5.metric(
        "Hidden Fields",
        forms["hidden_fields"]
    )

    col6.metric(
        "Checkboxes",
        forms["checkbox_fields"]
    )

    if forms["form_details"]:

        st.subheader("Detected Forms")

        st.dataframe(
            forms["form_details"],
            use_container_width=True
        )

    else:

        st.success(
            "No forms detected on this website."
        )

    st.divider()



    # =====================================================
    # Security Analysis
    # =====================================================

    st.header("🔒 Security Analysis")

    security = report["security"]

    left, right = st.columns([1, 2])

    with left:

        st.metric(
            "Security Score",
            f"{security['security_score']}/100"
        )

        st.metric(
            "Security Level",
            security["security_level"]
        )

    with right:

        st.subheader("Security Findings")

        for item in security["findings"]:

            st.write("✅", item)

    st.divider()



    # =====================================================
    # Accessibility
    # =====================================================

    st.header("♿ Accessibility Analysis")

    accessibility = report["accessibility"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Accessibility Score",
        f"{accessibility['accessibility_score']}/100"
    )

    col2.metric(
        "Missing Alt Tags",
        accessibility["missing_alt"]
    )

    col3.metric(
        "Unlabelled Inputs",
        accessibility["unlabeled_inputs"]
    )

    col4.metric(
        "Empty Buttons",
        accessibility["empty_buttons"]
    )

    st.subheader("Accessibility Findings")

    for item in accessibility["findings"]:

        st.write("✔", item)

    st.divider()

    # =====================================================
    # Performance Analysis
    # =====================================================

    st.header("⚡ Performance Analysis")

    performance = report["performance"]

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Performance Score",
        f"{performance['performance_score']}/100"
    )

    p2.metric(
        "HTML Size",
        f"{performance['html_size_kb']} KB"
    )

    p3.metric(
        "Images",
        performance["images"]
    )

    p4.metric(
        "Scripts",
        performance["scripts"]
    )

    p5, p6, p7 = st.columns(3)

    p5.metric(
        "Stylesheets",
        performance["stylesheets"]
    )

    p6.metric(
        "Links",
        performance["links"]
    )

    p7.metric(
        "Forms",
        performance["forms"]
    )

    st.subheader("Performance Findings")

    for item in performance["findings"]:

        st.write("📌", item)

    st.divider()


    # =====================================================
    # Overall Website Health
    # =====================================================

    st.header("💻 Website Health")

    score = report["overall_score"]

    if score >= 90:

        st.success(
            f"Overall Website Score : {score}/100\n\nExcellent website quality."
        )

    elif score >= 80:

        st.info(
            f"Overall Website Score : {score}/100\n\nGood website quality."
        )

    elif score >= 70:

        st.warning(
            f"Overall Website Score : {score}/100\n\nAverage website quality."
        )

    else:

        st.error(
            f"Overall Website Score : {score}/100\n\nWebsite requires improvements."
        )

    st.metric(
        "Website Grade",
        report["grade"]
    )

    st.metric(
        "Overall Status",
        report["status"]
    )

    st.divider()


    # =====================================================
    # Recommendations
    # =====================================================

    st.header("💡 Recommendations")

    recommendations = report["recommendations"]

    if recommendations:

        for recommendation in recommendations:

            st.write(
                "✅",
                recommendation
            )

    else:

        st.success(
            "No recommendations. Website looks healthy."
        )

    st.divider()


    # =====================================================
    # Raw Report (Developer View)
    # =====================================================

    with st.expander("🛠 View Raw Report"):

        st.json(report)

    st.divider()

    # =====================================================
    # Generate PDF Report
    # =====================================================

    st.header("📄 Export Audit Report")

    st.write(
        "Generate a professional PDF containing the complete website audit."
    )

    if st.button(
        "📄 Generate PDF Report",
        key="generate_pdf"
    ):

        with st.spinner(
            "Generating report..."
        ):

            pdf_path = generate_pdf(
                report
            )

        st.success(
            "PDF generated successfully!"
        )

        with open(
            pdf_path,
            "rb"
        ) as pdf_file:

            st.download_button(

                label="⬇ Download Audit Report",

                data=pdf_file,

                file_name="SiteVerify_Report.pdf",

                mime="application/pdf",

                key="download_pdf"

            )


    st.divider()


    # =====================================================
    # Scan Summary
    # =====================================================

    st.header("📋 Scan Summary")

    summary1, summary2, summary3 = st.columns(3)

    with summary1:

        st.info(
            f"""
### Security

Score: **{report['security']['security_score']}/100**

Level: **{report['security']['security_level']}**
"""
        )

    with summary2:

        st.info(
            f"""
### Accessibility

Score: **{report['accessibility']['accessibility_score']}/100**

Level: **{report['accessibility']['accessibility_level']}**
"""
        )

    with summary3:

        st.info(
            f"""
### Performance

Score: **{report['performance']['performance_score']}/100**

Level: **{report['performance']['performance_rating']}**
"""
        )


    st.divider()


    # =====================================================
    # Footer
    # =====================================================

    st.markdown(
        """
---
### 🌐 SiteVerify

**Intelligent Website Audit & Form Analysis Platform**

Built using:

- Python
- Streamlit
- Selenium
- BeautifulSoup
- ReportLab

Developed for automated website inspection, accessibility auditing,
security analysis, form intelligence, and professional report generation.
"""
    )