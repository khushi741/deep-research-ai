import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


def normalize_url(url: str) -> str:
    """
    Normalizes a URL by converting host to lowercase, removing default ports,
    stripping tracking query parameters (utm_*), and removing trailing slashes.
    """
    if not url:
        return ""
    
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Remove standard ports
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    elif netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    # Filter out tracking query params
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = [
        (k, v) for k, v in query_params 
        if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid", "ref", "source"}
    ]
    new_query = urlencode(filtered_params)

    path = parsed.path.rstrip("/")
    if not path:
        path = ""

    normalized = urlunparse((scheme, netloc, path, parsed.params, new_query, ""))
    return normalized


def clean_text_content(text: str) -> str:
    """Cleans extracted raw webpage text, collapsing extra whitespace and line breaks."""
    if not text:
        return ""

    # Replace non-breaking spaces and normalize whitespace
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """Safely truncates text to a maximum character length."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [Truncated after {max_chars} characters]"


def extract_domain(url: str) -> str:
    """Extracts domain name from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split("/")[0]
    except Exception:
        return "unknown"
