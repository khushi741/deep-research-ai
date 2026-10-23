from app.models.research import ExtractedContent
from app.agents.source_evaluator import SourceEvaluator
from app.providers.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_instruction=None) -> str:
        return "Mock text response"

    def generate_structured(self, prompt: str, response_schema, system_instruction=None):
        from app.agents.source_evaluator import SourceEvaluationResponse
        from app.models.research import SourceEvaluation
        return SourceEvaluationResponse(evaluations=[
            SourceEvaluation(
                url="https://example.gov/report",
                title="Official Government Report on Energy",
                domain="example.gov",
                relevance_score=0.9,
                authority_score=0.95,
                source_type="Primary Academic / Government",
                credibility_signals=["Official domain"],
                reasoning="Primary government source",
                published_date="2026-01-01"
            )
        ])

    def is_available(self) -> bool:
        return True


def test_source_evaluator_with_mock_llm():
    provider = MockLLMProvider()
    evaluator = SourceEvaluator(provider)
    sources = [
        ExtractedContent(
            url="https://example.gov/report",
            title="Official Government Report on Energy",
            content=(
                "Detailed research statistical findings regarding sample query energy development. "
                "This comprehensive investigation provides verified empirical evidence, official data, "
                "and technological milestones for the sample query topic across the industry."
            ),
            domain="example.gov"
        )
    ]
    evals = evaluator.evaluate_sources("Sample query energy development", sources)
    assert len(evals) == 1
    assert evals[0].authority_score >= 0.90
    assert "Academic" in evals[0].source_type or "Government" in evals[0].source_type
    assert evals[0].is_included is True


def test_source_evaluator_rule_based_fallback():
    class UnavailableLLM(BaseLLMProvider):
        def generate_text(self, prompt: str, system_instruction=None) -> str:
            raise RuntimeError("Unavailable")
        def generate_structured(self, prompt: str, response_schema, system_instruction=None):
            raise RuntimeError("Unavailable")
        def is_available(self) -> bool:
            return False

    evaluator = SourceEvaluator(UnavailableLLM())
    sources = [
        ExtractedContent(
            url="https://harvard.edu/paper",
            title="University Paper on Quantum Computing",
            content=(
                "Harvard research laboratory findings on quantum computing architectures, "
                "superconducting qubits, coherence times, and fault-tolerant quantum error correction."
            ),
            domain="harvard.edu"
        )
    ]
    evals = evaluator.evaluate_sources("Quantum computing architectures", sources)
    assert len(evals) == 1
    assert evals[0].authority_score >= 0.85  # .edu academic rule
    assert evals[0].is_included is True
