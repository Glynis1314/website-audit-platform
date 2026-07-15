from bs4 import BeautifulSoup


def analyze_accessibility(html):
    """
    Analyze webpage accessibility.
    """

    soup = BeautifulSoup(html, "lxml")

    score = 100
    findings = []

    # =========================
    # Page Title
    # =========================

    title = soup.find("title")

    if title and title.text.strip():
        findings.append("Page title found.")
    else:
        findings.append("Missing page title.")
        score -= 15

    # =========================
    # Images
    # =========================

    images = soup.find_all("img")

    missing_alt = 0

    for image in images:

        alt = image.get("alt")

        if alt is None or alt.strip() == "":
            missing_alt += 1

    if missing_alt > 0:
        findings.append(
            f"{missing_alt} image(s) missing alt text."
        )
        score -= min(missing_alt * 2, 20)
    else:
        findings.append("All images have alt text.")

    # =========================
    # Form Labels
    # =========================

    inputs = soup.find_all("input")

    unlabeled_inputs = 0

    for field in inputs:

        if field.get("type") in ["hidden", "submit", "button"]:
            continue

        has_label = False
        field_id = field.get("id")

        # 1. Check <label for="...">
        if field_id:
            label = soup.find("label", attrs={"for": field_id})
            if label is not None:
                has_label = True

        # 2. Check aria-label
        if not has_label:
            aria_label = field.get("aria-label")
            if aria_label and aria_label.strip():
                has_label = True

        # 3. Check aria-labelledby
        if not has_label:
            aria_labelledby = field.get("aria-labelledby")
            if aria_labelledby:
                ref_ids = aria_labelledby.split()
                for ref_id in ref_ids:
                    if ref_id.strip() and soup.find(id=ref_id.strip()):
                        has_label = True
                        break

        if not has_label:
            unlabeled_inputs += 1

    if unlabeled_inputs > 0:

        findings.append(
            f"{unlabeled_inputs} input field(s) missing labels."
        )

        score -= min(unlabeled_inputs * 2, 20)

    else:

        findings.append("All input fields have labels.")

    # =========================
    # Buttons
    # =========================

    buttons = soup.find_all("button")

    empty_buttons = 0

    for button in buttons:

        if button.get_text(strip=True) == "":
            empty_buttons += 1

    if empty_buttons > 0:

        findings.append(
            f"{empty_buttons} empty button(s) detected."
        )

        score -= min(empty_buttons * 5, 15)

    else:

        findings.append("All buttons contain text.")

    # =========================
    # Headings
    # =========================

    headings = soup.find_all(["h1", "h2", "h3"])

    if len(headings) == 0:

        findings.append(
            "No heading structure found."
        )

        score -= 10

    else:

        findings.append(
            f"{len(headings)} heading(s) detected."
        )

    # =========================
    # Final Score
    # =========================

    score = max(score, 0)

    if score >= 85:
        level = "Excellent"

    elif score >= 65:
        level = "Needs Improvement"

    else:
        level = "Poor"

    return {

        "accessibility_score": score,

        "accessibility_level": level,

        "missing_alt": missing_alt,

        "unlabeled_inputs": unlabeled_inputs,

        "empty_buttons": empty_buttons,

        "headings": len(headings),

        "findings": findings

    }