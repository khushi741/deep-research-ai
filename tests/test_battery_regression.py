import pytest
from app.models.research import ExtractedContent, SubQuestion
from app.agents.source_evaluator import SourceEvaluator
from app.agents.evidence_extractor import EvidenceExtractor
from app.providers.base import BaseLLMProvider
from app.tools.relevance_filter import SemanticRelevanceFilter


class DeterministicFallbackLLM(BaseLLMProvider):
    def generate_text(self, prompt: str, system_instruction=None) -> str:
        raise RuntimeError("LLM disabled for deterministic unit testing")

    def generate_structured(self, prompt: str, response_schema, system_instruction=None):
        raise RuntimeError("LLM disabled for deterministic unit testing")

    def is_available(self) -> bool:
        return False


def test_battery_research_rejects_unrelated_sources():
    """
    CRITICAL REGRESSION TEST:
    Asserts that for a research topic on 'solid-state battery breakthroughs and commercialization',
    the system strictly rejects:
    1. Wikipedia's elementary definition of solid state of matter
    2. Wikipedia's SOLID object-oriented software design principles
    3. Dictionary definitions of the word 'solid'
    4. Automobile dealership sales, inventory, and financing pages
    And accepts:
    5. Primary research paper on solid-state battery electrolyte and energy density
    """
    topic = "What are the current breakthroughs and challenges in solid-state battery commercialization?"
    subquestions = [
        "What are the solid electrolyte materials being developed?",
        "What are the commercialization timelines and cost parity targets for solid-state batteries in EVs?"
    ]

    unrelated_sources = [
        # 1. Wikipedia: Solid state of matter
        ExtractedContent(
            url="https://en.wikipedia.org/wiki/Solid",
            title="Solid - Wikipedia",
            content=(
                "Solid is one of the four fundamental states of matter along with liquid, gas, and plasma. "
                "The molecules in a solid are closely packed together and contain the least amount of kinetic energy. "
                "A solid is characterized by structural rigidity and resistance to a force applied to the surface. "
                "Unlike a liquid, a solid object does not flow to take on the shape of its container."
            ),
            domain="en.wikipedia.org"
        ),
        # 2. Wikipedia: SOLID software design principles
        ExtractedContent(
            url="https://en.wikipedia.org/wiki/SOLID",
            title="SOLID - Wikipedia",
            content=(
                "In software engineering, SOLID is a mnemonic acronym for five design principles intended to make "
                "software designs more understandable, flexible, and maintainable. The principles are Single Responsibility, "
                "Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion. "
                "These object-oriented programming guidelines were promoted by Robert C. Martin."
            ),
            domain="en.wikipedia.org"
        ),
        # 3. Merriam-Webster: Dictionary definition
        ExtractedContent(
            url="https://www.merriam-webster.com/dictionary/solid",
            title="Solid Definition & Meaning - Merriam-Webster",
            content=(
                "Solid adjective: having an interior usually completely filled up, free from voids or cavities. "
                "Firm and stable in shape; not liquid or fluid. Examples of solid in a sentence: a solid piece of wood. "
                "Synonyms: firm, hard, substantial, sound. Medical Definition of solid."
            ),
            domain="merriam-webster.com"
        ),
        # 4. Toyota Dealership sales page
        ExtractedContent(
            url="https://www.toyotaofnaperville.com/inventory/new-toyota-rav4",
            title="New Toyota Cars & SUVs For Sale | Toyota of Naperville Dealership",
            content=(
                "Welcome to Toyota of Naperville! View our new inventory of Camry, RAV4, and Prius models. "
                "Schedule a test drive today or visit our showroom for exclusive lease specials, financing rates, "
                "trade-in appraisal, and Toyota certified auto service. Contact us at 555-0199 for pricing."
            ),
            domain="www.toyotaofnaperville.com"
        ),
        # 5. Legitimate Technical Research Paper on Solid-State Batteries
        ExtractedContent(
            url="https://www.nature.com/articles/s41560-023-01300-8",
            title="High-energy lithium-metal solid-state battery with sulfide electrolytes",
            content=(
                "Solid-state lithium metal batteries promise significantly higher energy density (reaching >450 Wh/kg) "
                "and superior thermal safety compared to conventional liquid electrolyte lithium-ion cells. "
                "Here, we report a halide-coated sulfide solid electrolyte that suppresses lithium dendrite penetration "
                "at room temperature under 5 mA/cm2 current density. The pouch cell maintains 88% capacity retention "
                "over 800 cycles, addressing critical automotive commercialization bottlenecks for next-generation electric vehicles."
            ),
            domain="www.nature.com"
        )
    ]

    evaluator = SourceEvaluator(DeterministicFallbackLLM())
    evaluations = evaluator.evaluate_sources(topic, unrelated_sources, subquestions=subquestions, min_relevance=0.45)

    assert len(evaluations) == 5

    # Check Wikipedia "Solid"
    wiki_solid = next(e for e in evaluations if "wiki/Solid" in e.url)
    assert wiki_solid.is_included is False, f"Expected Wikipedia Solid to be rejected, got relevance={wiki_solid.relevance_score}"
    assert wiki_solid.relevance_score < 0.25
    assert "dictionary" in wiki_solid.exclusion_reason.lower() or "matter" in wiki_solid.exclusion_reason.lower()

    # Check Wikipedia "SOLID"
    wiki_solid_sw = next(e for e in evaluations if "wiki/SOLID" in e.url)
    assert wiki_solid_sw.is_included is False, f"Expected Wikipedia SOLID software to be rejected, got relevance={wiki_solid_sw.relevance_score}"
    assert wiki_solid_sw.relevance_score < 0.25
    assert "software" in wiki_solid_sw.exclusion_reason.lower() or "homonym" in wiki_solid_sw.exclusion_reason.lower()

    # Check Dictionary
    dictionary = next(e for e in evaluations if "merriam-webster" in e.domain)
    assert dictionary.is_included is False, f"Expected dictionary to be rejected, got relevance={dictionary.relevance_score}"
    assert "dictionary" in dictionary.exclusion_reason.lower()

    # Check Dealership
    dealer = next(e for e in evaluations if "toyotaofnaperville" in e.domain)
    assert dealer.is_included is False, f"Expected car dealership to be rejected, got relevance={dealer.relevance_score}"
    assert "dealership" in dealer.exclusion_reason.lower() or "commercial" in dealer.exclusion_reason.lower()

    # Check Genuine Nature Paper
    nature_paper = next(e for e in evaluations if "nature.com" in e.domain)
    assert nature_paper.is_included is True, f"Expected Nature paper to be accepted, got relevance={nature_paper.relevance_score}"
    assert nature_paper.relevance_score >= 0.65
    assert nature_paper.authority_score >= 0.85
    assert "Academic" in nature_paper.source_type or "Nature" in nature_paper.credibility_signals[0]


def test_evidence_extractor_does_not_extract_from_unrelated():
    """Verifies that evidence extractor only extracts real factual passages from relevant sources."""
    subq = SubQuestion(
        id="sq_1",
        question="What are the key solid electrolyte materials?",
        search_queries=["solid electrolyte materials batteries"]
    )
    relevant_source = ExtractedContent(
        url="https://www.nature.com/articles/s41560-023-01300-8",
        title="High-energy lithium-metal solid-state battery with sulfide electrolytes",
        content=(
            "Solid-state lithium metal batteries promise significantly higher energy density reaching 450 Wh/kg. "
            "Here we report a halide-coated sulfide solid electrolyte that suppresses lithium dendrite penetration."
        ),
        domain="www.nature.com"
    )

    extractor = EvidenceExtractor(DeterministicFallbackLLM())
    findings = extractor.extract_evidence(subq, [relevant_source])
    assert len(findings) >= 1
    assert "sulfide solid electrolyte" in findings[0].evidence_excerpt or "energy density" in findings[0].evidence_excerpt
    assert findings[0].source_urls == ["https://www.nature.com/articles/s41560-023-01300-8"]
