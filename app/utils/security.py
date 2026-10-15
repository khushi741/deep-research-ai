import ipaddress
import socket
import re
from urllib.parse import urlparse
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("security")

# Blocked IP Networks (Private, Loopback, Link-Local, Multicast, Reserved)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # Includes Cloud Metadata APIs (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_ip_blocked(ip_str: str) -> bool:
    """Check if an IP address falls within any blocked/private network."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_NETWORKS:
            if ip in net:
                return True
        return False
    except ValueError:
        return True


def validate_url_for_ssrf(url: str) -> tuple[bool, str]:
    """
    Validates a URL against SSRF vulnerabilities:
    1. Scheme check (only http/https allowed)
    2. Hostname resolution check (DNS resolution check against blocked IP ranges)
    """
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid type"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL parse error: {str(e)}"

    if parsed.scheme.lower() not in settings.ALLOWED_SCHEMES:
        return False, f"Forbidden scheme: '{parsed.scheme}'. Only http and https are allowed."

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    hostname_lower = hostname.lower()
    if hostname_lower in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or hostname_lower.endswith(".local"):
        return False, f"Access to localhost/local domain '{hostname}' is blocked."

    # DNS Resolution Check
    try:
        # Resolve hostname to IP addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            if is_ip_blocked(ip_str):
                return False, f"URL hostname '{hostname}' resolves to blocked IP '{ip_str}'."
    except socket.gaierror:
        return False, f"Failed to resolve DNS for hostname '{hostname}'."
    except Exception as e:
        return False, f"DNS resolution error for '{hostname}': {str(e)}"

    return True, "URL is safe"


def sanitize_untrusted_content(content: str) -> str:
    """
    Sanitizes untrusted web content to mitigate prompt injection attacks.
    Removes system prompt overrides and wraps external web text safely.
    """
    if not content:
        return ""

    # Remove attempts to inject system instruction delimiters or prompt overrides
    content = re.sub(r"<\/?(?:system|instruction|prompt|context)[^>]*>", "", content, flags=re.IGNORECASE)
    
    # Strip potential jailbreak patterns
    jailbreak_patterns = [
        r"IGNORE ALL PREVIOUS INSTRUCTIONS",
        r"DISREGARD PREVIOUS SYSTEM PROMPTS",
        r"YOU ARE NOW A",
    ]
    for pattern in jailbreak_patterns:
        content = re.sub(pattern, "[REDACTED_ATTEMPTED_INJECTION]", content, flags=re.IGNORECASE)

    return content


def wrap_untrusted_web_content(url: str, title: str, text: str) -> str:
    """Wraps retrieved web content inside XML tags to isolate it from system instructions."""
    clean_text = sanitize_untrusted_content(text)
    return (
        f'<untrusted_web_source url="{url}" title="{title}">\n'
        f'{clean_text}\n'
        f'</untrusted_web_source>'
    )
