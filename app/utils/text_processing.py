import re
import hashlib
from typing import List, Set, Tuple, Optional
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
        if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid", "ref", "source", "amp"}
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


def get_shingle_set(text: str, shingle_size: int = 3) -> Set[str]:
    """Generates a set of word shingles for near-duplicate and syndication detection."""
    words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text.lower())
    if len(words) < shingle_size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i+shingle_size]) for i in range(len(words) - shingle_size + 1)}


def calculate_jaccard_similarity(text1: str, text2: str) -> float:
    """Calculates Jaccard similarity between two texts based on word shingles."""
    s1 = get_shingle_set(text1)
    s2 = get_shingle_set(text2)
    if not s1 or not s2:
        return 0.0
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return round(intersection / union, 3) if union > 0 else 0.0


def is_syndicated_duplicate(text1: str, text2: str, threshold: float = 0.65) -> bool:
    """
    Determines if two texts are syndicated duplicates (e.g. copied press wire releases).
    Distinguishes independent corroboration from copy-paste syndication.
    """
    if not text1 or not text2:
        return False
    # If lengths are wildly different, not direct duplicates
    len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2))
    if len_ratio < 0.4:
        return False
    
    sim = calculate_jaccard_similarity(text1[:3000], text2[:3000])
    return sim >= threshold


def find_supporting_sentences(content: str, keywords: List[str], max_sentences: int = 3) -> str:
    """
    Extracts verbatim sentences from content that have highest keyword density.
    Ensures quotes are authentic and bounded.
    """
    if not content or not keywords:
        return content[:250] if content else ""
    
    # Split text into sentences
    sentences = re.split(r"(?<=[.!?])\s+", content)
    kw_set = {k.lower() for k in keywords if len(k) > 2}
    
    scored_sentences: List[Tuple[int, str]] = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) < 30 or len(s_clean) > 400:
            continue
        words = set(re.findall(r"\b\w+\b", s_clean.lower()))
        score = len(words.intersection(kw_set))
        if score > 0:
            scored_sentences.append((score, s_clean))
            
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored_sentences[:max_sentences]]
    
    if top_sentences:
        return " ".join(top_sentences)
    return content[:250].strip()
