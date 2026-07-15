"""
URL Safety Utility

This module provides functions to validate URLs to protect against Server-Side 
Request Forgery (SSRF) attacks.

KNOWN LIMITATION (DNS Rebinding):
--------------------------------
This module validates the resolved IP addresses of a hostname at check-time. However, 
subsequent library calls (e.g. requests or Selenium) resolve DNS independently at 
actual connect-time. A sufficiently adversarial DNS server could return a safe IP 
during our check and then return an internal/private IP during the subsequent connection. 
This Time-of-Check to Time-of-Use (TOCTOU) gap is a known limitation when using 
high-level HTTP libraries and standard DNS resolvers.
"""

import socket
import ipaddress
import urllib.parse
import requests

def is_safe_public_url(url: str) -> tuple[bool, str]:
    """
    Validates if a URL is safe to query from the server.
    Ensures that the URL points to a public, standard web resource (port 80 or 443)
    and does not resolve to private, loopback, multicast, or reserved IPs.

    Returns:
        tuple[bool, str]: (is_safe, reason_if_unsafe)
    """
    if not url:
        return False, "URL is empty."

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        return False, f"Failed to parse URL: {str(e)}"

    # 1. Scheme Check
    if parsed.scheme not in ("http", "https"):
        return False, f"Invalid scheme '{parsed.scheme}'. Only http and https are allowed."

    # 2. Port Check
    port = parsed.port
    if port is not None:
        if parsed.scheme == "http" and port != 80:
            return False, f"Non-standard port {port} for HTTP scheme is rejected."
        if parsed.scheme == "https" and port != 443:
            return False, f"Non-standard port {port} for HTTPS scheme is rejected."

    # 3. Hostname Check
    hostname = parsed.hostname
    if not hostname:
        return False, "URL does not contain a valid host."

    # 4. Resolve DNS records (resolving A & AAAA records)
    try:
        # socket.getaddrinfo returns a list of 5-tuples: (family, type, proto, canonname, sockaddr)
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        return False, f"DNS resolution failed for hostname '{hostname}': {e.strerror}"
    except Exception as e:
        return False, f"Failed to resolve hostname '{hostname}': {str(e)}"

    if not addr_info:
        return False, f"DNS resolved to 0 addresses for host '{hostname}'."

    # 5. IP Address Verification
    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]

        # Explicitly clean up IPv6 scopes if present (e.g. fe80::1%lo0 -> fe80::1)
        if "%" in ip_str:
            ip_str = ip_str.split("%")[0]

        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False, f"Resolved IP address '{ip_str}' is malformed."

        # Reject private/loopback/link-local/multicast/reserved/unspecified ranges
        if ip.is_private:
            return False, f"Access to private IP address '{ip_str}' is forbidden."
        if ip.is_loopback:
            return False, f"Access to loopback IP address '{ip_str}' is forbidden."
        if ip.is_link_local:
            return False, f"Access to link-local IP address '{ip_str}' is forbidden."
        if ip.is_multicast:
            return False, f"Access to multicast IP address '{ip_str}' is forbidden."
        if ip.is_reserved:
            return False, f"Access to reserved IP address '{ip_str}' is forbidden."
        if ip.is_unspecified:
            return False, f"Access to unspecified IP address '{ip_str}' is forbidden."

        # Explicitly reject common cloud metadata addresses (AWS/GCP/Azure)
        if ip_str == "169.254.169.254" or ip_str.lower() == "fd00:ec2::254":
            return False, f"Access to cloud metadata IP address '{ip_str}' is forbidden."

    return True, ""

def safe_request(method: str, url: str, **kwargs) -> requests.Response:
    """
    Wrapper around requests.request that validates URL safety before launching the request.
    Manually follows redirects up to 5 hops, verifying the safety of every intermediate target.
    
    Raises:
        ValueError: If any target URL in the chain is found to be unsafe.
    """
    current_url = url
    max_hops = 5
    hops = 0

    # Ensure allow_redirects parameter is not passed directly to requests since we handle it manually
    kwargs = kwargs.copy()
    kwargs["allow_redirects"] = False

    while True:
        # Validate safety of the target URL before making the call
        is_safe, reason = is_safe_public_url(current_url)
        if not is_safe:
            raise ValueError(f"Unsafe URL encountered: {reason}")

        # Execute single request hop
        response = requests.request(method, current_url, **kwargs)

        # Check for HTTP redirect statuses (3xx)
        if 300 <= response.status_code < 400 and "Location" in response.headers:
            hops += 1
            if hops > max_hops:
                raise ValueError("Maximum redirect hops (5) exceeded.")

            redirect_url = response.headers["Location"]
            # Resolve relative redirects correctly
            current_url = urllib.parse.urljoin(current_url, redirect_url)
        else:
            break

    return response
