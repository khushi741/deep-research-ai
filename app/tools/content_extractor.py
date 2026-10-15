import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.text_processing import clean_text_content, truncate_text, extract_domain
from app.utils.logging import get_logger

logger = get_logger("content_extractor")


class HTMLContentExtractor:
    """Extracts readable article content, title, and metadata from raw HTML."""

    @staticmethod
    def extract_text_and_metadata(html: str, url: str) -> Tuple[str, str, Optional[str]]:
        """
        Parses raw HTML string and returns: (title, main_text, publication_date)
        """
        if not html or not html.strip():
            return "Untitled", "", None

        domain = extract_domain(url)
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            logger.warning(f"HTML parsing warning for {url}: {str(e)}")
            soup = BeautifulSoup(html, "html.events") if "html.events" in str(e) else BeautifulSoup("", "html.parser")

        # 1. Extract Page Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        
        if not title:
            title = f"Article from {domain}"

        # 2. Extract Publication Date from Meta Tags
        pub_date = HTMLContentExtractor._extract_pub_date(soup)

        # 3. Strip non-content / clutter elements
        for element in soup(["script", "style", "nav", "header", "footer", "iframe", "noscript", "aside", "form", "svg"]):
            element.decompose()

        # Target main content containers if available
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|post|article|body", re.I))
        target = main_content if main_content else soup.body or soup

        # Extract text with space separator
        raw_text = target.get_text(separator=" ", strip=True)
        cleaned_text = clean_text_content(raw_text)

        # Truncate text to safety limit
        final_text = truncate_text(cleaned_text, max_chars=settings.MAX_CONTENT_LENGTH_PER_PAGE)

        return title, final_text, pub_date

    @staticmethod
    def _extract_pub_date(soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date from common HTML meta tags."""
        meta_date_keys = [
            ("meta", {"property": "article:published_time"}),
            ("meta", {"name": "publication_date"}),
            ("meta", {"name": "date"}),
            ("meta", {"name": "DC.date.issued"}),
            ("time", {}),
        ]

        for tag_name, attrs in meta_date_keys:
            tag = soup.find(tag_name, attrs)
            if tag:
                date_val = tag.get("content") or tag.get("datetime") or tag.get_text()
                if date_val and isinstance(date_val, str) and len(date_val.strip()) >= 4:
                    return date_val.strip()[:25]  # Cap length

        return None
