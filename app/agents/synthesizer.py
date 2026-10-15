from typing import List, Dict
from pydantic import BaseModel
from app.agents.base import BaseAgent
from app.models.research import ResearchPlan, Finding, SourceEvaluation, Citation, ResearchReport
from app.utils.text_processing import extract_domain


class RawSynthesisResponse(BaseModel):
    title: str
    executive_summary: str
    methodology: str
    key_findings: List[str]
    detailed_analysis: str
    evidence_and_citations: str
    conflicting_evidence_and_limitations: str
    unanswered_questions: str
    conclusion: str


class ResearchSynthesizer(BaseAgent):
    """
    Synthesizes collected evidence, source evaluations, and subquestion findings
    into a comprehensive, structured research report with numbered citations.
    """

    SYSTEM_INSTRUCTION = (
        "You are a Senior Principal Analyst and Research Director. "
        "Synthesize evidence into a rigorous, well-structured, production-grade research report. "
        "Every claim MUST be backed by evidence citations using numbered bracket format e.g., [1], [2]. "
        "Never invent URLs or claim facts not supported by the evidence."
    )

    def synthesize_report(
        self, 
        question: str, 
        plan: ResearchPlan, 
        findings: List[Finding], 
        sources: List[SourceEvaluation]
    ) -> ResearchReport:
        """Synthesizes evidence into a complete ResearchReport with built-in reference mapping."""
        self.logger.info(f"Synthesizing final research report for question: '{question}'")

        # 1. Build Reference URL Mapping: URL -> Citation ID (1, 2, 3...)
        url_to_citation: Dict[str, Citation] = {}
        citation_id_counter = 1

        # Deduplicate and register all cited source URLs
        all_urls = set()
        for f in findings:
            for url in f.source_urls:
                all_urls.add(url)
        for s in sources:
            all_urls.add(s.url)

        # Build citation list
        for url in sorted(all_urls):
            source_info = next((s for s in sources if s.url == url), None)
            title = source_info.title if source_info else f"Source from {extract_domain(url)}"
            domain = source_info.domain if source_info else extract_domain(url)
            pub_date = source_info.published_date if source_info else None

            url_to_citation[url] = Citation(
                id=citation_id_counter,
                url=url,
                title=title,
                domain=domain,
                published_date=pub_date
            )
            citation_id_counter += 1

        references = list(url_to_citation.values())

        if not self.llm.is_available():
            return self._fallback_synthesis(question, plan, findings, references, url_to_citation)

        # Build Evidence Text Summary for LLM with explicit citation tags [N]
        evidence_summary_lines = []
        for f in findings:
            citation_tags = [f"[{url_to_citation[u].id}]" for u in f.source_urls if u in url_to_citation]
            tags_str = " ".join(citation_tags)
            evidence_summary_lines.append(
                f"- Claim: {f.claim} {tags_str}\n"
                f"  Excerpt: \"{f.evidence_excerpt}\"\n"
                f"  Subquestion: {f.subquestion_id} | Confidence: {f.confidence_level}"
            )
        evidence_prompt_text = "\n".join(evidence_summary_lines)

        prompt = (
            f"Original Research Question: '{question}'\n"
            f"Refined Question: '{plan.refined_question}'\n\n"
            f"Collected Findings & Evidence (with citation tags):\n{evidence_prompt_text}\n\n"
            f"Generate a comprehensive report with:\n"
            f"1. Professional Report Title\n"
            f"2. Executive Summary (2-3 dense paragraphs)\n"
            f"3. Research Methodology (brief outline of plan and search scope)\n"
            f"4. Key Findings (list of 4-6 high-impact points)\n"
            f"5. Detailed Analysis by Topic (extensive narrative with inline citations like [1], [2])\n"
            f"6. Evidence & Citations (summary of primary vs secondary evidence)\n"
            f"7. Conflicting Evidence or Limitations\n"
            f"8. Unanswered Questions & Gaps\n"
            f"9. Conclusion"
        )

        try:
            raw = self.llm.generate_structured(
                prompt=prompt,
                response_schema=RawSynthesisResponse,
                system_instruction=self.SYSTEM_INSTRUCTION
            )

            # Assemble Full Markdown Document
            full_md = self._build_full_markdown(raw, references)

            return ResearchReport(
                title=raw.title,
                executive_summary=raw.executive_summary,
                methodology=raw.methodology,
                key_findings=raw.key_findings,
                detailed_analysis=raw.detailed_analysis,
                evidence_and_citations=raw.evidence_and_citations,
                conflicting_evidence_and_limitations=raw.conflicting_evidence_and_limitations,
                unanswered_questions=raw.unanswered_questions,
                conclusion=raw.conclusion,
                references=references,
                full_markdown=full_md
            )

        except Exception as e:
            self.logger.error(f"LLM report synthesis failed: {str(e)}. Using fallback synthesis.")
            return self._fallback_synthesis(question, plan, findings, references, url_to_citation)

    def _build_full_markdown(self, raw: RawSynthesisResponse, references: List[Citation]) -> str:
        """Assembles structured report parts into a clean Markdown document with clickable reference links."""
        ref_lines = [
            f"[{r.id}] **[{r.title}]({r.url})** - *{r.domain}* " + (f"({r.published_date})" if r.published_date else "")
            for r in references
        ]
        ref_section = "\n".join(ref_lines) if ref_lines else "No external web references cited."

        key_findings_formatted = "\n".join([f"- {kf}" for kf in raw.key_findings])

        md = f"""# {raw.title}

## Executive Summary
{raw.executive_summary}

---

## Key Findings
{key_findings_formatted}

---

## Research Methodology
{raw.methodology}

---

## Detailed Analysis
{raw.detailed_analysis}

---

## Evidence & Source Assessment
{raw.evidence_and_citations}

---

## Conflicting Evidence & Limitations
{raw.conflicting_evidence_and_limitations}

---

## Unanswered Questions & Evidence Gaps
{raw.unanswered_questions}

---

## Conclusion
{raw.conclusion}

---

## References & Sources
{ref_section}
"""
        return md

    def _fallback_synthesis(
        self, 
        question: str, 
        plan: ResearchPlan, 
        findings: List[Finding], 
        references: List[Citation],
        url_map: Dict[str, Citation]
    ) -> ResearchReport:
        """Rule-based report synthesis when LLM is unavailable."""
        title = f"Deep Research Report: {question}"
        exec_summary = f"This report synthesizes web research findings investigating '{question}' across {len(plan.subquestions)} key sub-topics."
        methodology = f"Execution of search strategy covering {len(plan.subquestions)} subquestions, evaluating web sources and extracting factual claims."
        
        kf = [f.claim for f in findings[:5]] or ["Search executed across multiple query vectors."]

        analysis_parts = []
        for f in findings:
            c_tag = f"[{url_map[f.source_urls[0]].id}]" if f.source_urls and f.source_urls[0] in url_map else ""
            analysis_parts.append(f"### Finding: {f.claim} {c_tag}\n\n*Evidence Quote:* \"{f.evidence_excerpt}\"\n")
        
        analysis = "\n".join(analysis_parts) or "Detailed analysis constructed from retrieved search results."

        raw = RawSynthesisResponse(
            title=title,
            executive_summary=exec_summary,
            methodology=methodology,
            key_findings=kf,
            detailed_analysis=analysis,
            evidence_and_citations="Evidence collected from search engine results.",
            conflicting_evidence_and_limitations="Source evaluation limited to top public web results.",
            unanswered_questions="Further deep domain-specific database searches recommended.",
            conclusion="Research pipeline completed with extracted evidence items."
        )

        full_md = self._build_full_markdown(raw, references)

        return ResearchReport(
            title=raw.title,
            executive_summary=raw.executive_summary,
            methodology=raw.methodology,
            key_findings=raw.key_findings,
            detailed_analysis=raw.detailed_analysis,
            evidence_and_citations=raw.evidence_and_citations,
            conflicting_evidence_and_limitations=raw.conflicting_evidence_and_limitations,
            unanswered_questions=raw.unanswered_questions,
            conclusion=raw.conclusion,
            references=references,
            full_markdown=full_md
        )
