from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.enums import TA_CENTER

from reportlab.lib.colors import darkblue

from reportlab.lib.units import inch

import os
from datetime import datetime


def generate_pdf(report):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    filename = "reports/siteverify_report.pdf"

    document = SimpleDocTemplate(
        filename
    )

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.textColor = darkblue

    elements = []

    # =========================
    # Title
    # =========================

    elements.append(

        Paragraph(
            "SiteVerify Website Audit Report",
            title_style
        )

    )

    elements.append(
        Spacer(1, 0.3 * inch)
    )

    # =========================
    # Generated Time
    # =========================

    elements.append(

        Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )

    )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Website
    # =========================

    elements.append(

        Paragraph(
            "<b>Website Information</b>",
            styles["Heading2"]
        )

    )

    elements.append(

        Paragraph(
            f"Title: {report['website']['title']}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"URL: {report['website']['url']}",
            styles["Normal"]
        )

    )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Overall Score
    # =========================

    elements.append(

        Paragraph(
            "<b>Overall Website Score</b>",
            styles["Heading2"]
        )

    )

    elements.append(

        Paragraph(
            f"Score : {report['overall_score']}/100",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Grade : {report['grade']}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Status : {report['status']}",
            styles["Normal"]
        )

    )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Form Analysis
    # =========================

    form = report["forms"]

    elements.append(

        Paragraph(
            "<b>Form Intelligence</b>",
            styles["Heading2"]
        )

    )

    elements.append(
        Paragraph(
            f"Forms Found : {form['forms_found']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Inputs : {form['total_inputs']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Buttons : {form['total_buttons']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Email Fields : {form['email_fields']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Password Fields : {form['password_fields']}",
            styles["Normal"]
        )
    )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Security
    # =========================

    security = report["security"]

    elements.append(

        Paragraph(
            "<b>Security Analysis</b>",
            styles["Heading2"]
        )

    )

    elements.append(

        Paragraph(
            f"Security Score : {security['security_score']}/100",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Security Level : {security['security_level']}",
            styles["Normal"]
        )

    )

    for item in security["findings"]:

        elements.append(

            Paragraph(
                "• " + item,
                styles["Normal"]
            )

        )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Accessibility
    # =========================

    access = report["accessibility"]

    elements.append(

        Paragraph(
            "<b>Accessibility Analysis</b>",
            styles["Heading2"]
        )

    )

    elements.append(

        Paragraph(
            f"Accessibility Score : {access['accessibility_score']}/100",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Accessibility Level : {access['accessibility_level']}",
            styles["Normal"]
        )

    )

    for item in access["findings"]:

        elements.append(

            Paragraph(
                "• " + item,
                styles["Normal"]
            )

        )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Performance
    # =========================

    performance = report["performance"]

    elements.append(

        Paragraph(
            "<b>Performance Overview</b>",
            styles["Heading2"]
        )

    )

    elements.append(

        Paragraph(
            f"Performance Score : {performance['performance_score']}/100",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"HTML Size : {performance['html_size_kb']} KB",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Images : {performance['images']}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Scripts : {performance['scripts']}",
            styles["Normal"]
        )

    )

    elements.append(

        Paragraph(
            f"Stylesheets : {performance['stylesheets']}",
            styles["Normal"]
        )

    )

    elements.append(
        Spacer(1, 0.2 * inch)
    )

    # =========================
    # Recommendations
    # =========================

    elements.append(

        Paragraph(
            "<b>Recommendations</b>",
            styles["Heading2"]
        )

    )

    for recommendation in report["recommendations"]:

        elements.append(

            Paragraph(
                "• " + recommendation,
                styles["Normal"]
            )

        )

    elements.append(
        Spacer(1, 0.4 * inch)
    )

    # =========================
    # Footer
    # =========================

    elements.append(

        Paragraph(
            "Generated by SiteVerify",
            styles["Italic"]
        )

    )

    document.build(elements)

    return filename