from bs4 import BeautifulSoup
from utils.scoring import rating_for_score, PERFORMANCE_THRESHOLDS

def analyze_performance(html, timing_data=None):
    """
    Analyze webpage structure and W3C Navigation Timing metrics.
    """
    soup = BeautifulSoup(html, "lxml")

    images = soup.find_all("img")
    scripts = soup.find_all("script")
    stylesheets = soup.find_all("link", rel="stylesheet")
    links = soup.find_all("a")
    forms = soup.find_all("form")

    html_size = len(html.encode("utf-8")) / 1024  # KB
    score = 100
    findings = []
    deductions = []
    performance_metrics = {}

    # 1. HTML Size Audit
    if html_size > 1000:
        score -= 20
        findings.append(f"Large HTML document ({round(html_size, 1)} KB). Optimizing code and minification is recommended.")
        deductions.append({
            "id": "large_html_document",
            "label": f"Large HTML document ({round(html_size, 1)} KB)",
            "points": 20,
            "category": "performance"
        })
    elif html_size > 500:
        score -= 10
        findings.append(f"Moderately large HTML document ({round(html_size, 1)} KB).")
        deductions.append({
            "id": "large_html_document",
            "label": f"Moderately large HTML document ({round(html_size, 1)} KB)",
            "points": 10,
            "category": "performance"
        })
    else:
        findings.append(f"HTML size is efficient ({round(html_size, 1)} KB).")

    # 2. JavaScript Bloat Audit
    inline_js = 0
    external_js = 0
    for s in scripts:
        if s.get("src"):
            external_js += 1
        else:
            inline_js += 1

    if len(scripts) > 30:
        score -= 10
        findings.append(f"High number of JavaScript resources ({len(scripts)} found: {external_js} external, {inline_js} inline).")
        deductions.append({
            "id": "javascript_bloat",
            "label": f"High number of JavaScript resources ({len(scripts)} found)",
            "points": 10,
            "category": "performance"
        })
    else:
        findings.append(f"JavaScript resource count is reasonable ({len(scripts)} found).")

    # 3. CSS Resource Audit
    inline_css = len(soup.find_all("style"))
    external_css = len(stylesheets)
    total_css = inline_css + external_css

    if total_css > 15:
        score -= 5
        findings.append(f"High number of CSS stylesheets ({total_css} detected: {external_css} external, {inline_css} inline).")
        deductions.append({
            "id": "css_bloat",
            "label": f"High number of CSS stylesheets ({total_css} detected)",
            "points": 5,
            "category": "performance"
        })
    else:
        findings.append(f"CSS stylesheet count is optimal ({total_css} detected).")

    # 4. Images Audit
    if len(images) > 40:
        score -= 10
        findings.append(f"Large number of image assets ({len(images)}). Consider implementing lazy loading or modern formats like WebP.")
        deductions.append({
            "id": "excessive_images",
            "label": f"Large number of image assets ({len(images)})",
            "points": 10,
            "category": "performance"
        })
    else:
        findings.append(f"Image asset count is lightweight ({len(images)} images).")

    # 5. Timing Metrics from W3C API
    if timing_data and isinstance(timing_data, dict) and timing_data.get("navigationStart", 0) > 0:
        # Calculate metric phases in milliseconds
        def get_delta(end_key, start_key):
            if timing_data.get(end_key, 0) > 0 and timing_data.get(start_key, 0) > 0:
                delta = timing_data[end_key] - timing_data[start_key]
                return max(0, delta)
            return 0

        dns_time = get_delta("domainLookupEnd", "domainLookupStart")
        tcp_time = get_delta("connectEnd", "connectStart")
        ttfb = get_delta("responseStart", "requestStart")
        response_time = get_delta("responseEnd", "responseStart")
        dom_processing = get_delta("domComplete", "domLoading")
        page_load = get_delta("loadEventEnd", "navigationStart")
        
        # Fallback if loadEventEnd is 0
        if page_load == 0:
            page_load = get_delta("domComplete", "navigationStart")
        if page_load == 0:
            page_load = get_delta("domInteractive", "navigationStart")

        performance_metrics = {
            "dns_lookup_ms": dns_time,
            "tcp_handshake_ms": tcp_time,
            "ttfb_ms": ttfb,
            "server_response_ms": response_time,
            "dom_processing_ms": dom_processing,
            "page_load_ms": page_load
        }

        # Deduct score based on latency limits
        # TTFB (Time to First Byte)
        if ttfb > 1000:
            score -= 15
            findings.append(f"Critical TTFB (Time to First Byte) latency: {ttfb}ms. Suggests slow host response.")
            deductions.append({
                "id": "slow_ttfb",
                "label": f"Critical TTFB (Time to First Byte) latency: {ttfb}ms",
                "points": 15,
                "category": "performance"
            })
        elif ttfb > 400:
            score -= 5
            findings.append(f"Sub-optimal TTFB (Time to First Byte) latency: {ttfb}ms.")
            deductions.append({
                "id": "slow_ttfb",
                "label": f"Sub-optimal TTFB (Time to First Byte) latency: {ttfb}ms",
                "points": 5,
                "category": "performance"
            })
        else:
            findings.append(f"Excellent server response latency (TTFB: {ttfb}ms).")

        # Full Page Load
        if page_load > 6000:
            score -= 20
            findings.append(f"Critical page load latency: {round(page_load / 1000, 2)}s. Recommended: < 3.0s.")
            deductions.append({
                "id": "slow_page_load",
                "label": f"Critical page load latency: {round(page_load / 1000, 2)}s",
                "points": 20,
                "category": "performance"
            })
        elif page_load > 3000:
            score -= 10
            findings.append(f"Slow page load latency: {round(page_load / 1000, 2)}s. Target is less than 3 seconds.")
            deductions.append({
                "id": "slow_page_load",
                "label": f"Slow page load latency: {round(page_load / 1000, 2)}s",
                "points": 10,
                "category": "performance"
            })
        else:
            findings.append(f"Page loaded rapidly in {round(page_load / 1000, 2)}s.")

        # DNS Lookup
        if dns_time > 200:
            score -= 5
            findings.append(f"Slightly slow DNS resolution time ({dns_time}ms).")
            deductions.append({
                "id": "slow_dns",
                "label": f"Slightly slow DNS resolution time ({dns_time}ms)",
                "points": 5,
                "category": "performance"
            })
    else:
        # Fallback or empty metrics
        performance_metrics = {
            "dns_lookup_ms": 0,
            "tcp_handshake_ms": 0,
            "ttfb_ms": 0,
            "server_response_ms": 0,
            "dom_processing_ms": 0,
            "page_load_ms": 0
        }
        findings.append("No W3C timing statistics available. Using HTML structure profiling only.")

    # Clamp Score
    score = max(score, 0)
    rating = rating_for_score(score, PERFORMANCE_THRESHOLDS)

    return {
        "performance_score": score,
        "performance_rating": rating,
        "html_size_kb": round(html_size, 2),
        "images": len(images),
        "scripts": len(scripts),
        "stylesheets": len(stylesheets),
        "links": len(links),
        "forms": len(forms),
        "inline_js": inline_js,
        "external_js": external_js,
        "inline_css": inline_css,
        "external_css": external_css,
        "metrics": performance_metrics,
        "findings": findings,
        "deductions": deductions
    }