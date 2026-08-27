# Prompt Changelog

All prompts used across Task 1 (Ticket Triage), Task 2 (TAM Account Health Summariser), and Task 3 (LLM-as-Judge Evals) are version-controlled and tracked here.

---

## [v1.0.0] - 2026-08-08

### Task 1: Intelligent Ticket Triage Agent
- **Added `TRIAGE_SYSTEM_PROMPT`**: Configured strict JSON schema enforcement for `product_area`, `category`, `urgency` (P1-P4), `urgency_reasoning`, `recommended_responder_team`, and `draft_response`.
- **Added `TRIAGE_USER_PROMPT_TEMPLATE`**: Injects raw ticket subject/body alongside RAG Knowledge Base context snippets.

### Task 2: TAM Account Health Summariser
- **Added `ACCOUNT_SUMMARISER_SYSTEM_PROMPT`**: Enforces 3-section QBR brief structure (Executive Summary, Open Risks & Flagged Issues, Recommended Talking Points).
- **Added Direct Quote Rule**: Requires explicit `direct_quote_evidence` extracted from raw ticket text to prevent hallucinated churn risk flags.
- **Deterministic Output Controls**: Set model temperature to `0.0` with seed control.

### Task 3: LLM-as-Judge Evals
- **Added `EVAL_JUDGE_SYSTEM_PROMPT`**: Standardized scoring schema (0.0 to 1.0) with pass/fail decision logic based on automated acceptance criteria.
