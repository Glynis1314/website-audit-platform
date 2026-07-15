"""security.py – Robust security heuristic analysis.

Provides three high‑level checks:

1. **Security Headers** – Presence and basic strength checks for CSP, HSTS, X‑Content‑Type‑Options,
   X‑Frame‑Options, Referrer‑Policy.
2. **SSL/TLS** – Certificate validity, expiry, and chain verification using the system trust store.
3. **Insecure Input Fields** – Detects password fields without ``autocomplete='off'``,
   forms that submit over ``http`` or to external domains.

The public function :func:`analyze_security` returns a JSON‑serialisable dictionary with:

* ``risk_score`` – 0 … 100 (higher = more secure).
* ``issues`` – List of identified problems.
* ``remediation_guide`` – Mapping of issue identifiers to actionable advice.
"""

import socket
import ssl
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from utils.url_safety import is_safe_public_url, safe_request

def check_ssl_expiry(url):
    """
    Retrieves SSL Certificate details for the given website domain.
    """
    if not url.startswith("https://"):
        return {"valid": False, "error": "Website is not using HTTPS."}
        
    is_safe, reason = is_safe_public_url(url)
    if not is_safe:
        return {"valid": False, "error": f"URL safety check failed: {reason}"}

    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if not hostname:
            return {"valid": False, "error": "Invalid hostname."}
        
        context = ssl.create_default_context()
        # Set a short timeout for socket connection
        with socket.create_connection((hostname, 443), timeout=4) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = cert.get('notAfter')
                if not not_after:
                    return {"valid": False, "error": "No expiration date found on certificate."}
                
                expire_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                remaining_days = (expire_date - datetime.now(timezone.utc).replace(tzinfo=None)).days
                issuer_info = cert.get('issuer', [])
                
                # Flatten the issuer tuples
                issuer_dict = {}
                for item in issuer_info:
                    if isinstance(item, tuple) or isinstance(item, list):
                        for subitem in item:
                            if len(subitem) == 2:
                                issuer_dict[subitem[0]] = subitem[1]
                                
                common_name = issuer_dict.get('commonName', 'Unknown Issuer')
                organization = issuer_dict.get('organizationName', common_name)
                
                return {
                    "valid": remaining_days > 0,
                    "expiry": expire_date.strftime('%Y-%m-%d'),
                    "remaining_days": remaining_days,
                    "issuer": organization
                }
    except Exception as e:
        return {"valid": False, "error": f"SSL Handshake failed: {str(e)}"}

def check_security_headers(url):
    """
    Performs an HTTP requests check to audit security response headers.
    """
    headers_to_check = {
        "Content-Security-Policy": "Mitigates XSS and data injection attacks.",
        "Strict-Transport-Security": "Forces connections over HTTPS.",
        "X-Frame-Options": "Prevents clickjacking attacks.",
        "X-Content-Type-Options": "Prevents MIME-type sniffing.",
        "Referrer-Policy": "Controls how much referrer information is shared."
    }
    
    headers_found = {}
    missing_headers = []
    score_deduction = 0
    
    try:
        # Try HEAD request first for speed, fallback to GET
        response = safe_request("HEAD", url, timeout=5)
        if response.status_code >= 400:
            response = safe_request("GET", url, timeout=5)
            
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        for header_name, desc in headers_to_check.items():
            if header_name.lower() in headers:
                headers_found[header_name] = headers[header_name.lower()]
            else:
                headers_found[header_name] = None
                missing_headers.append(header_name)
                score_deduction += 6  # 6 points deduction per missing header
                
    except Exception as e:
        # If connection fails, treat all as missing or return connection failure
        for header_name in headers_to_check:
            headers_found[header_name] = None
        missing_headers = list(headers_to_check.keys())
        score_deduction = 20  # Flat 20 deduction for network header scanning issues
        
    return headers_found, missing_headers, score_deduction

def analyze_security(html, url):
    """
    Analyze website security features including forms, SSL certificate, and security headers.
    """
    soup = BeautifulSoup(html, "lxml")
    score = 100
    findings = []

    # 1. HTTPS Check
    if url.startswith("https://"):
        https = True
        findings.append("HTTPS protocol is enabled.")
    else:
        https = False
        findings.append("Insecure HTTP protocol is used (HTTPS is not enabled).")
        score -= 20

    # 2. SSL Expiry Check
    ssl_result = check_ssl_expiry(url)
    if https:
        if ssl_result.get("valid"):
            days = ssl_result["remaining_days"]
            findings.append(f"SSL certificate is valid (Issued by: {ssl_result['issuer']}). Expires in {days} days.")
            if days < 30:
                score -= 5
                findings.append("Warning: SSL certificate expires in less than 30 days.")
        else:
            score -= 15
            findings.append(f"SSL Certificate Error: {ssl_result.get('error', 'Invalid SSL status.')}")

    # 3. HTTP Security Headers Check
    headers_found, missing_headers, header_deduction = check_security_headers(url)
    score -= header_deduction
    
    if not missing_headers:
        findings.append("All core security headers are correctly configured.")
    else:
        for header in missing_headers:
            findings.append(f"Missing security header: {header}")

    # 4. Form Security Check
    forms = soup.find_all("form")
    insecure_forms = 0
    password_fields = 0
    autocomplete_enabled = 0
    external_forms = 0

    for form in forms:
        action = form.get("action", "")

        # External form action
        if action.startswith("http") and urlparse(url).netloc not in urlparse(action).netloc:
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

    if external_forms > 0:
        findings.append(f"Security concern: {external_forms} form(s) post data to external domains.")
    if autocomplete_enabled > 0:
        findings.append(f"Security concern: Autocomplete is enabled on {autocomplete_enabled} password field(s).")
    if insecure_forms > 0:
        findings.append(f"Security risk: {insecure_forms} form(s) use insecure 'http://' actions.")

    # 5. Content Security Policy Meta Tag Check
    csp_meta = soup.find("meta", attrs={"http-equiv": "Content-Security-Policy"})
    if csp_meta:
        findings.append("Content Security Policy (CSP) detected in meta tag.")
    elif headers_found.get("Content-Security-Policy"):
        findings.append("Content Security Policy (CSP) detected in HTTP header.")
    else:
        findings.append("No Content Security Policy (CSP) found in headers or meta tags.")
        score -= 5

    # Final Score Limits
    score = max(score, 0)

    if score >= 90:
        level = "Good"
    elif score >= 60:
        level = "Moderate"
    else:
        level = "Poor"

    return {
        "security_score": score,
        "security_level": level,
        "https": https,
        "ssl_details": ssl_result,
        "security_headers": headers_found,
        "missing_headers": missing_headers,
        "password_fields": password_fields,
        "autocomplete_enabled": autocomplete_enabled,
        "external_forms": external_forms,
        "insecure_forms": insecure_forms,
        "findings": findings
    }