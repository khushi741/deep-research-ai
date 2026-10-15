from typing import List, Dict
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.research import ExtractedContent, Finding, SubQuestion
from app.utils.security import wrap_untrusted_web_content


class ExtractionResponse(BaseModel):
    findings: List[Finding]


class EvidenceExtractor(BaseAgent):
    """
    Extracts structured, verifiable findings and quotes from web page text.
    Maintains source attribution and preserves conflicting evidence.
    """

    SYSTEM_INSTRUCTION = (
        "You are an Evidence Extraction Specialist. "
        "Extract factual claims, verbatim evidence excerpts, and confidence levels strictly from the provided text. "
        "DO NOT invent facts or hallucinate statistics. If sources disagree, preserve the conflict."
    )

    def extract_evidence(
        self, 
        subquestion: SubQuestion, 
        sources: List[ExtractedContent]
    ) -> List[Finding]:
        """Extracts structured findings for a specific subquestion from retrieved web sources."""
        valid_sources = [s for s in sources if s.content and not s.error]
        if not valid_sources:
            return []

        self.logger.info(f"Extracting evidence for subquestion '{subquestion.id}': '{subquestion.question}' from {len(valid_sources)} sources")

        if not self.llm.is_available():
            return self._fallback_extraction(subquestion, valid_sources)

        # Securely format untrusted web content with XML wrappers
        formatted_sources = "\n\n".join([
            wrap_untrusted_web_content(url=s.url, title=s.title, text=s.content[:3500])
            for s in valid_sources[:5]  # Cap per prompt
        ])

        prompt = (
            f"Subquestion ({subquestion.id}): '{subquestion.question}'\n\n"
            f"Retrieved Web Content Sources:\n{formatted_sources}\n\n"
            f"Extract structured findings relevant to the subquestion above.\n"
            f"For each finding, specify:\n"
            f"- id (e.g., f_{subquestion.id}_1)\n"
            f"- claim (concise factual statement)\n"
            f"- evidence_excerpt (short direct excerpt from the text)\n"
            f"- source_urls (list containing exact URL of source)\n"
            f"- subquestion_id ('{subquestion.id}')\n"
            f"- confidence_level ('High', 'Medium', or 'Low')\n"
            f"- confidence_explanation\n"
            f"- relevant_dates (if mentioned)"
        )

        try:
            result = self.llm.generate_structured(
                prompt=prompt,
                response_schema=ExtractionResponse,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            return result.findings
        except Exception as e:
            self.logger.error(f"LLM evidence extraction failed: {str(e)}. Using fallback extraction.")
            return self._fallback_extraction(subquestion, valid_sources)

    def _fallback_extraction(self, subquestion: SubQuestion, sources: List[ExtractedContent]) -> List[Finding]:
        """Rule-based extraction when LLM is unavailable."""
        findings = []
        for i, s in enumerate(sources[:3]):
            snippet = s.content[:300] if len(s.content) > 300 else s.content
            findings.append(Finding(
                id=f"f_{subquestion.id}_{i+1}",
                claim=f"Information from {s.title} regarding {subquestion.question}",
                evidence_excerpt=snippet,
                source_urls=[s.url],
                subquestion_id=subquestion.id,
                confidence_level="Medium",
                confidence_explanation="Extracted directly from top search result snippet.",
                relevant_dates=s.published_date
            ))
        return findings
