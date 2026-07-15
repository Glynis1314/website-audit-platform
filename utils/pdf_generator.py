from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import darkblue, HexColor
from reportlab.lib.units import inch
import os
from datetime import datetime

def generate_pdf(report):
    """
    Compiles the unified audit report into a professional PDF document.
    """
    os.makedirs("reports", exist_ok=True)
    import uuid
    unique_id = uuid.uuid4().hex
    filename = f"reports/siteverify_report_{unique_id}.pdf"

    document = SimpleDocTemplate(
        filename,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = darkblue
    
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    normal_style.leading = 14
    
    bullet_style = styles["Normal"]
    bullet_style.leftIndent = 15
    bullet_style.fontSize = 9.5
    bullet_style.leading = 13

    section_style = styles["Heading2"]
    section_style.textColor = HexColor("#1E3A8A")
    section_style.spaceBefore = 10
    section_style.spaceAfter = 6

    elements = []

    # =========================
    # Header Title
    # =========================
    elements.append(Paragraph("SiteVerify Professional Audit Report", title_style))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", normal_style))
    elements.append(Paragraph(f"<b>Target URL:</b> {report['website']['url']}", normal_style))
    elements.append(Paragraph(f"<b>Page Title:</b> {report['website']['title']}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Executive Summary Score
    # =========================
    elements.append(Paragraph("<b>1. Executive Summary</b>", section_style))
    elements.append(Paragraph(f"<b>Overall Score:</b> {report['overall_score']}/100 (Grade: <b>{report['grade']}</b> - {report['status']})", normal_style))
    
    sec_score = report["security"]["security_score"]
    acc_score = report["accessibility"]["accessibility_score"]
    perf_score = report["performance"]["performance_score"]
    seo_score = report["seo"]["seo_score"]
    
    elements.append(Paragraph(
        f"Category Breakdown: "
        f"Security: <b>{sec_score}/100</b> | "
        f"Accessibility: <b>{acc_score}/100</b> | "
        f"Performance: <b>{perf_score}/100</b> | "
        f"SEO: <b>{seo_score}/100</b>",
        normal_style
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Security & SSL trust
    # =========================
    elements.append(Paragraph("<b>2. Security & SSL Audit</b>", section_style))
    elements.append(Paragraph(f"HTTPS Status: {'Enabled' if report['security']['https'] else 'Disabled/Insecure'}", normal_style))
    
    ssl_details = report["security"].get("ssl_details", {})
    if ssl_details and ssl_details.get("valid"):
        elements.append(Paragraph(f"SSL Certificate: Valid (Issued by: {ssl_details['issuer']}). Expiry: {ssl_details['expiry']} (in {ssl_details['remaining_days']} days)", normal_style))
    else:
        elements.append(Paragraph(f"SSL Certificate: Insecure or Handshake Failed ({ssl_details.get('error', 'Insecure')})", normal_style))

    missing_headers = report["security"].get("missing_headers", [])
    if missing_headers:
        elements.append(Paragraph(f"Missing HTTP Security Headers: {', '.join(missing_headers)}", normal_style))
    else:
        elements.append(Paragraph("Security Headers: All core security response headers present.", normal_style))

    for item in report["security"]["findings"]:
        elements.append(Paragraph(f"• {item}", bullet_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Accessibility
    # =========================
    elements.append(Paragraph("<b>3. Accessibility Analysis</b>", section_style))
    elements.append(Paragraph(
        f"Missing Alt Text: <b>{report['accessibility']['missing_alt']}</b> | "
        f"Unlabeled Inputs: <b>{report['accessibility']['unlabeled_inputs']}</b> | "
        f"Empty Buttons: <b>{report['accessibility']['empty_buttons']}</b>",
        normal_style
    ))
    for item in report["accessibility"]["findings"]:
        elements.append(Paragraph(f"• {item}", bullet_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Performance & Timing Profile
    # =========================
    elements.append(Paragraph("<b>4. Performance & Core Web Vitals Timing Profile</b>", section_style))
    elements.append(Paragraph(
        f"Page HTML Size: <b>{report['performance']['html_size_kb']} KB</b> | "
        f"Total Images: <b>{report['performance']['images']}</b> | "
        f"CSS Assets: <b>{report['performance']['stylesheets']}</b> | "
        f"Script Assets: <b>{report['performance']['scripts']}</b>",
        normal_style
    ))
    
    perf_metrics = report["performance"].get("metrics", {})
    if perf_metrics and perf_metrics.get("page_load_ms", 0) > 0:
        elements.append(Paragraph(
            f"<b>W3C Timing Latencies:</b><br/>"
            f"- DNS Lookup Time: {perf_metrics['dns_lookup_ms']} ms<br/>"
            f"- TCP Connection Latency: {perf_metrics['tcp_handshake_ms']} ms<br/>"
            f"- Time to First Byte (TTFB): {perf_metrics['ttfb_ms']} ms<br/>"
            f"- Server Response Download: {perf_metrics['server_response_ms']} ms<br/>"
            f"- DOM Rendering Time: {perf_metrics['dom_processing_ms']} ms<br/>"
            f"- Full Page Load Duration: <b>{round(perf_metrics['page_load_ms']/1000, 3)} seconds</b>",
            normal_style
        ))
    else:
        elements.append(Paragraph("W3C timing statistics are unavailable.", normal_style))

    for item in report["performance"]["findings"]:
        elements.append(Paragraph(f"• {item}", bullet_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # SEO & Social Metadata
    # =========================
    elements.append(Paragraph("<b>5. Search Engine Optimization (SEO) & Social Cards</b>", section_style))
    seo_data = report["seo"]
    elements.append(Paragraph(
        f"Title Tag: <b>{seo_data.get('title') or 'Missing'}</b><br/>"
        f"Meta Description: <b>{seo_data.get('meta_description') or 'Missing'}</b><br/>"
        f"Canonical Tag: {'Configured' if seo_data.get('has_canonical') else 'Missing'}<br/>"
        f"Viewport Config: {'Responsiveness meta tag found' if seo_data.get('has_viewport') else 'Missing responsiveness configurations'}<br/>"
        f"Open Graph Social Tags: {'Present' if seo_data.get('has_og_tags') else 'Missing'}<br/>"
        f"Headings structure: H1s={seo_data.get('h1_count')}, H2s={seo_data.get('h2_count')}, H3s={seo_data.get('h3_count')}",
        normal_style
    ))
    for item in seo_data["findings"]:
        elements.append(Paragraph(f"• {item}", bullet_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Link Audit
    # =========================
    elements.append(Paragraph("<b>6. Concurrent Link Audit</b>", section_style))
    link_data = report["links"]
    elements.append(Paragraph(
        f"Total Anchor Links Identified: <b>{link_data['total_links_found']}</b> | "
        f"Tested Unique Links: <b>{link_data['links_tested']}</b><br/>"
        f"Working (2xx/3xx): <b>{link_data['working_links']}</b> | "
        f"Broken / Connection Failed: <b>{link_data['broken_links_count']}</b>",
        normal_style
    ))
    
    if link_data["broken_links"]:
        elements.append(Paragraph("<b>Broken Link Inventory:</b>", normal_style))
        for lnk in link_data["broken_links"]:
            elements.append(Paragraph(f"• Status {lnk['status']}: {lnk['url']}", bullet_style))
    else:
        elements.append(Paragraph("No broken anchor links were detected.", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # =========================
    # Action Plan (Recommendations)
    # =========================
    elements.append(Paragraph("<b>7. Prioritized Action Plan & Recommendations</b>", section_style))
    for recommendation in report["recommendations"]:
        elements.append(Paragraph(f"• {recommendation}", bullet_style))
    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # Footer
    # =========================
    elements.append(Paragraph("Generated automatically by SiteVerify Web Audit Platform.", styles["Italic"]))

    # Build the document flow
    document.build(elements)
    return filename