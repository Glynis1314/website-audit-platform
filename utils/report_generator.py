from datetime import datetime
from utils.scoring import compute_overall_grade

def generate_report(
    scan_data,
    form_data,
    security_data,
    accessibility_data,
    performance_data,
    seo_data,
    link_data
):
    """
    Combines the outputs of all analysis modules (including SEO & Link Auditor)
    into a single comprehensive report dictionary.
    """

    # =========================
    # Overall Website Score
    # =========================
    # Include Security, Accessibility, Performance, and SEO in the average.
    overall_score = round(
        (
            security_data["security_score"]
            + accessibility_data["accessibility_score"]
            + performance_data["performance_score"]
            + seo_data["seo_score"]
        ) / 4,
        1
    )

    grade, status = compute_overall_grade(overall_score)

    # =========================
    # Recommendations compilation
    # =========================
    recommendations = []

    # 1. Security Recommendations
    if not security_data["https"]:
        recommendations.append("Enable HTTPS protocol immediately to secure transport data.")
    
    ssl_details = security_data.get("ssl_details", {})
    if ssl_details and not ssl_details.get("valid", True):
        recommendations.append(f"Resolve SSL Certificate issues: {ssl_details.get('error')}.")
    elif ssl_details and ssl_details.get("remaining_days", 999) < 30:
        recommendations.append(f"Renew SSL Certificate (expires in {ssl_details['remaining_days']} days).")

    if security_data.get("missing_headers"):
        recommendations.append(f"Configure missing HTTP security headers: {', '.join(security_data['missing_headers'])}.")

    if security_data["autocomplete_enabled"] > 0:
        recommendations.append("Disable autocomplete attribute on password input fields.")

    if security_data["insecure_forms"] > 0:
        recommendations.append("Update all form endpoints utilizing insecure HTTP ('http://') actions to secure HTTPS.")

    # 2. Accessibility Recommendations
    if accessibility_data["missing_alt"] > 0:
        recommendations.append("Add descriptive alt text to all img tags to improve screen reader compatibility.")

    if accessibility_data["unlabeled_inputs"] > 0:
        recommendations.append("Associate labels with all form input fields using 'for' attribute matching.")

    if accessibility_data["empty_buttons"] > 0:
        recommendations.append("Add text content or accessible labels to empty button elements.")

    # 3. Performance Recommendations
    perf_metrics = performance_data.get("metrics", {})
    if perf_metrics.get("page_load_ms", 0) > 3000:
        load_sec = round(perf_metrics["page_load_ms"] / 1000, 2)
        recommendations.append(f"Improve page speed: The website loaded in {load_sec}s. Goal is < 3s. Minify JS/CSS assets.")

    if perf_metrics.get("ttfb_ms", 0) > 400:
        recommendations.append(f"Improve Server Response Time (TTFB: {perf_metrics['ttfb_ms']}ms). Optimize backend caching or hosting.")

    if performance_data["html_size_kb"] > 800:
        recommendations.append(f"Reduce overall HTML document size (currently {performance_data['html_size_kb']} KB).")

    if performance_data["scripts"] > 30:
        recommendations.append("Optimize performance by combining or eliminating redundant external JS files.")

    # 4. SEO Recommendations
    if not seo_data["title"]:
        recommendations.append("Add a primary title tag. Titles are critical for search engine indexing.")
    elif len(seo_data["title"]) > 60:
        recommendations.append("Shorten page title (currently > 60 chars) to prevent truncation in search result pages.")

    if not seo_data["meta_description"]:
        recommendations.append("Provide a meta description outlining page contents to improve click-through rates.")

    if not seo_data["has_viewport"]:
        recommendations.append("Define a viewport meta tag with width=device-width to enable mobile responsive layouts.")

    if seo_data["h1_count"] == 0:
        recommendations.append("Incorporate exactly one <h1> tag for the main heading on the page.")
    elif seo_data["h1_count"] > 1:
        recommendations.append("Consolidate multiple <h1> tags into subheadings (<h2>/<h3>) to preserve logical heading hierarchy.")

    if not seo_data["has_canonical"]:
        recommendations.append("Add a canonical link tag to indicate the authoritative URL and prevent duplicate ranking penalties.")

    # 5. Broken Link Recommendations
    if link_data["broken_links_count"] > 0:
        recommendations.append(f"Repair or remove {link_data['broken_links_count']} broken link(s) on the webpage.")

    if len(recommendations) == 0:
        recommendations.append("No major issues detected. Excellent audit profile!")

    # =========================
    # Final Report aggregation
    # =========================
    report = {
        "website": {
            "title": scan_data["title"],
            "url": scan_data["url"],
            "screenshot": scan_data["screenshot"]
        },
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "overall_score": overall_score,
        "grade": grade,
        "status": status,
        "forms": form_data,
        "security": security_data,
        "accessibility": accessibility_data,
        "performance": performance_data,
        "seo": seo_data,
        "links": link_data,
        "recommendations": recommendations
    }

    return report