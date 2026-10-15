# Deep Research AI — Key Design Decisions & Engineering Trade-Offs

## 1. Orchestrated Multi-Stage Workflow vs. Uncontrolled Recursive Loop

### Choice: Bounded Stage Orchestration
We chose an explicitly orchestrated multi-stage pipeline (`Planner -> Search -> Extract -> Evaluate -> Evidence -> Synthesize`) with a bounded follow-up pass instead of an unconstrained agent recursion.

### Trade-off & Rationale:
- **Cost & Rate Limits:** Autonomous agent loops risk infinite retries, rapid API quota exhaustion, and unpredictable latency.
- **Observability:** Users can clearly observe the exact phase of research in the UI.
- **Traceability:** Every step produces a Pydantic-validated output that can be logged, tested, and audited.

---

## 2. Security Safeguards: SSRF & Prompt Injection Defense

### Choice: Multi-Layered Security Controls
1. **SSRF Mitigation:**
   - Pre-request URL scheme validation (allowing `http` and `https` only).
   - DNS host resolution checking against blocked IPv4/IPv6 ranges (loopback, RFC 1918 private networks, link-local `169.254.169.254` cloud metadata IP).
   - Manual HTTP redirect re-verification to prevent open-redirect SSRF bypasses.

2. **Prompt Injection Mitigation:**
   - External web page content is treated as **untrusted data**.
   - Content is sanitized of system instructions and jailbreak patterns.
   - Web text is wrapped inside `<untrusted_web_source url="...">` XML blocks before injection into LLM context windows.

---

## 3. Strict Citation & Traceability Model

### Choice: Verifiable Bracketed References `[1]`, `[2]`
- Claims are only included when supported by extracted web evidence quotes.
- The Synthesizer maps each unique source URL to a numeric reference ID `[1]`, maintaining a clean bibliography mapping URL, publisher domain, and date.
- No invented URLs or statistics are permitted.

---

## 4. Provider Abstraction Architecture

### Choice: `BaseLLMProvider` Abstraction
- The system depends on `BaseLLMProvider` rather than concrete SDK calls inside agents.
- Defaults to Google Gemini API via official `google-genai` / `google.generativeai` SDK.
- Swapping to another LLM provider (e.g. Anthropic, OpenAI, or local Ollama) requires implementing a single class without modifying any agent logic.
