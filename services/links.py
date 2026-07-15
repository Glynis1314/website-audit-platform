from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.url_safety import safe_request

def check_link_status(url, timeout=4):
    """
    Checks the status of a single URL. Returns (url, status_code, is_broken).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # Use HEAD first to minimize bandwidth, fallback to GET if needed
        response = safe_request("head", url, headers=headers, timeout=timeout)
        status_code = response.status_code
        
        # Some servers block HEAD with 404/405/403, retry with GET
        if status_code in [403, 404, 405]:
            response = safe_request("get", url, headers=headers, timeout=timeout, stream=True)
            status_code = response.status_code
            
        # Treat status codes >= 400 as broken, except occasionally 403 (if cloudflare blocks scripts)
        is_broken = status_code >= 400
        return url, status_code, is_broken
    except (requests.exceptions.RequestException, ValueError) as e:
        return url, 0, True

def audit_links(html, base_url, max_workers=10):
    """
    Extracts all links from the page, verifies them concurrently,
    and returns a summary report of broken/working links.
    """
    soup = BeautifulSoup(html, "lxml")
    anchors = soup.find_all("a", href=True)
    
    unique_links = set()
    links_data = []
    
    for a in anchors:
        href = a["href"].strip()
        
        # Skip javascript links, mailto, tel, and anchor fragments
        if href.startswith(("javascript:", "mailto:", "tel:", "#")) or not href:
            continue
            
        # Resolve relative URLs
        absolute_url = urljoin(base_url, href)
        # Parse and sanitize (remove fragments for uniqueness check)
        parsed = urlparse(absolute_url)
        sanitized_url = parsed._replace(fragment="").geturl()
        
        if sanitized_url.startswith("http"):
            unique_links.add(sanitized_url)

    total_unique_links = len(unique_links)
    broken_links = []
    working_count = 0
    broken_count = 0

    # Limit to top 30 links to avoid excessive time and API abuse during user interaction
    links_to_test = sorted(list(unique_links))[:30]
    untested_count = max(0, total_unique_links - 30)

    # Use ThreadPoolExecutor to request status concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_link_status, url): url for url in links_to_test}
        
        for future in as_completed(futures):
            url, status_code, is_broken = future.result()
            if is_broken:
                broken_count += 1
                broken_links.append({
                    "url": url,
                    "status": status_code if status_code != 0 else "Connection Timeout/Failed"
                })
            else:
                working_count += 1

    return {
        "total_links_found": total_unique_links,
        "links_tested": len(links_to_test),
        "untested_count": untested_count,
        "working_links": working_count,
        "broken_links_count": broken_count,
        "broken_links": broken_links
    }
