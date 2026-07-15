from bs4 import BeautifulSoup
from utils.scoring import rating_for_score, SEO_THRESHOLDS

def analyze_seo(html):
    """
    Perform a comprehensive SEO audit on the webpage HTML.
    """
    soup = BeautifulSoup(html, "lxml")
    score = 100
    findings = []
    deductions = []
    seo_data = {}

    # 1. Page Title Check
    title_tag = soup.find("title")
    title_text = title_tag.text.strip() if title_tag else ""
    seo_data["title"] = title_text
    
    if not title_text:
        score -= 15
        findings.append("Missing page title.")
        deductions.append({
            "id": "seo_title_issues",
            "label": "Missing page title",
            "points": 15,
            "category": "seo"
        })
    elif len(title_text) < 30:
        score -= 5
        findings.append(f"Page title is too short ({len(title_text)} chars). Recommended: 30-60 characters.")
        deductions.append({
            "id": "seo_title_issues",
            "label": f"Page title is too short ({len(title_text)} chars)",
            "points": 5,
            "category": "seo"
        })
    elif len(title_text) > 60:
        score -= 5
        findings.append(f"Page title is too long ({len(title_text)} chars). Recommended: 30-60 characters.")
        deductions.append({
            "id": "seo_title_issues",
            "label": f"Page title is too long ({len(title_text)} chars)",
            "points": 5,
            "category": "seo"
        })
    else:
        findings.append("Page title length is optimal (30-60 characters).")

    # 2. Meta Description Check
    desc_tag = soup.find("meta", attrs={"name": "description"})
    desc_text = desc_tag.get("content", "").strip() if desc_tag else ""
    seo_data["meta_description"] = desc_text

    if not desc_text:
        score -= 15
        findings.append("Missing meta description.")
        deductions.append({
            "id": "seo_meta_description_issues",
            "label": "Missing meta description",
            "points": 15,
            "category": "seo"
        })
    elif len(desc_text) < 50:
        score -= 5
        findings.append(f"Meta description is too short ({len(desc_text)} chars). Recommended: 50-160 characters.")
        deductions.append({
            "id": "seo_meta_description_issues",
            "label": f"Meta description is too short ({len(desc_text)} chars)",
            "points": 5,
            "category": "seo"
        })
    elif len(desc_text) > 160:
        score -= 5
        findings.append(f"Meta description is too long ({len(desc_text)} chars). Recommended: 50-160 characters.")
        deductions.append({
            "id": "seo_meta_description_issues",
            "label": f"Meta description is too long ({len(desc_text)} chars)",
            "points": 5,
            "category": "seo"
        })
    else:
        findings.append("Meta description length is optimal (50-160 characters).")

    # 3. Viewport (Mobile Friendly) Check
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    seo_data["has_viewport"] = viewport_tag is not None
    if not viewport_tag:
        score -= 10
        findings.append("Missing viewport meta tag (not optimized for mobile devices).")
        deductions.append({
            "id": "missing_viewport_meta",
            "label": "Missing viewport meta tag",
            "points": 10,
            "category": "seo"
        })
    else:
        findings.append("Viewport meta tag detected (mobile-friendly configuration).")

    # 4. Heading Hierarchy Check
    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")
    
    seo_data["h1_count"] = len(h1s)
    seo_data["h2_count"] = len(h2s)
    seo_data["h3_count"] = len(h3s)

    if len(h1s) == 0:
        score -= 10
        findings.append("Missing <h1> tag. Every page should have exactly one <h1> heading.")
        deductions.append({
            "id": "seo_h1_issues",
            "label": "Missing <h1> tag",
            "points": 10,
            "category": "seo"
        })
    elif len(h1s) > 1:
        score -= 5
        findings.append(f"Multiple <h1> tags detected ({len(h1s)}). Recommended to use only one per page.")
        deductions.append({
            "id": "seo_h1_issues",
            "label": f"Multiple <h1> tags detected ({len(h1s)})",
            "points": 5,
            "category": "seo"
        })
    else:
        findings.append("Exactly one <h1> tag detected.")

    if len(h2s) == 0 and len(h3s) == 0:
        findings.append("No secondary headings (<h2>/<h3>) detected. Consider using them for logical structure.")
    else:
        findings.append(f"Structure includes {len(h2s)} <h2> and {len(h3s)} <h3> tags.")

    # 5. Social Sharing (Open Graph & Twitter Cards) Check
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_image = soup.find("meta", attrs={"property": "og:image"})
    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
    
    seo_data["has_og_tags"] = og_title is not None and og_image is not None
    seo_data["has_twitter_card"] = twitter_card is not None

    if seo_data["has_og_tags"]:
        findings.append("Open Graph tags (og:title, og:image) for rich social sharing are present.")
    else:
        score -= 5
        findings.append("Missing Open Graph metadata (og:title and/or og:image).")
        deductions.append({
            "id": "missing_og_tags",
            "label": "Missing Open Graph metadata (og:title and/or og:image)",
            "points": 5,
            "category": "seo"
        })

    if seo_data["has_twitter_card"]:
        findings.append("Twitter Card configuration is present.")
    else:
        findings.append("Missing Twitter Card configuration.")

    # 6. Canonical Link Check
    canonical = soup.find("link", attrs={"rel": "canonical"})
    seo_data["has_canonical"] = canonical is not None
    if not canonical:
        score -= 5
        findings.append("Missing canonical link. A canonical tag prevents duplicate content issues.")
        deductions.append({
            "id": "missing_canonical_link",
            "label": "Missing canonical link",
            "points": 5,
            "category": "seo"
        })
    else:
        findings.append("Canonical URL link detected.")

    # 7. Image Alt Text Check (Also a major SEO factor)
    images = soup.find_all("img")
    missing_alt = 0
    for img in images:
        alt = img.get("alt")
        if alt is None or alt.strip() == "":
            missing_alt += 1
            
    seo_data["total_images"] = len(images)
    seo_data["images_missing_alt"] = missing_alt

    if len(images) > 0:
        if missing_alt > 0:
            percentage = round((missing_alt / len(images)) * 100, 1)
            score -= min(missing_alt * 2, 15)
            findings.append(f"{missing_alt} out of {len(images)} images ({percentage}%) are missing alt attributes.")
            deductions.append({
                "id": "missing_image_alt_seo",
                "label": f"{missing_alt} image(s) missing alt attributes",
                "points": min(missing_alt * 2, 15),
                "category": "seo"
            })
        else:
            findings.append("All images contain descriptive alt text.")
    else:
        findings.append("No images detected on page.")

    # Final Score clamp
    score = max(score, 0)
    rating = rating_for_score(score, SEO_THRESHOLDS)

    seo_data["seo_score"] = score
    seo_data["seo_rating"] = rating
    seo_data["findings"] = findings
    seo_data["deductions"] = deductions
    
    return seo_data
