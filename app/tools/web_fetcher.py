import httpx
import asyncio
from typing import Optional, List
from app.config import settings
from app.models.research import ExtractedContent
from app.tools.content_extractor import HTMLContentExtractor
from app.utils.security import validate_url_for_ssrf
from app.utils.text_processing import extract_domain, normalize_url
from app.utils.logging import get_logger

logger = get_logger("web_fetcher")

# Browser User-Agent header for fetching web pages
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36 DeepResearchAI/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class AsyncWebFetcher:
    """
    Asynchronous Web Fetcher with built-in SSRF validation,
    redirect security re-verification, and HTML content extraction.
    """

    def __init__(self, timeout_seconds: Optional[int] = None):
        self.timeout = timeout_seconds or settings.HTTP_TIMEOUT_SECONDS

    async def fetch_url(self, url: str) -> ExtractedContent:
        """Fetches a single URL safely, returning ExtractedContent."""
        domain = extract_domain(url)

        # 1. SSRF Safety Check
        is_safe, error_msg = validate_url_for_ssrf(url)
        if not is_safe:
            logger.warning(f"Blocked SSRF risk for URL '{url}': {error_msg}")
            return ExtractedContent(
                url=url,
                title="Access Denied (Security Block)",
                content="",
                domain=domain,
                error=f"SSRF Protection Block: {error_msg}"
            )

        # 2. Asynchronous HTTP Fetching with Redirect Validation
        try:
            async with httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                timeout=httpx.Timeout(self.timeout, connect=5.0),
                follow_redirects=False,  # Manually handle redirects for SSRF safety
                max_redirects=3,
            ) as client:
                curr_url = url
                redirect_count = 0
                max_redirects = 3
                response = None

                while redirect_count <= max_redirects:
                    resp = await client.get(curr_url)
                    
                    if resp.is_redirect and "location" in resp.headers:
                        redirect_count += 1
                        redirect_target = resp.headers["location"]
                        
                        # Resolve relative redirect URLs
                        if redirect_target.startswith("/"):
                            parsed = httpx.URL(curr_url)
                            redirect_target = f"{parsed.scheme}://{parsed.netloc}{redirect_target}"

                        # Re-validate redirect target for SSRF!
                        safe_redirect, r_msg = validate_url_for_ssrf(redirect_target)
                        if not safe_redirect:
                            return ExtractedContent(
                                url=url,
                                title="Redirect Blocked",
                                content="",
                                domain=domain,
                                error=f"Redirect to unsafe host blocked: {r_msg}"
                            )
                        curr_url = redirect_target
                    else:
                        response = resp
                        break

                if response is None:
                    return ExtractedContent(
                        url=url,
                        title="Too Many Redirects",
                        content="",
                        domain=domain,
                        error="Exceeded maximum allowed redirects"
                    )

                # Check HTTP status code
                if response.status_code == 403 or response.status_code == 401:
                    return ExtractedContent(
                        url=url,
                        title="Access Restricted",
                        content="",
                        domain=domain,
                        error=f"HTTP {response.status_code}: Access restricted or paywalled site."
                    )
                elif response.status_code != 200:
                    return ExtractedContent(
                        url=url,
                        title="Fetch Failed",
                        content="",
                        domain=domain,
                        error=f"HTTP Status {response.status_code}"
                    )

                # Content Type Check
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type and "text/plain" not in content_type and "application/xhtml" not in content_type:
                    return ExtractedContent(
                        url=url,
                        title="Unsupported Format",
                        content="",
                        domain=domain,
                        error=f"Unsupported Content-Type: '{content_type}'"
                    )

                # Extract Text and Metadata
                html_text = response.text
                title, main_text, pub_date = HTMLContentExtractor.extract_text_and_metadata(html_text, curr_url)

                return ExtractedContent(
                    url=url,
                    title=title,
                    content=main_text,
                    domain=domain,
                    published_date=pub_date
                )

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching URL: {url}")
            return ExtractedContent(
                url=url,
                title="Request Timeout",
                content="",
                domain=domain,
                error=f"Request timed out after {self.timeout}s"
            )
        except Exception as e:
            logger.error(f"Error fetching URL '{url}': {str(e)}")
            return ExtractedContent(
                url=url,
                title="Fetch Error",
                content="",
                domain=domain,
                error=f"Fetch failed: {str(e)}"
            )

    async def fetch_batch(self, urls: List[str], max_concurrency: int = 5) -> List[ExtractedContent]:
        """Fetches multiple URLs concurrently with limited concurrency."""
        semaphore = asyncio.Semaphore(max_concurrency)

        async def sem_fetch(url: str):
            async with semaphore:
                return await self.fetch_url(url)

        tasks = [sem_fetch(u) for u in urls]
        return await asyncio.gather(*tasks)
