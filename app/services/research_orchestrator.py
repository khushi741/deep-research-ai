import asyncio
import time
import uuid
from typing import Optional, List, Dict, Set, Callable
from app.config import settings
from app.models.research import (
    ResearchRequest, 
    ResearchSessionState, 
    ResearchPlan, 
    ExtractedContent, 
    SourceEvaluation, 
    Finding, 
    ResearchReport,
    FollowupRequest,
    FollowupResponse,
    Citation
)
from app.providers.gemini_provider import GeminiLLMProvider
from app.agents.planner import ResearchPlanner
from app.agents.source_evaluator import SourceEvaluator
from app.agents.evidence_extractor import EvidenceExtractor
from app.agents.synthesizer import ResearchSynthesizer
from app.tools.search import WebSearchTool
from app.tools.web_fetcher import AsyncWebFetcher
from app.utils.text_processing import normalize_url, extract_domain
from app.utils.logging import get_logger

logger = get_logger("orchestrator")


class ResearchOrchestrator:
    """
    Coordinates the multi-stage autonomous research workflow:
    Planning -> Targeted Multi-query Search -> Safe Web Fetching -> Semantic Source Evaluation 
    -> Evidence Extraction & Corroboration -> Synthesis -> Citation Validation.
    Supports genuine research budgets, live event streaming, cancellation, and interactive follow-ups.
    """

    def __init__(self, llm_provider: Optional[GeminiLLMProvider] = None):
        self.llm = llm_provider or GeminiLLMProvider()
        self.planner = ResearchPlanner(self.llm)
        self.source_evaluator = SourceEvaluator(self.llm)
        self.evidence_extractor = EvidenceExtractor(self.llm)
        self.synthesizer = ResearchSynthesizer(self.llm)
        
        self.search_tool = WebSearchTool()
        self.web_fetcher = AsyncWebFetcher()
        self._cancelled_sessions: Set[str] = set()

    def cancel_research(self, session_id: str) -> bool:
        """Marks an active research session as cancelled."""
        logger.info(f"Cancellation requested for research session: {session_id}")
        self._cancelled_sessions.add(session_id)
        return True

    def is_cancelled(self, session_id: str) -> bool:
        return session_id in self._cancelled_sessions

    async def run_research(
        self, 
        request: ResearchRequest, 
        session_id: Optional[str] = None,
        progress_callback: Optional[Callable[[ResearchSessionState], None]] = None
    ) -> ResearchSessionState:
        """Executes the full research pipeline asynchronously with honest progress tracking."""
        sid = session_id or str(uuid.uuid4())
        start_time = time.time()

        # Budgets based on mode
        is_deep = (request.mode == "deep")
        max_subquestions = 5 if is_deep else 2
        max_urls_cap = 18 if is_deep else 6
        min_relevance = request.min_relevance or 0.45

        state = ResearchSessionState(
            id=sid,
            question=request.question,
            mode=request.mode,
            status="planning",
            current_stage="Stage 1/6: Formulating Research Plan & Search Vectors",
            progress_percent=5,
            completed_stages=[]
        )
        self._notify_progress(state, progress_callback)

        try:
            # -------------------------------------------------------------
            # STAGE 1: RESEARCH PLANNING
            # -------------------------------------------------------------
            if self.is_cancelled(sid):
                return self._handle_cancellation(state, start_time, progress_callback)

            logger.info(f"[{sid}] Starting Stage 1: Research Planning (Mode={request.mode})")
            plan = self.planner.create_plan(
                question=request.question,
                mode=request.mode,
                category=request.category,
                date_scope=request.date_scope
            )
            # Enforce mode subquestion budget
            plan.subquestions = plan.subquestions[:max_subquestions]
            state.plan = plan
            state.completed_stages.append("planning")
            state.progress_percent = 15

            # Calculate total planned queries
            all_queries = [q for sq in plan.subquestions for q in sq.search_queries]
            state.total_queries_count = len(all_queries)
            state.status = "searching"
            state.current_stage = f"Stage 2/6: Executing Web Searches ({state.total_queries_count} queries across {len(plan.subquestions)} vectors)"
            self._notify_progress(state, progress_callback)

            # -------------------------------------------------------------
            # STAGE 2: MULTI-QUERY WEB SEARCH & ASYNC CONTENT EXTRACTION
            # -------------------------------------------------------------
            if self.is_cancelled(sid):
                return self._handle_cancellation(state, start_time, progress_callback)

            logger.info(f"[{sid}] Starting Stage 2: Web Search & Fetching")
            extracted_sources = await self._execute_search_and_extraction(
                plan=plan,
                state=state,
                max_urls_cap=max_urls_cap,
                progress_callback=progress_callback
            )

            state.sources_count = len(extracted_sources)
            state.completed_stages.append("searching")
            state.progress_percent = 50
            state.status = "evaluating"
            state.current_stage = f"Stage 3/6: Semantic Source Evaluation ({len(extracted_sources)} sources)"
            self._notify_progress(state, progress_callback)

            # -------------------------------------------------------------
            # STAGE 3: SEMANTIC SOURCE EVALUATION & HOMONYM FILTERING
            # -------------------------------------------------------------
            if self.is_cancelled(sid):
                return self._handle_cancellation(state, start_time, progress_callback)

            logger.info(f"[{sid}] Starting Stage 3: Source Evaluation")
            sq_texts = [sq.question for sq in plan.subquestions]
            evaluations = self.source_evaluator.evaluate_sources(
                question=request.question,
                sources=extracted_sources,
                subquestions=sq_texts,
                min_relevance=min_relevance
            )
            state.sources = evaluations
            state.rejected_sources_count = sum(1 for e in evaluations if not e.is_included)

            # Map included content by URL
            included_urls = {e.url for e in evaluations if e.is_included}
            content_by_url = {s.url: s for s in extracted_sources if s.url in included_urls}

            state.completed_stages.append("evaluating")
            state.progress_percent = 65
            state.status = "extracting"
            state.current_stage = f"Stage 4/6: Extracting Verifiable Claims ({len(included_urls)} relevant sources accepted, {state.rejected_sources_count} excluded)"
            self._notify_progress(state, progress_callback)

            # -------------------------------------------------------------
            # STAGE 4: EVIDENCE EXTRACTION & CROSS-SOURCE CORROBORATION
            # -------------------------------------------------------------
            if self.is_cancelled(sid):
                return self._handle_cancellation(state, start_time, progress_callback)

            logger.info(f"[{sid}] Starting Stage 4: Evidence Extraction")
            all_findings: List[Finding] = []
            
            for idx, sq in enumerate(plan.subquestions, 1):
                if self.is_cancelled(sid):
                    return self._handle_cancellation(state, start_time, progress_callback)

                relevant_sources = [content_by_url[url] for url in included_urls if url in content_by_url]
                sq_findings = self.evidence_extractor.extract_evidence(sq, relevant_sources)
                all_findings.extend(sq_findings)

                # Incremental progress inside extraction stage
                state.progress_percent = min(80, 65 + int((idx / len(plan.subquestions)) * 15))
                state.findings_count = len(all_findings)
                self._notify_progress(state, progress_callback)

            # --- Deep Mode Adaptive Gap Filling Pass ---
            if is_deep and len(all_findings) < 4 and not self.is_cancelled(sid):
                logger.info(f"[{sid}] Deep mode detected evidence gaps. Launching adaptive follow-up pass.")
                state.current_stage = "Stage 4 (Pass 2): Adaptive Gap-Filling Search"
                self._notify_progress(state, progress_callback)

                adaptive_query = f"{request.question} research breakthrough technical analysis"
                extra_search = await self.search_tool.search(adaptive_query, max_results=3)
                existing_urls = {normalize_url(s.url) for s in extracted_sources}
                extra_urls = [r.url for r in extra_search if normalize_url(r.url) not in existing_urls]

                if extra_urls:
                    extra_content = await self.web_fetcher.fetch_batch(extra_urls, max_concurrency=2)
                    extra_evals = self.source_evaluator.evaluate_sources(
                        question=request.question,
                        sources=extra_content,
                        subquestions=sq_texts,
                        min_relevance=min_relevance
                    )
                    state.sources.extend(extra_evals)
                    for s in extra_content:
                        if any(e.url == s.url and e.is_included for e in extra_evals):
                            content_by_url[s.url] = s

                    # Extract findings from extra pass
                    for sq in plan.subquestions[:2]:
                        extra_findings = self.evidence_extractor.extract_evidence(sq, extra_content)
                        all_findings.extend(extra_findings)

            state.findings = all_findings
            state.findings_count = len(all_findings)
            state.completed_stages.append("extracting")
            state.progress_percent = 85

            # -------------------------------------------------------------
            # STAGE 5: REPORT SYNTHESIS
            # -------------------------------------------------------------
            if self.is_cancelled(sid):
                return self._handle_cancellation(state, start_time, progress_callback)

            state.status = "synthesizing"
            state.current_stage = "Stage 5/6: Synthesizing Evidence-Grounded Report"
            self._notify_progress(state, progress_callback)

            logger.info(f"[{sid}] Starting Stage 5: Research Synthesis")
            report = self.synthesizer.synthesize_report(
                question=request.question,
                plan=plan,
                findings=all_findings,
                sources=state.sources
            )
            state.report = report
            state.completed_stages.append("synthesizing")
            state.progress_percent = 95

            # -------------------------------------------------------------
            # STAGE 6: FINAL VALIDATION & COMPLETION
            # -------------------------------------------------------------
            state.current_stage = "Stage 6/6: Validating Citations & Provenance Integrity"
            self._notify_progress(state, progress_callback)

            # Ensure all citations point to actual included sources
            verified_refs = [
                ref for ref in report.references
                if any(s.url == ref.url and s.is_included for s in state.sources)
            ]
            report.references = verified_refs

            state.status = "completed"
            state.completed_stages.append("completed")
            state.current_stage = f"Research Completed Successfully ({len(report.references)} verified citations)"
            state.progress_percent = 100
            state.duration_seconds = round(time.time() - start_time, 2)
            self._notify_progress(state, progress_callback)

            logger.info(f"[{sid}] Research completed successfully in {state.duration_seconds}s")
            return state

        except Exception as e:
            logger.error(f"[{sid}] Research pipeline error: {str(e)}", exc_info=True)
            state.status = "failed"
            state.current_stage = "Research Failed"
            state.error_message = f"Research execution error: {str(e)}"
            state.duration_seconds = round(time.time() - start_time, 2)
            self._notify_progress(state, progress_callback)
            return state

    async def _execute_search_and_extraction(
        self, 
        plan: ResearchPlan, 
        state: ResearchSessionState,
        max_urls_cap: int,
        progress_callback: Optional[Callable[[ResearchSessionState], None]]
    ) -> List[ExtractedContent]:
        """Executes search queries across subquestions and fetches webpage content concurrently."""
        all_candidate_urls: List[str] = []
        completed_queries = 0
        total_queries = max(state.total_queries_count, 1)

        # Collect search results for all subquestion queries
        for sq in plan.subquestions:
            for query in sq.search_queries[:2]:  # Up to 2 targeted queries per subquestion
                if self.is_cancelled(state.id):
                    return []
                
                search_results = await self.search_tool.search(query, max_results=4)
                completed_queries += 1
                state.completed_queries_count = completed_queries

                # Update progress smoothly across search stage (15% to 35%)
                state.progress_percent = 15 + int((completed_queries / total_queries) * 20)
                state.current_stage = f"Stage 2/6: Querying Web ({completed_queries}/{total_queries} queries completed)"
                self._notify_progress(state, progress_callback)

                for r in search_results:
                    all_candidate_urls.append(r.url)

        # Deduplicate URLs
        seen_norm_urls = set()
        unique_urls = []
        for url in all_candidate_urls:
            norm = normalize_url(url)
            if norm and norm not in seen_norm_urls:
                seen_norm_urls.add(norm)
                unique_urls.append(url)

        target_urls = unique_urls[:max_urls_cap]
        logger.info(f"Fetching content for {len(target_urls)} unique URLs (budget cap: {max_urls_cap})")

        # Update progress for fetch stage (35% to 50%)
        state.current_stage = f"Stage 2/6: Fetching & Cleaning {len(target_urls)} Web Article Payloads"
        state.progress_percent = 38
        self._notify_progress(state, progress_callback)

        extracted_content = await self.web_fetcher.fetch_batch(target_urls, max_concurrency=3)
        valid_extracted = [c for c in extracted_content if c.content and not c.error]
        return valid_extracted

    def _handle_cancellation(
        self, 
        state: ResearchSessionState, 
        start_time: float, 
        callback: Optional[Callable[[ResearchSessionState], None]]
    ) -> ResearchSessionState:
        """Handles graceful cancellation of a research run."""
        state.status = "cancelled"
        state.is_cancelled = True
        state.current_stage = "Research Cancelled by User"
        state.duration_seconds = round(time.time() - start_time, 2)
        self._notify_progress(state, callback)
        return state

    def _notify_progress(self, state: ResearchSessionState, callback: Optional[Callable[[ResearchSessionState], None]]):
        if callback:
            try:
                callback(state)
            except Exception as e:
                logger.warning(f"Progress callback error: {str(e)}")

    async def answer_followup(
        self, 
        session: ResearchSessionState, 
        followup_req: FollowupRequest
    ) -> FollowupResponse:
        """
        Answers a follow-up question grounded in the report's evidence.
        Distinguishes answers based on existing evidence from newly retrieved evidence.
        """
        user_q = followup_req.question.strip()
        logger.info(f"[{session.id}] Answering follow-up question: '{user_q}'")

        if not session.report:
            raise ValueError("Research report is not yet complete for this session.")

        # Check existing evidence
        existing_evidence_lines = []
        for f in session.findings:
            existing_evidence_lines.append(f"- Claim: {f.claim}\n  Excerpt: \"{f.evidence_excerpt}\"")
        existing_evidence_text = "\n".join(existing_evidence_lines)

        prompt = (
            f"Original Topic: '{session.question}'\n"
            f"User Follow-up Question: '{user_q}'\n\n"
            f"Existing Collected Findings:\n{existing_evidence_text}\n\n"
            f"Answer the user's question accurately using the existing evidence. "
            f"If the existing evidence directly answers the question, provide a detailed answer. "
            f"If the existing evidence does NOT answer the question or has missing gaps, state clearly: "
            f"'[INSUFFICIENT_EXISTING_EVIDENCE]' followed by what is known so far."
        )

        initial_answer = self.llm.generate_text(prompt)

        # If existing evidence was sufficient or new search is disabled
        if "[INSUFFICIENT_EXISTING_EVIDENCE]" not in initial_answer or not followup_req.allow_new_search:
            clean_answer = initial_answer.replace("[INSUFFICIENT_EXISTING_EVIDENCE]", "").strip()
            return FollowupResponse(
                question=user_q,
                answer=clean_answer,
                cited_references=session.report.references[:5],
                new_searches_conducted=False,
                evidence_source="Existing Report Evidence"
            )

        # Launch targeted supplementary search for the follow-up
        logger.info(f"[{session.id}] Supplementary search triggered for follow-up.")
        search_results = await self.search_tool.search(f"{session.question} {user_q}", max_results=3)
        existing_urls = {normalize_url(s.url) for s in session.sources}
        new_urls = [r.url for r in search_results if normalize_url(r.url) not in existing_urls][:3]

        new_content = await self.web_fetcher.fetch_batch(new_urls, max_concurrency=2) if new_urls else []
        new_evals = self.source_evaluator.evaluate_sources(user_q, new_content, min_relevance=0.40)
        valid_new_sources = [c for c in new_content if any(e.url == c.url and e.is_included for e in new_evals)]

        new_evidence_snippets = "\n\n".join([
            f"Source ({s.title}): {s.content[:1500]}"
            for s in valid_new_sources
        ])

        second_prompt = (
            f"Topic: '{session.question}'\n"
            f"User Follow-up: '{user_q}'\n\n"
            f"Newly Retrieved Web Sources:\n{new_evidence_snippets}\n\n"
            f"Synthesize a clear, evidence-grounded answer to the follow-up question. "
            f"Explicitly note that this information was retrieved through supplementary search."
        )
        supplemented_answer = self.llm.generate_text(second_prompt)

        new_citations = [
            Citation(
                id=len(session.report.references) + i + 1,
                url=s.url,
                title=s.title,
                domain=extract_domain(s.url),
                relevance_score=0.85,
                source_type="Supplementary Search"
            )
            for i, s in enumerate(valid_new_sources)
        ]

        return FollowupResponse(
            question=user_q,
            answer=supplemented_answer,
            cited_references=new_citations,
            new_searches_conducted=True,
            evidence_source="Newly Retrieved Web Evidence (Supplementary Search)"
        )
