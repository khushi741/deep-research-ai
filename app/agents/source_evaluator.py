from typing import List, Optional
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.models.research import ExtractedContent, SourceEvaluation
from app.providers.base import BaseLLMProvider
from app.tools.relevance_filter import SemanticRelevanceFilter


class SourceEvaluationResponse(BaseModel):
    evaluations: List[SourceEvaluation]


class SourceEvaluator(BaseAgent):
    """
    Evaluates retrieved web pages for semantic relevance, publisher authority, recency, 
    and source classification with transparent reasoning.
    Disqualifies irrelevant results (homonyms, dictionary definitions, commercial spam)
    before they enter the evidence pool.
    """

    SYSTEM_INSTRUCTION = (
        "You are a critical Academic and Intelligence Source Evaluator. "
        "Assess sources objectively for relevance to the specific research question, authority signals, recency, and primary vs. secondary status. "
        "Explicitly penalize homonyms (e.g. SOLID software design principles when researching solid-state batteries) "
        "and commercial dealership/marketing pages."
    )

    def evaluate_sources(
        self, 
        question: str, 
        sources: List[ExtractedContent],
        subquestions: Optional[List[str]] = None,
        min_relevance: float = 0.45
    ) -> List[SourceEvaluation]:
        """
        Evaluates a list of extracted content items against the research question.
        Returns a list of SourceEvaluation objects with is_included and exclusion_reason populated.
        """
        valid_sources = [s for s in sources if s.content and not s.error]
        if not valid_sources:
            return []

        self.logger.info(f"Evaluating {len(valid_sources)} sources for query: '{question}' (min_relevance={min_relevance})")

        evaluations: List[SourceEvaluation] = []

        # 1. First pass: High-precision semantic relevance & authority calculation
        for source in valid_sources:
            rel_score, rel_reason, rel_signals = SemanticRelevanceFilter.calculate_relevance(
                topic=question,
                page_title=source.title,
                page_content=source.content,
                url=source.url,
                subquestions=subquestions
            )
            auth_score, source_type, auth_signals = SemanticRelevanceFilter.assess_authority(
                url=source.url,
                title=source.title,
                content=source.content
            )

            is_included = rel_score >= min_relevance
            exclusion_reason = None if is_included else (
                f"Excluded: Relevance score ({rel_score:.2f}) is below threshold ({min_relevance:.2f}). {rel_reason}"
            )

            eval_item = SourceEvaluation(
                url=source.url,
                title=source.title,
                domain=source.domain,
                relevance_score=rel_score,
                authority_score=auth_score,
                source_type=source_type,
                credibility_signals=rel_signals + auth_signals,
                reasoning=f"{rel_reason} {source_type} domain assessment.",
                published_date=source.published_date,
                is_included=is_included,
                exclusion_reason=exclusion_reason
            )
            evaluations.append(eval_item)

        # 2. Second pass: If LLM is available, refine reasoning and classification for included sources
        if self.llm.is_available():
            included_evals = [e for e in evaluations if e.is_included]
            if included_evals:
                try:
                    evaluations = self._refine_with_llm(question, included_evals, evaluations)
                except Exception as e:
                    self.logger.warning(f"LLM source evaluation refinement skipped: {str(e)}")

        included_count = sum(1 for e in evaluations if e.is_included)
        self.logger.info(f"Source evaluation completed: {included_count}/{len(evaluations)} sources approved as relevant.")
        return evaluations

    def _refine_with_llm(
        self, 
        question: str, 
        candidate_evals: List[SourceEvaluation], 
        all_evals: List[SourceEvaluation]
    ) -> List[SourceEvaluation]:
        """Refines scores and classification using LLM while preserving algorithmic homonym rejection."""
        # Prompt LLM for candidate sources
        summary_snippets = []
        for i, ev in enumerate(candidate_evals[:8]):
            summary_snippets.append(
                f"--- SOURCE {i+1} ---\n"
                f"URL: {ev.url}\n"
                f"Domain: {ev.domain}\n"
                f"Title: {ev.title}\n"
                f"Algorithmic Relevance: {ev.relevance_score}\n"
                f"Algorithmic Authority: {ev.authority_score}\n"
                f"Published Date: {ev.published_date or 'Unknown'}"
            )

        prompt = (
            f"Research Question: '{question}'\n\n"
            f"Review these candidate web sources:\n"
            + "\n\n".join(summary_snippets) +
            f"\n\nConfirm relevance (0.0-1.0), authority (0.0-1.0), source_type, and concise reasoning."
        )

        try:
            llm_res = self.llm.generate_structured(
                prompt=prompt,
                response_schema=SourceEvaluationResponse,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            # Merge LLM refinements
            llm_map = {e.url: e for e in llm_res.evaluations}
            for ev in all_evals:
                if ev.url in llm_map:
                    refined = llm_map[ev.url]
                    # Retain disqualifications if algorithmic score was very low
                    if ev.relevance_score < 0.2:
                        continue
                    # Blend LLM and algorithmic score safely
                    ev.relevance_score = round(0.5 * ev.relevance_score + 0.5 * min(1.0, max(0.0, refined.relevance_score)), 2)
                    ev.authority_score = round(0.5 * ev.authority_score + 0.5 * min(1.0, max(0.0, refined.authority_score)), 2)
                    ev.source_type = refined.source_type or ev.source_type
                    if refined.reasoning:
                        ev.reasoning = f"{refined.reasoning} (Algorithmic relevance: {ev.relevance_score:.2f})"
        except Exception as e:
            self.logger.warning(f"Error in LLM evaluation refinement: {str(e)}")

        return all_evals
