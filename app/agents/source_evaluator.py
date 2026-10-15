from typing import List, Optional
from pydantic import BaseModel, Field
from app.agents.base import BaseAgent
from app.models.research import ExtractedContent, SourceEvaluation
from app.providers.base import BaseLLMProvider


class SourceEvaluationResponse(BaseModel):
    evaluations: List[SourceEvaluation]


class SourceEvaluator(BaseAgent):
    """
    Evaluates retrieved web pages for relevance, publisher authority, recency, 
    and source classification with transparent reasoning.
    """

    SYSTEM_INSTRUCTION = (
        "You are a critical Academic and Intelligence Source Evaluator. "
        "Assess sources objectively for relevance, authority signals, recency, and primary vs. secondary status. "
        "Do not over-rate self-published blogs or unverified commercial marketing."
    )

    def evaluate_sources(self, question: str, sources: List[ExtractedContent]) -> List[SourceEvaluation]:
        """Evaluates a list of extracted content items against the research question."""
        valid_sources = [s for s in sources if s.content and not s.error]
        if not valid_sources:
            return []

        self.logger.info(f"Evaluating {len(valid_sources)} sources for query: '{question}'")

        if not self.llm.is_available():
            return [self._rule_based_evaluation(s) for s in valid_sources]

        # Truncate content for LLM evaluation prompt efficiency
        sources_summary = "\n\n".join([
            f"--- SOURCE {i+1} ---\n"
            f"URL: {s.url}\n"
            f"Domain: {s.domain}\n"
            f"Title: {s.title}\n"
            f"Snippet: {s.content[:600]}...\n"
            f"Published Date: {s.published_date or 'Unknown'}"
            for i, s in enumerate(valid_sources[:10])  # Batch limit
        ])

        prompt = (
            f"Research Question: '{question}'\n\n"
            f"Evaluate the following web sources:\n{sources_summary}\n\n"
            f"For each source, provide a SourceEvaluation containing:\n"
            f"- url, title, domain\n"
            f"- relevance_score (0.0 to 1.0)\n"
            f"- authority_score (0.0 to 1.0)\n"
            f"- source_type (Primary, Secondary, Opinion, Academic, News, Industry Report)\n"
            f"- credibility_signals (list of positive/negative signals)\n"
            f"- reasoning (transparent explanation)\n"
            f"- published_date"
        )

        try:
            result = self.llm.generate_structured(
                prompt=prompt,
                response_schema=SourceEvaluationResponse,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            return result.evaluations
        except Exception as e:
            self.logger.error(f"LLM source evaluation failed: {str(e)}. Falling back to heuristic evaluation.")
            return [self._rule_based_evaluation(s) for s in valid_sources]

    def _rule_based_evaluation(self, source: ExtractedContent) -> SourceEvaluation:
        """Heuristic evaluation when LLM is unavailable."""
        domain = source.domain.lower()
        
        # Domain authority signals
        high_authority = any(ext in domain for ext in [".gov", ".edu", ".org", "arxiv.org", "reuters.com", "bloomberg.com"])
        med_authority = any(ext in domain for ext in [".com", "techcrunch.com", "github.com", "medium.com"])

        auth_score = 0.85 if high_authority else (0.65 if med_authority else 0.50)
        source_type = "Academic/Government" if high_authority else "Secondary"
        signals = []
        if high_authority:
            signals.append("Trusted top-level domain (.gov/.edu/.org or major press)")
        if source.published_date:
            signals.append(f"Publication date present ({source.published_date})")

        return SourceEvaluation(
            url=source.url,
            title=source.title,
            domain=source.domain,
            relevance_score=0.75,
            authority_score=auth_score,
            source_type=source_type,
            credibility_signals=signals or ["Standard web source"],
            reasoning="Heuristic evaluation based on domain extensions and metadata presence.",
            published_date=source.published_date
        )
