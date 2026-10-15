from typing import Optional
from app.agents.base import BaseAgent
from app.models.research import ResearchPlan, SubQuestion
from app.providers.base import BaseLLMProvider


class ResearchPlanner(BaseAgent):
    """
    Agent responsible for decomposing complex research questions 
    into structured subquestions and search queries.
    """

    SYSTEM_INSTRUCTION = (
        "You are an expert Research Strategy Planner. Your goal is to analyze research questions "
        "and break them down into actionable subquestions and effective search engine queries."
    )

    def create_plan(
        self, 
        question: str, 
        mode: str = "quick", 
        category: Optional[str] = None, 
        date_scope: Optional[str] = None
    ) -> ResearchPlan:
        """Generates a structured research plan."""
        self.logger.info(f"Generating research plan for query: '{question}' (mode={mode})")

        if not self.llm.is_available():
            self.logger.warning("LLM provider unavailable. Generating rule-based fallback research plan.")
            return self._fallback_plan(question, mode)

        num_subquestions = 5 if mode == "deep" else 3
        prompt = (
            f"User Research Question: '{question}'\n"
            f"Research Mode: {mode.upper()}\n"
            f"Category Filter: {category or 'General'}\n"
            f"Date Scope: {date_scope or 'Recent'}\n\n"
            f"Generate a detailed research plan with EXACTLY {num_subquestions} focused subquestions.\n"
            f"For each subquestion, provide 2 to 3 concise, high-precision web search engine queries.\n"
            f"Ensure queries cover market data, recent developments, technical background, and official reports."
        )

        try:
            plan = self.llm.generate_structured(
                prompt=prompt,
                response_schema=ResearchPlan,
                system_instruction=self.SYSTEM_INSTRUCTION
            )
            return plan
        except Exception as e:
            self.logger.error(f"LLM research planning failed: {str(e)}. Using fallback plan.")
            return self._fallback_plan(question, mode)

    def _fallback_plan(self, question: str, mode: str) -> ResearchPlan:
        """Provides an explicit rule-based fallback plan when LLM is unavailable."""
        sq_count = 4 if mode == "deep" else 3
        subquestions = [
            SubQuestion(
                id=f"sq_{i+1}",
                question=f"Key aspect {i+1} regarding: {question}",
                search_queries=[
                    f"{question} key trends overview",
                    f"{question} official statistics reports",
                ]
            )
            for i in range(sq_count)
        ]

        return ResearchPlan(
            refined_question=f"[Fallback Plan] {question}",
            main_objectives=[
                f"Analyze core aspects of: {question}",
                "Gather statistical evidence and expert consensus",
                "Identify key trends and future outlook"
            ],
            subquestions=subquestions,
            time_scope="Recent",
            geographic_scope="Global"
        )
