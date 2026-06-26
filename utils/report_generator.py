def generate_report(

    scan_data,

    form_data,

    security_data,

    accessibility_data,

    performance_data

):
    """
    Combines the outputs of all analysis modules
    into a single report dictionary.
    """

    # =========================
    # Overall Website Score
    # =========================

    overall_score = round(

        (

            security_data["security_score"]

            +

            accessibility_data["accessibility_score"]

            +

            performance_data["performance_score"]

        ) / 3,

        1

    )

    if overall_score >= 90:

        grade = "A"

        status = "Excellent"

    elif overall_score >= 80:

        grade = "B"

        status = "Good"

    elif overall_score >= 70:

        grade = "C"

        status = "Average"

    else:

        grade = "D"

        status = "Needs Improvement"

    # =========================
    # Recommendations
    # =========================

    recommendations = []

    if not security_data["https"]:

        recommendations.append(

            "Enable HTTPS for secure communication."

        )

    if accessibility_data["missing_alt"] > 0:

        recommendations.append(

            "Add alt text to all images."

        )

    if accessibility_data["unlabeled_inputs"] > 0:

        recommendations.append(

            "Associate labels with all form inputs."

        )

    if security_data["autocomplete_enabled"] > 0:

        recommendations.append(

            "Disable autocomplete for password fields."

        )

    if performance_data["html_size_kb"] > 1000:

        recommendations.append(

            "Reduce HTML page size."

        )

    if performance_data["scripts"] > 30:

        recommendations.append(

            "Reduce JavaScript resources."

        )

    if len(recommendations) == 0:

        recommendations.append(

            "No major issues detected."

        )

    # =========================
    # Final Report
    # =========================

    report = {

        "website": {

            "title": scan_data["title"],

            "url": scan_data["url"],

            "screenshot": scan_data["screenshot"]

        },

        "overall_score": overall_score,

        "grade": grade,

        "status": status,

        "forms": form_data,

        "security": security_data,

        "accessibility": accessibility_data,

        "performance": performance_data,

        "recommendations": recommendations

    }

    return report