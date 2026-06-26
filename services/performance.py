from bs4 import BeautifulSoup


def analyze_performance(html):
    """
    Analyze webpage structure and estimate performance.
    """

    soup = BeautifulSoup(html, "lxml")

    images = soup.find_all("img")
    scripts = soup.find_all("script")
    stylesheets = soup.find_all("link", rel="stylesheet")
    links = soup.find_all("a")
    forms = soup.find_all("form")

    html_size = len(html.encode("utf-8")) / 1024

    score = 100

    findings = []

    # =========================
    # HTML Size
    # =========================

    if html_size > 1500:

        score -= 20

        findings.append(
            "Large HTML document."
        )

    elif html_size > 800:

        score -= 10

        findings.append(
            "Moderately large HTML document."
        )

    else:

        findings.append(
            "HTML size is acceptable."
        )

    # =========================
    # JavaScript
    # =========================

    if len(scripts) > 30:

        score -= 10

        findings.append(
            "High number of JavaScript files."
        )

    else:

        findings.append(
            "JavaScript usage is reasonable."
        )

    # =========================
    # Images
    # =========================

    if len(images) > 50:

        score -= 10

        findings.append(
            "Large number of images."
        )

    else:

        findings.append(
            "Image count is reasonable."
        )

    # =========================
    # Stylesheets
    # =========================

    if len(stylesheets) > 10:

        score -= 5

        findings.append(
            "Many CSS stylesheets detected."
        )

    else:

        findings.append(
            "Stylesheet count is acceptable."
        )

    # =========================
    # Overall Rating
    # =========================

    score = max(score, 0)

    if score >= 85:

        rating = "Excellent"

    elif score >= 70:

        rating = "Good"

    elif score >= 50:

        rating = "Average"

    else:

        rating = "Poor"

    return {

        "performance_score": score,

        "performance_rating": rating,

        "html_size_kb": round(html_size, 2),

        "images": len(images),

        "scripts": len(scripts),

        "stylesheets": len(stylesheets),

        "links": len(links),

        "forms": len(forms),

        "findings": findings

    }