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

# Custom High-End Styling Matching React Frontend Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global typography & background */
    html, body, [class*="css"], .stMarkdown, p, div {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #0B0F19;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
        background-attachment: fixed;
        color: #F8FAFC;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(11, 15, 25, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Hero section styling */
    .hero-container {
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 1.1rem;
        border-radius: 9999px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        font-size: 0.85rem;
        font-weight: 600;
        color: #60A5FA;
        margin-bottom: 1rem;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
    }

    .hero-title {
        font-size: 2.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.15;
        margin-bottom: 0.8rem;
        color: #FFFFFF;
    }

    .gradient-text {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.08rem;
        color: #94A3B8;
        max-width: 680px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Glassmorphic card utility */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        margin-bottom: 1.5rem;
    }

    /* Primary glowing action button */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 4px 20px -2px rgba(59, 130, 246, 0.5) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
    }

    /* Metric cards */
    .metric-card-container {
        background: rgba(17, 24, 39, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.1rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card-container:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    .metric-number {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Key Finding Callout */
    .finding-card {
        background: rgba(17, 24, 39, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #8B5CF6;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.9rem;
        color: #E2E8F0;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Source Box Styling */
    .source-box {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #3B82F6;
        padding: 1rem 1.25rem;
        margin-bottom: 0.9rem;
        border-radius: 10px;
        transition: border-color 0.2s ease;
    }
    .source-box:hover {
        border-color: #60A5FA;
    }
    .source-box a {
        color: #60A5FA !important;
        text-decoration: none;
        font-weight: 600;
    }
    .source-box a:hover {
        text-decoration: underline;
    }

    /* Status Pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .status-badge-active {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
    }
    .status-badge-pending {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60A5FA;
    }

    /* Pulse dot animation */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34D399;
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
        animation: pulse 1.6s infinite cubic-bezier(0.66, 0, 0, 1);
    }
    @keyframes pulse {
        to {
            box-shadow: 0 0 0 10px rgba(52, 211, 153, 0);
        }
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.4);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.2) !important;
        color: #60A5FA !important;
        border-bottom: 2px solid #3B82F6 !important;
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
    st.sidebar.markdown("""
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.6rem;">🔍</span>
            <span style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">Deep Research AI</span>
        </div>
        <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 1rem;">
            Autonomous multi-step research agent with citation verification.
        </p>
    """, unsafe_allow_html=True)
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
        st.sidebar.markdown("""
            <div style="padding: 0.65rem 0.9rem; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <span class="pulse-dot"></span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #34D399;">Gemini LLM Configured</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.warning("⚠️ GEMINI_API_KEY Required")
        st.sidebar.info(
            "**API Key Required:**\n"
            "Set `GEMINI_API_KEY` in Streamlit Cloud Secrets or enter your key above.\n\n"
            "Get a free key at: [Google AI Studio](https://aistudio.google.com/)"
        )

    tavily_status = bool(os.getenv("TAVILY_API_KEY") or (st.secrets.get("TAVILY_API_KEY") if hasattr(st, "secrets") else None))
    if tavily_status:
        st.sidebar.markdown("""
            <div style="padding: 0.65rem 0.9rem; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #60A5FA;">⚡ Tavily Search Active</span>
            </div>
        """, unsafe_allow_html=True)
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

    # Hero Header Section
    st.markdown("""
        <div class="hero-container">
            <div class="hero-badge">⚡ Autonomous AI Research & Verification Agent</div>
            <h1 class="hero-title">Research Smarter. <span class="gradient-text">Verify Sources.</span> Discover Insights.</h1>
            <p class="hero-subtitle">
                Deep Research AI autonomously executes multi-step web queries, validates publisher credibility, extracts structured evidence, and synthesizes cited whitepapers.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Example Query Suggestions
    if "selected_query" not in st.session_state:
        st.session_state["selected_query"] = ""

    st.markdown('<div style="font-size: 0.88rem; font-weight: 600; color: #94A3B8; margin-bottom: 0.4rem;">💡 Or try an example research question:</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🤖 AI Impact on Software Jobs (2026)", use_container_width=True):
            st.session_state["selected_query"] = "How is generative AI changing software engineering jobs in India in 2026?"
            st.rerun()
    with c2:
        if st.button("🔋 Solid-State Battery Breakthroughs", use_container_width=True):
            st.session_state["selected_query"] = "What are the latest breakthroughs and commercialization challenges in solid-state EV batteries?"
            st.rerun()
    with c3:
        if st.button("🔐 Quantum Cryptography Progress", use_container_width=True):
            st.session_state["selected_query"] = "Quantum computing advancements in cryptography, post-quantum standards, and timeline"
            st.rerun()

    # Input Form
    with st.form("research_form"):
        default_val = st.session_state.get("selected_query", "")
        question = st.text_area(
            "Enter your research question:",
            value=default_val,
            placeholder="e.g., How is generative AI changing software engineering jobs in India in 2026?",
            height=110
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            mode = st.radio("Research Depth:", ["quick", "deep"], format_func=lambda x: "⚡ Quick Research" if x == "quick" else "🔍 Deep Research")
        with col2:
            category = st.selectbox("Topic Category (Optional):", ["General", "Technology & AI", "Economics & Business", "Science & Medicine", "Policy & Law"])
        with col3:
            date_scope = st.selectbox("Date Scope:", ["Past Year (Recent)", "Past 3 Years", "All Time"])

        submit_btn = st.form_submit_button("🚀 Launch Autonomous Research Run", use_container_width=True)

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
        status_box = st.empty()

        def update_progress(state: ResearchSessionState):
            stage_map = {
                "planning": 20,
                "searching": 45,
                "evaluating": 65,
                "extracting": 82,
                "synthesizing": 92,
                "completed": 100,
                "failed": 100
            }
            pct = stage_map.get(state.status, 5)
            progress_bar.progress(pct)
            status_box.markdown(f"""
                <div class="glass-card" style="margin-top: 1rem; border-color: rgba(59, 130, 246, 0.4);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span class="status-badge status-badge-active">
                            <span class="pulse-dot"></span> Agent {state.status.upper()}
                        </span>
                        <span style="font-size: 0.82rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace;">
                            Pipeline Progress: {pct}%
                        </span>
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF;">
                        {state.current_stage}
                    </div>
                </div>
            """, unsafe_allow_html=True)

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
        st.markdown(f"""
            <div class="metric-card-container">
                <div class="metric-number">{state.duration_seconds}s</div>
                <div class="metric-label">Execution Time</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-card-container">
                <div class="metric-number">{state.sources_count}</div>
                <div class="metric-label">Sources Evaluated</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-card-container">
                <div class="metric-number">{state.findings_count}</div>
                <div class="metric-label">Evidence Findings</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="metric-card-container">
                <div class="metric-number">{len(report.references)}</div>
                <div class="metric-label">Verified Citations</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

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
            label="📄 Download Publication PDF",
            data=pdf_bytes,
            file_name=f"research_report_{state.id[:8]}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()

    # Tabs for Report View
    report_tabs = st.tabs(["📄 Full Synthesis Report", "📌 Key Findings", "🔗 Sources & Citations", "📋 Research Strategy"])

    with report_tabs[0]:
        st.markdown(report.full_markdown)

    with report_tabs[1]:
        st.subheader("Key Findings & Core Insights")
        for idx, kf in enumerate(report.key_findings, 1):
            st.markdown(f"""
                <div class="finding-card">
                    <span style="font-weight: 700; color: #A78BFA; margin-right: 0.4rem;">#{idx}</span> {kf}
                </div>
            """, unsafe_allow_html=True)

    with report_tabs[2]:
        st.subheader("Evaluated Sources & Verifiable References")
        for ref in report.references:
            st.markdown(
                f'<div class="source-box">'
                f'<b>[{ref.id}] <a href="{ref.url}" target="_blank">{ref.title}</a></b><br/>'
                f'<small style="color: #94A3B8;">Domain: <code>{ref.domain}</code> | Published: {ref.published_date or "N/A"}</small>'
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
