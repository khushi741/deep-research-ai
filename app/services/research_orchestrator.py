import asyncio
import time
import uuid
from typing import Optional, List, Callable
from app.config import settings
from app.models.research import (
    ResearchRequest, 
    ResearchSessionState, 
    ResearchPlan, 
    ExtractedContent, 
    SourceEvaluation, 
    Finding, 
    ResearchReport
)
from app.providers.gemini_provider import GeminiLLMProvider
from app.agents.planner import ResearchPlanner
from app.agents.source_evaluator import SourceEvaluator
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.synthesizer import ResearchSynthesizer
from app.tools.search import WebSearchTool
from app.tools.web_fetcher import AsyncWebFetcher
from app.utils.text_processing import normalize_url
from app.utils.logging import get_logger

logger = get_logger("orchestrator")


class ResearchOrchestrator:
    """
    Coordinates the multi-stage research workflow:
    Planning -> Web Search -> Content Extraction -> Source Evaluation -> Evidence Extraction -> Synthesis
    Supports bounded iteration for missing evidence.
    """

    def __init__(self, llm_provider: Optional[GeminiLLMProvider] = None):
        self.llm = llm_provider or GeminiLLMProvider()
        self.planner = ResearchPlanner(self.llm)
        self.source_evaluator = SourceEvaluator(self.llm)
        self.evidence_extractor = EvidenceExtractor(self.llm)
        self.synthesizer = ResearchSynthesizer(self.llm)
        
        self.search_tool = WebSearchTool()
        self.web_fetcher = AsyncWebFetcher()

    async def run_research(
        self, 
        request: ResearchRequest, 
        session_id: Optional[str] = None,
        progress_callback: Optional[Callable[[ResearchSessionState], None]] = None
    ) -> ResearchSessionState:
        """Executes the full research pipeline asynchronously."""
        sid = session_id or str(uuid.uuid4())
        start_time = time.time()

        state = ResearchSessionState(
            id=sid,
            question=request.question,
            mode=request.mode,
            status="planning",
            current_stage="Stage A: Research Planning"
        )
        self._notify_progress(state, progress_callback)

        try:
            # --- Stage A: Research Planning ---
            logger.info(f"[{sid}] Starting Stage A: Research Planning")
            plan = self.planner.create_plan(
                question=request.question,
                mode=request.mode,
                category=request.category,
                date_scope=request.date_scope
            )
            state.plan = plan
            state.status = "searching"
            state.current_stage = f"Stage B: Web Research ({len(plan.subquestions)} subquestions)"
            self._notify_progress(state, progress_callback)

            # --- Stage B & C: Web Research & Content Extraction ---
            logger.info(f"[{sid}] Starting Stage B & C: Web Search & Extraction")
            extracted_sources = await self._execute_search_and_extraction(plan, request.mode)
            state.sources_count = len(extracted_sources)
            state.status = "evaluating"
            state.current_stage = f"Stage D: Evaluating {len(extracted_sources)} Discovered Sources"
            self._notify_progress(state, progress_callback)

            # --- Stage D: Source Evaluation ---
            logger.info(f"[{sid}] Starting Stage D: Source Evaluation")
            evaluations = self.source_evaluator.evaluate_sources(request.question, extracted_sources)
            state.sources = evaluations
            state.status = "extracting"
            state.current_stage = "Stage E: Extracting Structured Evidence & Quotes"
            self._notify_progress(state, progress_callback)

            # --- Stage E: Evidence Extraction ---
            logger.info(f"[{sid}] Starting Stage E: Evidence Extraction")
            all_findings: List[Finding] = []
            
            # Map extracted content by URL for fast lookup
            content_by_url = {s.url: s for s in extracted_sources}

            for sq in plan.subquestions:
                # Get relevant extracted sources for this subquestion
                relevant_sources = [
                    content_by_url[eval_item.url] 
                    for eval_item in evaluations 
                    if eval_item.url in content_by_url and eval_item.relevance_score >= 0.4
                ]
                sq_findings = self.evidence_extractor.extract_evidence(sq, relevant_sources)
                all_findings.extend(sq_findings)

            state.findings = all_findings
            state.findings_count = len(all_findings)

            # --- Bounded Iteration Check for Evidence Gaps ---
            if request.mode == "deep" and len(all_findings) < 3:
                logger.info(f"[{sid}] Evidence gaps detected. Running bounded 2nd iteration pass.")
                state.current_stage = "Stage E (Pass 2): Bounded Follow-up Web Search"
                self._notify_progress(state, progress_callback)

                # Generate 2 targeted follow-up queries
                followup_query = f"{request.question} statistics evidence detailed analysis"
                extra_search = await self.search_tool.search(followup_query, max_results=3)
                extra_urls = [r.url for r in extra_search if normalize_url(r.url) not in {normalize_url(s.url) for s in extracted_sources}]
                
                if extra_urls:
                    extra_content = await self.web_fetcher.fetch_batch(extra_urls, max_concurrency=2)
                    extra_evals = self.source_evaluator.evaluate_sources(request.question, extra_content)
                    state.sources.extend(extra_evals)
                    
                    # Extract from extra pass
                    for sq in plan.subquestions[:2]:
                        extra_findings = self.evidence_extractor.extract_evidence(sq, extra_content)
                        all_findings.extend(extra_findings)
                    
                    state.findings = all_findings
                    state.findings_count = len(all_findings)

            # --- Stage F: Research Synthesis ---
            state.status = "synthesizing"
            state.current_stage = "Stage F: Synthesizing Final Report & References"
            self._notify_progress(state, progress_callback)

            logger.info(f"[{sid}] Starting Stage F: Research Synthesis")
            report = self.synthesizer.synthesize_report(
                question=request.question,
                plan=plan,
                findings=all_findings,
                sources=state.sources
            )

            state.report = report
            state.status = "completed"
            state.current_stage = "Research Complete"
            state.duration_seconds = round(time.time() - start_time, 2)
            self._notify_progress(state, progress_callback)

            logger.info(f"[{sid}] Research completed successfully in {state.duration_seconds}s")
            return state

        except Exception as e:
            logger.error(f"[{sid}] Research pipeline error: {str(e)}", exc_info=True)
            state.status = "failed"
            state.current_stage = "Failed"
            state.error_message = f"Research execution error: {str(e)}"
            state.duration_seconds = round(time.time() - start_time, 2)
            self._notify_progress(state, progress_callback)
            return state

    async def _execute_search_and_extraction(self, plan: ResearchPlan, mode: str) -> List[ExtractedContent]:
        """Executes search queries across subquestions and fetches webpage content concurrently."""
        all_urls_to_fetch = []
        max_search_results = 4 if mode == "deep" else 3

        # Collect search results for all subquestion queries
        for sq in plan.subquestions:
            for query in sq.search_queries[:2]:  # Top 2 queries per subquestion
                search_results = await self.search_tool.search(query, max_results=max_search_results)
                for r in search_results:
                    all_urls_to_fetch.append(r.url)

        # Deduplicate URLs by normalized URL
        seen_norm_urls = set()
        unique_urls = []
        for url in all_urls_to_fetch:
            norm = normalize_url(url)
            if norm and norm not in seen_norm_urls:
                seen_norm_urls.add(norm)
                unique_urls.append(url)

        # Enforce max page limit from settings
        target_urls = unique_urls[:settings.MAX_PAGES_PROCESSED]
        logger.info(f"Fetching content for {len(target_urls)} unique URLs (capped at MAX_PAGES_PROCESSED={settings.MAX_PAGES_PROCESSED})")

        # Asynchronously fetch content in parallel
        extracted_content = await self.web_fetcher.fetch_batch(target_urls, max_concurrency=4)
        
        # Filter out completely failed or empty pages
        valid_extracted = [c for c in extracted_content if c.content and not c.error]
        return valid_extracted

    def _notify_progress(self, state: ResearchSessionState, callback: Optional[Callable[[ResearchSessionState], None]]):
        if callback:
            try:
                callback(state)
            except Exception as e:
                logger.warning(f"Progress callback error: {str(e)}")
