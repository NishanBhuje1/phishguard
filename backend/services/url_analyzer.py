import os
import re
import requests
from urllib.parse import urlparse

_SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".pw", ".top", ".click", ".link"}
_BRAND_TYPOS = {"paypa1", "g00gle", "arnazon", "micosoft", "app1e", "faceb00k", "netfl1x"}
_URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "short.io", "rb.gy"}
_SPECIAL_CHARS = set("@.-_?=&%")
_IPV4_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def check_phishtank(url: str) -> bool:
    try:
        api_key = os.getenv("PHISHTANK_API_KEY", "")
        response = requests.post(
            "https://checkurl.phishtank.com/checkurl/",
            data={"url": url, "format": "json", "app_key": api_key},
            timeout=5,
        )
        data = response.json()
        return (
            data.get("results", {}).get("in_database", False)
            and data.get("results", {}).get("valid", False)
        )
    except Exception:
        return False  # fail-secure: API down → don't block the scan


def extract_features(url: str) -> dict:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""

    # 1. Total character length of the full URL string
    url_length = len(url)

    # 2. Count of special characters: @ . - _ ? = & %
    special_char_count = sum(1 for ch in url if ch in _SPECIAL_CHARS)

    # 3. Subdomains: split hostname, drop www, count everything except the last two parts
    parts = hostname.lower().split(".")
    parts = [p for p in parts if p and p != "www"]
    subdomain_count = max(0, len(parts) - 2)

    # 4. True if hostname is a bare IPv4 address
    has_ip_address = bool(_IPV4_RE.match(hostname))

    # 5. True if domain ends with a suspicious TLD
    suspicious_tld = any(hostname.lower().endswith(tld) for tld in _SUSPICIOUS_TLDS)

    # 6. True if the full URL contains a brand typo string
    url_lower = url.lower()
    has_brand_typo = any(typo in url_lower for typo in _BRAND_TYPOS)

    # 7. True if the hostname exactly matches a known URL shortener domain
    is_url_shortener = hostname.lower() in _URL_SHORTENERS

    # 8. Number of "/" in the path component only (urlparse already excludes "://")
    path_depth = path.count("/")

    # 9. PhishTank lookup (fail-secure: returns False if API unavailable)
    phishtank_match = check_phishtank(url)

    # 10. HTTPS — maps to sslfinal_state (33% of model importance)
    uses_https = parsed.scheme.lower() == "https"

    return {
        "url_length": url_length,
        "special_char_count": special_char_count,
        "subdomain_count": subdomain_count,
        "has_ip_address": has_ip_address,
        "suspicious_tld": suspicious_tld,
        "has_brand_typo": has_brand_typo,
        "is_url_shortener": is_url_shortener,
        "path_depth": path_depth,
        "phishtank_match": phishtank_match,
        "uses_https": uses_https,
    }
