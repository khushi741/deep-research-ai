import pytest
from app.models.research import ResearchRequest, ResearchSessionState
from app.services.research_orchestrator import ResearchOrchestrator
from app.providers.base import BaseLLMProvider


class MockEndToEndLLM(BaseLLMProvider):
    def generate_text(self, prompt: str, system_instruction=None) -> str:
        return "Mock LLM Text Output"

    def generate_structured(self, prompt: str, response_schema, system_instruction=None):
        raise RuntimeError("LLM unavailable test fallback trigger")

    def is_available(self) -> bool:
        return False  # Test rule-based deterministic fallback pipeline


@pytest.mark.asyncio
async def test_orchestrator_fallback_e2e_run():
    orchestrator = ResearchOrchestrator(llm_provider=MockEndToEndLLM())
    request = ResearchRequest(
        question="How is AI changing software development in 2026?",
        mode="quick"
    )

    state = await orchestrator.run_research(request)
    
    assert state.status == "completed"
    assert state.report is not None
    assert "AI changing software development" in state.report.title or "Deep Research Report" in state.report.title
    assert state.duration_seconds > 0
