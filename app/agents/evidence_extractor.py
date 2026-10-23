import re
from typing import List, Dict, Set
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.research import ExtractedContent, Finding, SubQuestion
from app.utils.security import wrap_untrusted_web_content
from app.utils.text_processing import find_supporting_sentences, is_syndicated_duplicate


class ExtractionResponse(BaseModel):
    findings: List[Finding]


class EvidenceExtractor(BaseAgent):
    """
    Extracts structured, verifiable findings and quotes from web page text.
    Maintains rigorous claim-to-source attribution, detects syndicated duplication,
    and preserves conflicting evidence without fabricating support.
    """

    SYSTEM_INSTRUCTION = (
        "You are an Evidence Extraction Specialist. "
        "Extract factual claims, verbatim evidence excerpts, and confidence levels strictly from the provided text. "
        "Every claim MUST have a verbatim excerpt from the text that directly proves it. "
        "DO NOT invent facts or hallucinate statistics. If sources disagree, document the conflict. "
        "If a source does not contain direct evidence for the subquestion, DO NOT extract a finding from it."
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
            f"Extract structured findings that are directly relevant to the subquestion above.\n"
            f"Requirements:\n"
            f"- id (e.g., f_{subquestion.id}_1)\n"
            f"- claim (concise factual statement supported by the text)\n"
            f"- evidence_excerpt (exact verbatim sentence or passage from the source text)\n"
            f"- source_urls (list containing exact URL of the source providing this excerpt)\n"
            f"- subquestion_id ('{subquestion.id}')\n"
            f"- confidence_level ('High', 'Medium', or 'Low')\n"
            f"- confidence_explanation (why confidence is rated as such)\n"
            f"- relevant_dates (dates, years, or timelines if explicitly mentioned)"
        )

        try:
            result = self.llm.generate_structured(
                prompt=prompt,
                response_schema=ExtractionResponse,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            
            # Post-process findings: verify source attribution and corroboration
            processed_findings = self._verify_and_cross_reference(result.findings, valid_sources)
            return processed_findings
        except Exception as e:
            self.logger.error(f"LLM evidence extraction failed: {str(e)}. Using fallback extraction.")
            return self._fallback_extraction(subquestion, valid_sources)

    def _verify_and_cross_reference(self, findings: List[Finding], sources: List[ExtractedContent]) -> List[Finding]:
        """Verifies that findings reference genuine source content and computes corroboration counts."""
        source_map = {s.url: s.content for s in sources}
        verified_findings: List[Finding] = []

        for f in findings:
            # Check that source URL exists in fetched set
            valid_urls = [u for u in f.source_urls if u in source_map]
            if not valid_urls:
                continue
            
            f.source_urls = valid_urls

            # Check syndication vs independent corroboration if multiple URLs cited
            independent_sources = set()
            for url in valid_urls:
                is_duplicate = False
                for other_url in independent_sources:
                    if is_syndicated_duplicate(source_map[url], source_map[other_url]):
                        is_duplicate = True
                        break
                if not is_duplicate:
                    independent_sources.add(url)

            f.corroboration_count = max(1, len(independent_sources))
            
            if f.corroboration_count >= 2:
                f.verification_status = "Verified"
            elif f.confidence_level == "Low":
                f.verification_status = "Uncorroborated"
            else:
                f.verification_status = "Verified" if f.confidence_level == "High" else "Uncorroborated"

            verified_findings.append(f)

        return verified_findings

    def _fallback_extraction(self, subquestion: SubQuestion, sources: List[ExtractedContent]) -> List[Finding]:
        """Rule-based extraction extracting real sentences based on subquestion keywords."""
        findings = []
        # Extract keywords from subquestion text
        keywords = re.findall(r"\b[a-zA-Z]{3,}\b", subquestion.question.lower())
        stopwords = {"what", "when", "where", "which", "with", "about", "current", "state", "aspect", "regarding"}
        meaningful_kws = [w for w in keywords if w not in stopwords]

        for i, s in enumerate(sources[:3]):
            passage = find_supporting_sentences(s.content, meaningful_kws, max_sentences=2)
            if not passage or len(passage.strip()) < 30:
                continue

            findings.append(Finding(
                id=f"f_{subquestion.id}_{i+1}",
                claim=f"{s.title}: Key development regarding {subquestion.question}",
                evidence_excerpt=passage,
                source_urls=[s.url],
                subquestion_id=subquestion.id,
                confidence_level="Medium",
                confidence_explanation="Extracted verbatim passage matching subquestion keywords.",
                relevant_dates=s.published_date,
                corroboration_count=1,
                verification_status="Uncorroborated"
            ))
        return findings
