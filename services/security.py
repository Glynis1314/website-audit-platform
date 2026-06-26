from bs4 import BeautifulSoup


def analyze_security(html, url):
    """
    Analyze website security features.
    """

    soup = BeautifulSoup(html, "lxml")

    score = 100
    findings = []

    # =========================
    # HTTPS Check
    # =========================

    if url.startswith("https://"):
        https = True
        findings.append("HTTPS is enabled.")
    else:
        https = False
        findings.append("Website is not using HTTPS.")
        score -= 20

    # =========================
    # Forms
    # =========================

    forms = soup.find_all("form")

    insecure_forms = 0
    password_fields = 0
    autocomplete_enabled = 0
    external_forms = 0

    for form in forms:

        action = form.get("action", "")

        # External form action
        if action.startswith("http") and url not in action:
            external_forms += 1
            score -= 5

        inputs = form.find_all("input")

        for field in inputs:

            field_type = field.get("type", "").lower()

            if field_type == "password":
                password_fields += 1

                if field.get("autocomplete", "").lower() != "off":
                    autocomplete_enabled += 1
                    score -= 5

        if action.startswith("http://"):
            insecure_forms += 1
            score -= 10

    # =========================
    # Meta Security Headers
    # =========================

    csp = soup.find(
        "meta",
        attrs={
            "http-equiv": "Content-Security-Policy"
        }
    )

    if csp:
        findings.append("Content Security Policy detected.")
    else:
        findings.append("No Content Security Policy found.")
        score -= 10

    # =========================
    # Score Limits
    # =========================

    score = max(score, 0)

    if score >= 85:
        level = "Good"

    elif score >= 60:
        level = "Moderate"

    else:
        level = "Poor"

    return {

        "security_score": score,

        "security_level": level,

        "https": https,

        "password_fields": password_fields,

        "autocomplete_enabled": autocomplete_enabled,

        "external_forms": external_forms,

        "insecure_forms": insecure_forms,

        "findings": findings

    }