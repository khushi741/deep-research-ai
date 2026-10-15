import os
import asyncio
from typing import List, Optional
from app.config import settings
from app.models.research import SearchResult
from app.utils.text_processing import normalize_url
from app.utils.logging import get_logger

logger = get_logger("search_tool")


class WebSearchTool:
    """
    Unified Web Search Provider.
    Tries Tavily API if key is present, otherwise falls back to DuckDuckGo search.
    Enforces deduplication by normalized URL and maximum search results.
    """

    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_key = tavily_api_key or settings.TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")
        self._tavily_client = None

        if self.tavily_key:
            try:
                from tavily import TavilyClient
                self._tavily_client = TavilyClient(api_key=self.tavily_key)
                logger.info("Tavily search provider initialized.")
            except ImportError:
                logger.warning("tavily-python package not installed, falling back to DuckDuckGo search.")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily client: {str(e)}")

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Executes a web search query safely with deduplication."""
        if not query or not query.strip():
            return []

        clean_query = query.strip()[:settings.MAX_QUERY_LENGTH]
        logger.info(f"Executing web search for query: '{clean_query}' (max_results={max_results})")

        # Try Tavily first if available
        if self._tavily_client:
            try:
                results = await self._search_tavily(clean_query, max_results)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"Tavily search failed for '{clean_query}': {str(e)}. Attempting fallback...")

        # Fallback to DuckDuckGo
        return await self._search_duckduckgo(clean_query, max_results)

    async def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        loop = asyncio.get_event_loop()
        # Run blocking Tavily call in executor
        response = await loop.run_in_executor(
            None, 
            lambda: self._tavily_client.search(
                query=query, 
                max_results=max_results, 
                search_depth="advanced"
            )
        )
        
        raw_results = response.get("results", [])
        results: List[SearchResult] = []
        seen_urls = set()

        for item in raw_results:
            raw_url = item.get("url", "")
            norm_url = normalize_url(raw_url)
            if not norm_url or norm_url in seen_urls:
                continue
            seen_urls.add(norm_url)

            results.append(SearchResult(
                title=item.get("title", "Untitled"),
                url=raw_url,
                snippet=item.get("content", item.get("snippet", "")),
                published_date=item.get("published_date"),
                source_metadata={"provider": "tavily", "score": item.get("score", 0.0)}
            ))

        return results

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback web search using duckduckgo_search library."""
        try:
            from duckduckgo_search import DDGS
            loop = asyncio.get_event_loop()
            
            def run_ddg():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=max_results))

            raw_results = await loop.run_in_executor(None, run_ddg)
            results: List[SearchResult] = []
            seen_urls = set()

            for item in raw_results:
                raw_url = item.get("href", item.get("url", ""))
                norm_url = normalize_url(raw_url)
                if not norm_url or norm_url in seen_urls:
                    continue
                seen_urls.add(norm_url)

                results.append(SearchResult(
                    title=item.get("title", "Untitled"),
                    url=raw_url,
                    snippet=item.get("body", item.get("snippet", "")),
                    published_date=None,
                    source_metadata={"provider": "duckduckgo"}
                ))

            logger.info(f"DuckDuckGo search returned {len(results)} deduplicated results for '{query}'")
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {str(e)}")
            return []
