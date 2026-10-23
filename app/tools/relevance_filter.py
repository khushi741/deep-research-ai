import re
import math
from typing import List, Dict, Set, Tuple, Optional
from urllib.parse import urlparse
from app.utils.logging import get_logger

logger = get_logger("relevance_filter")

# Common English stop words
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", 
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", 
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", 
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", 
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", 
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", 
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", 
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", 
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", 
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", 
    "yourself", "yourselves"
}

# Domain categories for authority assessment
ACADEMIC_GOV_DOMAINS = {
    ".gov", ".edu", ".mil", "arxiv.org", "nature.com", "science.org", "sciencedirect.com",
    "ieee.org", "nih.gov", "ncbi.nlm.nih.gov", "springer.com", "cell.com", "pnas.org",
    "acm.org", "biorxiv.org", "medrxiv.org", "wiley.com", "frontiersin.org"
}

MAJOR_PRESS_DOMAINS = {
    "reuters.com", "bloomberg.com", "wsj.com", "ft.com", "bbc.com", "apnews.com",
    "nytimes.com", "economist.com", "theguardian.com", "techcrunch.com", "wired.com",
    "technologyreview.com", "arstechnica.com", "scientificamerican.com"
}

# Commercial spam / dealership / generic dictionary indicators
GENERIC_DICTIONARY_DOMAINS = {
    "dictionary.com", "merriam-webster.com", "thefreedictionary.com", "wiktionary.org",
    "cambridge.org/dictionary", "collinsdictionary.com", "vocabulary.com"
}


def tokenize(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens, filtering stop words and single characters."""
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    return [w for w in words if w not in STOP_WORDS]


def extract_key_phrases(query: str) -> List[str]:
    """Extract multi-word key phrases and compound terms from research query."""
    clean = re.sub(r"[^\w\s-]", " ", query.lower()).strip()
    words = [w for w in clean.split() if w not in STOP_WORDS]
    phrases = []
    
    # 2-grams and 3-grams
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            phrases.append(" ".join(words[i:i+n]))
    
    return phrases


class SemanticRelevanceFilter:
    """
    Evaluates semantic relevance and authority between a research topic and retrieved web content.
    Prevents unrelated sources (e.g. SOLID software design or Toyota dealerships for battery research)
    from entering the evidence pool.
    """

    @staticmethod
    def calculate_relevance(
        topic: str,
        page_title: str,
        page_content: str,
        url: str,
        subquestions: Optional[List[str]] = None
    ) -> Tuple[float, str, List[str]]:
        """
        Calculates a transparent relevance score from 0.0 to 1.0.
        Returns: (score, reasoning, credibility_signals)
        """
        title_lower = (page_title or "").lower()
        content_lower = (page_content or "").lower()
        url_lower = (url or "").lower()
        parsed_url = urlparse(url)
        domain = (parsed_url.netloc or "").lower()
        path = (parsed_url.path or "").lower()

        topic_tokens = set(tokenize(topic))
        if not topic_tokens:
            return 0.5, "Topic contains no distinct keywords.", []

        signals: List[str] = []
        negative_signals: List[str] = []

        # -------------------------------------------------------------
        # 1. IMMEDIATE IRRELEVANCE / HOMONYM & COMMERCIAL DISQUALIFICATION
        # -------------------------------------------------------------
        # A. Generic Dictionary or elementary state of matter
        if any(dict_dom in domain for dict_dom in GENERIC_DICTIONARY_DOMAINS) or (path == "/wiki/solid" and not any(sw in content_lower for sw in ["software", "object-oriented", "programming", "liskov", "design principles"])):
            return 0.05, "Rejected: Generic dictionary or elementary state-of-matter definition unrelated to technical topic.", ["Excluded: Dictionary / broad lexical definition"]

        # B. SOLID Software Principles vs Solid-State Materials
        if any(b_term in topic_tokens for b_term in ["battery", "batteries", "energy", "electrolyte", "anode", "cathode"]):
            if any(sw_term in content_lower or sw_term in title_lower for sw_term in ["object-oriented", "liskov", "single responsibility", "design principles", "martin"]):
                if not any(batt_term in content_lower for batt_term in ["battery", "batteries", "electrolyte", "lithium"]):
                    return 0.04, "Rejected: Homonym conflict — page discusses SOLID software design principles, not solid-state batteries.", ["Excluded: Software engineering homonym"]

        # C. Auto Dealership & Car Sales Pages vs Battery Engineering/Commercialization
        dealership_indicators = ["dealer", "inventory", "test drive", "schedule service", "financing", "specials", "lease", "showroom", "used-cars", "new-cars"]
        is_dealer = any(ind in domain or ind in path for ind in dealership_indicators)
        if is_dealer:
            sales_words = sum(1 for w in ["inventory", "contact us", "sales", "call us", "trade-in", "price", "showroom"] if w in content_lower)
            if sales_words >= 2 and not any(tech_w in content_lower for tech_w in ["wh/kg", "commercialization", "anode", "solid electrolyte", "quantumscape"]):
                return 0.08, "Rejected: Commercial automobile dealership sales/inventory page, not technical research.", ["Excluded: Commercial car dealership"]

        # -------------------------------------------------------------
        # 2. KEY PHRASE & MULTI-WORD N-GRAM MATCHING
        # -------------------------------------------------------------
        key_phrases = extract_key_phrases(topic)
        title_phrase_matches = sum(1 for phrase in key_phrases if phrase in title_lower)
        content_phrase_matches = sum(1 for phrase in key_phrases if phrase in content_lower)

        # -------------------------------------------------------------
        # 3. TOKEN OVERLAP & DENSITY CALCULATION
        # -------------------------------------------------------------
        title_tokens = set(tokenize(page_title))
        content_tokens = tokenize(page_content)
        total_content_words = len(content_tokens)

        if total_content_words < 15:
            return 0.10, "Rejected: Insufficient text content extracted from page.", ["Excluded: Thin content (<15 words)"]

        # Check overlap
        matched_tokens = topic_tokens.intersection(set(content_tokens))
        token_coverage = len(matched_tokens) / len(topic_tokens)

        # Title keyword match
        title_matched = topic_tokens.intersection(title_tokens)
        title_coverage = len(title_matched) / len(topic_tokens)

        # Frequency density of topic tokens in body
        token_occurrences = sum(content_tokens.count(t) for t in topic_tokens)
        density = token_occurrences / max(total_content_words, 100)

        # Subquestion overlap if provided
        subq_bonus = 0.0
        if subquestions:
            subq_matches = 0
            for sq in subquestions:
                sq_toks = set(tokenize(sq))
                if len(sq_toks.intersection(set(content_tokens))) >= 2:
                    subq_matches += 1
            subq_bonus = min(0.15, (subq_matches / max(len(subquestions), 1)) * 0.15)

        # -------------------------------------------------------------
        # 4. COMPOSITE RELEVANCE SCORING
        # -------------------------------------------------------------
        # Base score from keyword coverage (0.0 to 0.40)
        score = token_coverage * 0.40

        # Exact phrase matches in title (up to 0.25 bonus)
        if title_phrase_matches > 0:
            score += 0.25
            signals.append(f"Title contains exact key phrase match ({title_phrase_matches})")
        elif title_coverage >= 0.5:
            score += 0.15
            signals.append("Title matches core research keywords")

        # Key phrases in body content (up to 0.15 bonus)
        if content_phrase_matches > 0:
            score += min(0.15, content_phrase_matches * 0.05)
            signals.append(f"Content contains {content_phrase_matches} topic key phrases")

        # Density bonus (up to 0.10)
        if density >= 0.015:
            score += 0.10
            signals.append(f"High topic keyword density ({density*100:.1f}%)")
        elif density >= 0.005:
            score += 0.05

        score += subq_bonus
        if subq_bonus > 0:
            signals.append("Matches multiple research subquestions")

        # Critical penalty: If core topic words are missing
        if token_coverage < 0.4:
            score *= 0.4
            negative_signals.append(f"Low topic keyword coverage ({len(matched_tokens)}/{len(topic_tokens)} words)")

        # Cap between 0.0 and 1.0
        final_score = round(max(0.02, min(0.98, score)), 2)

        reasoning = (
            f"Semantic relevance score {final_score:.2f}: "
            f"Keyword coverage {len(matched_tokens)}/{len(topic_tokens)} ({int(token_coverage*100)}%), "
            f"{content_phrase_matches} phrase matches, title match={bool(title_matched)}."
        )

        all_signals = signals + negative_signals
        return final_score, reasoning, all_signals

    @staticmethod
    def assess_authority(url: str, title: str, content: str) -> Tuple[float, str, List[str]]:
        """
        Assesses domain and publisher authority objectively.
        Explains that authority is a heuristic credibility signal, not an absolute guarantee.
        """
        parsed = urlparse(url)
        domain = (parsed.netloc or "").lower()
        signals: List[str] = []

        is_academic_gov = any(domain.endswith(d) or d in domain for d in ACADEMIC_GOV_DOMAINS)
        is_major_press = any(domain.endswith(d) or d in domain for d in MAJOR_PRESS_DOMAINS)

        if is_academic_gov:
            auth_score = 0.92
            source_type = "Primary Academic / Government"
            signals.append("Peer-reviewed repository or official governmental publisher (.gov/.edu/arXiv/Nature)")
        elif is_major_press:
            auth_score = 0.82
            source_type = "Authoritative Journalism"
            signals.append("Established major international press or specialized technology publisher")
        elif domain.endswith(".org"):
            auth_score = 0.70
            source_type = "Non-Profit / Organization"
            signals.append("Non-profit or organizational domain (.org)")
        elif any(tech in domain for tech in ["ieee", "sciencedirect", "springer", "cell", "energy"]):
            auth_score = 0.85
            source_type = "Industry / Scientific Technical"
            signals.append("Specialized technical or scientific domain")
        else:
            auth_score = 0.55
            source_type = "Standard Web Publication"
            signals.append("Commercial or independent web source")

        # Check for citation indicators in content
        if any(term in content.lower() for term in ["doi:", "references", "published in", "abstract", "issn", "et al."]):
            auth_score = min(0.96, auth_score + 0.08)
            signals.append("Formal academic structure detected (DOI, references, or abstract)")

        auth_score = round(auth_score, 2)
        return auth_score, source_type, signals
