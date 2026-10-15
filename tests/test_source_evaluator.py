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
                title="Official Government Report",
                domain="example.gov",
                relevance_score=0.9,
                authority_score=0.95,
                source_type="Academic/Government",
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
            title="Official Government Report",
            content="Detailed research statistical findings.",
            domain="example.gov"
        )
    ]
    evals = evaluator.evaluate_sources("Sample query", sources)
    assert len(evals) == 1
    assert evals[0].authority_score == 0.95
    assert evals[0].source_type == "Academic/Government"


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
            title="University Paper",
            content="Sample text content for testing.",
            domain="harvard.edu"
        )
    ]
    evals = evaluator.evaluate_sources("Test query", sources)
    assert len(evals) == 1
    assert evals[0].authority_score >= 0.8  # .edu domain rule
