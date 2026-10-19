import os
import sys
import asyncio
import time
from typing import Optional
import streamlit as st

# Add root project path to sys.path for direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.models.research import ResearchRequest, ResearchSessionState
from app.services.research_orchestrator import ResearchOrchestrator
from app.services.export_service import ExportService
from app.storage.repository import ResearchRepository
from app.providers.gemini_provider import GeminiLLMProvider

st.set_page_config(
    page_title="Deep Research AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .tagline {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .source-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #3B82F6;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Sync Streamlit Cloud secrets to environment if present
try:
    if hasattr(st, "secrets"):
        for sec_key, sec_val in st.secrets.items():
            if isinstance(sec_val, str) and sec_key not in os.environ:
                os.environ[sec_key] = sec_val
except Exception:
    pass

repository = ResearchRepository()


def main():
    # Sidebar Navigation & Settings
    st.sidebar.title("🔍 Deep Research AI")
    st.sidebar.markdown("**Tagline:** Research smarter. Verify sources. Discover insights.")
    st.sidebar.divider()

    # Determine Gemini API Key from environment, secrets, or sidebar input
    env_key = os.getenv("GEMINI_API_KEY") or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None)
    user_key = None

    if not env_key:
        user_key = st.sidebar.text_input(
            "Gemini API Key:",
            type="password",
            placeholder="AIzaSy...",
            help="Get a free key from https://aistudio.google.com/"
        )
        if user_key:
            os.environ["GEMINI_API_KEY"] = user_key

    active_key = user_key or env_key
    provider = GeminiLLMProvider(api_key=active_key)

    # System Status & Setup Instructions
    api_status = provider.is_available()
    if api_status:
        st.sidebar.success("✅ Gemini LLM Configured")
    else:
        st.sidebar.warning("⚠️ GEMINI_API_KEY Required")
        st.sidebar.info(
            "**API Key Required:**\n"
            "Set `GEMINI_API_KEY` in Streamlit Cloud Secrets or enter your key above.\n\n"
            "Get a free key at: [Google AI Studio](https://aistudio.google.com/)"
        )

    tavily_status = bool(os.getenv("TAVILY_API_KEY") or (st.secrets.get("TAVILY_API_KEY") if hasattr(st, "secrets") else None))
    if tavily_status:
        st.sidebar.success("✅ Tavily Search Configured")
    else:
        st.sidebar.caption("ℹ️ Search Engine: DuckDuckGo (Free & Built-in)")

    st.sidebar.divider()
    nav_option = st.sidebar.radio("Navigation", ["New Research", "Research History", "API Setup & Docs"])

    if nav_option == "New Research":
        render_new_research_page(provider)
    elif nav_option == "Research History":
        render_history_page()
    else:
        render_docs_page()


def render_new_research_page(provider: Optional[GeminiLLMProvider] = None):
    if provider is None:
        provider = GeminiLLMProvider()

    st.markdown('<div class="main-header">Deep Research AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Research smarter. Verify sources. Discover insights.</div>', unsafe_allow_html=True)

    # Input Form
    with st.form("research_form"):
        question = st.text_area(
            "Enter your research question:",
            placeholder="e.g., How is generative AI changing software engineering jobs in India in 2026?",
            height=100
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            mode = st.radio("Research Depth:", ["quick", "deep"], format_func=lambda x: "⚡ Quick Research" if x == "quick" else "🔍 Deep Research")
        with col2:
            category = st.selectbox("Topic Category (Optional):", ["General", "Technology & AI", "Economics & Business", "Science & Medicine", "Policy & Law"])
        with col3:
            date_scope = st.selectbox("Date Scope:", ["Past Year (Recent)", "Past 3 Years", "All Time"])

        submit_btn = st.form_submit_button("🚀 Start Research Run", use_container_width=True)

    if submit_btn:
        if not question or len(question.strip()) < 5:
            st.error("Please enter a research question of at least 5 characters.")
            return

        if not provider.is_available():
            st.error("Gemini API Key is not configured or invalid. Please configure GEMINI_API_KEY in the sidebar or environment.")
            return

        orchestrator = ResearchOrchestrator(llm_provider=provider)

        # Progress UI Placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        live_stage_box = st.info("Initializing research pipeline...")

        def update_progress(state: ResearchSessionState):
            stage_map = {
                "planning": 15,
                "searching": 35,
                "evaluating": 60,
                "extracting": 80,
                "synthesizing": 90,
                "completed": 100,
                "failed": 100
            }
            pct = stage_map.get(state.status, 5)
            progress_bar.progress(pct)
            status_text.markdown(f"**Current Status:** `{state.status.upper()}` — {state.current_stage}")

        req = ResearchRequest(
            question=question.strip(),
            mode=mode,
            category=category,
            date_scope=date_scope
        )

        # Run Async Research Pipeline
        with st.spinner("Executing autonomous agent research pipeline..."):
            session_state = asyncio.run(orchestrator.run_research(req, progress_callback=update_progress))
            repository.save_session(session_state)

        if session_state.status == "completed" and session_state.report:
            st.success(f"🎉 Research completed in {session_state.duration_seconds}s!")
            render_report_results(session_state)
        else:
            st.error(f"Research run failed: {session_state.error_message}")


def render_report_results(state: ResearchSessionState):
    report = state.report
    if not report:
        return

    st.divider()

    # Metrics Summary Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Duration", f"{state.duration_seconds}s")
    with m2:
        st.metric("Sources Discovered", state.sources_count)
    with m3:
        st.metric("Evidence Findings", state.findings_count)
    with m4:
        st.metric("References Cited", len(report.references))

    # Export Buttons
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        md_bytes = ExportService.generate_markdown_bytes(report)
        st.download_button(
            label="📥 Download Markdown Report",
            data=md_bytes,
            file_name=f"research_report_{state.id[:8]}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_exp2:
        pdf_bytes = ExportService.generate_pdf_bytes(report)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"research_report_{state.id[:8]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()

    # Tabs for Report View
    tab1, tab2, tab3, tab4 = st.columns(4)
    
    report_tabs = st.tabs(["📄 Full Synthesis Report", "📌 Key Findings", "🔗 Sources & Citations", "📋 Research Plan & Strategy"])

    with report_tabs[0]:
        st.markdown(report.full_markdown)

    with report_tabs[1]:
        st.subheader("Key Findings & Core Insights")
        for idx, kf in enumerate(report.key_findings, 1):
            st.markdown(f"**{idx}.** {kf}")

    with report_tabs[2]:
        st.subheader("Evaluated Sources & Verifiable References")
        for ref in report.references:
            st.markdown(
                f'<div class="source-box">'
                f'<b>[{ref.id}] <a href="{ref.url}" target="_blank">{ref.title}</a></b><br/>'
                f'<small>Domain: <code>{ref.domain}</code> | Published: {ref.published_date or "N/A"}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

        if state.sources:
            st.divider()
            st.subheader("Detailed Source Credibility Evaluations")
            for s in state.sources:
                with st.expander(f"{s.title} ({s.domain})"):
                    st.write(f"**URL:** {s.url}")
                    st.write(f"**Relevance Score:** {s.relevance_score} / 1.0")
                    st.write(f"**Authority Score:** {s.authority_score} / 1.0")
                    st.write(f"**Source Type:** {s.source_type}")
                    st.write(f"**Credibility Signals:** {', '.join(s.credibility_signals)}")
                    st.write(f"**Evaluation Rationale:** {s.reasoning}")

    with report_tabs[3]:
        st.subheader("Decomposed Research Strategy")
        if state.plan:
            st.write(f"**Refined Question:** {state.plan.refined_question}")
            st.write("**Objectives:**")
            for obj in state.plan.main_objectives:
                st.write(f"- {obj}")

            st.write("**Subquestions & Search Queries:**")
            for sq in state.plan.subquestions:
                with st.expander(f"{sq.id}: {sq.question}"):
                    for q in sq.search_queries:
                        st.code(q, language="text")


def render_history_page():
    st.subheader("📜 Local Research Session History")
    sessions = repository.list_sessions()

    if not sessions:
        st.info("No research sessions stored in local history.")
        return

    for session in sessions:
        with st.expander(f"[{session.created_at[:19]}] {session.question} ({session.mode.upper()})"):
            st.write(f"**Status:** `{session.status}` | **Duration:** {session.duration_seconds}s")
            st.write(f"**Sources Evaluated:** {session.sources_count} | **Findings Extracted:** {session.findings_count}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"View Report", key=f"view_{session.id}"):
                    st.session_state[f"show_{session.id}"] = True
            with c2:
                if st.button(f"Delete Session", key=f"del_{session.id}"):
                    repository.delete_session(session.id)
                    st.rerun()

            if st.session_state.get(f"show_{session.id}", False):
                render_report_results(session)


def render_docs_page():
    st.subheader("📚 API Setup & Architecture Documentation")
    st.markdown("""
### Deep Research AI Setup Guide

1. **Obtain API Keys:**
   - **Google Gemini API Key:** Required for LLM planning, evidence extraction, and synthesis. Obtain from [Google AI Studio](https://aistudio.google.com/).
   - **Tavily Search API Key:** Optional. High-precision search API. If absent, DuckDuckGo search is used automatically.

2. **Environment Configuration:**
   Copy `.env.example` to `.env` in the root folder:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

3. **Running Backend & Frontend:**
   - **FastAPI Backend:** `uvicorn app.main:app --reload --port 8000`
   - **Streamlit Frontend:** `streamlit run frontend/streamlit_app.py`
""")


if __name__ == "__main__":
    main()
