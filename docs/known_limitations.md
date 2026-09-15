# LawPedia — Known Limitations & System Boundaries

This document provides a calibrated, honest technical assessment of LawPedia's operational boundaries, architectural trade-offs, and current functional limitations.

---

## 1. Concurrency & Database Engine (SQLite vs. PostgreSQL)

### Current Architecture
* LawPedia currently uses an embedded **SQLite** database (`lawpedia.db` with WAL mode enabled) for persistent document, clause, and audit logging storage.

### Known Limitations
* **Concurrent Writes**: SQLite uses database-level locking for write operations. Under high concurrent write loads (e.g., hundreds of simultaneous document uploads across tenants), write requests will queue and potentially experience lock timeouts.
* **Horizontal Scaling**: SQLite files are stored on local disk and cannot be shared directly across multiple horizontally scaled application worker nodes without shared file systems (e.g., NFS), which can introduce file lock latency.

### Production Migration Path
* For multi-tenant production deployments requiring high-concurrency writes, SQLite should be swapped for **PostgreSQL** using SQLAlchemy or SQLModel ORM.
* A step-by-step PostgreSQL migration guide and schema configuration notes are documented in [`docker-compose.yml`](../docker-compose.yml).

---

## 2. Simplification Engine & Degradation Modes

### Current Architecture
* LawPedia supports hybrid simplification: calling **OpenAI** (`gpt-4o-mini`) or **Anthropic** (`claude-3-5-haiku-20241022`) when API credentials are provided server-side, and degrading to a clause-aware rule-based translation fallback (`fallback_no_llm_configured`) when API keys are absent or rate limits/circuit breakers trigger.

### Known Limitations
* **Rule-Based Fallback Quality**: The fallback path uses regex pattern substitutions (e.g., `shall` -> `must`, `indemnify` -> `protect from legal financial loss`) combined with clause-type structural prefixes. While deterministic, fast, and free, it lacks natural language paraphrasing depth for highly complex nested legal periods.
* **LLM Dependency**: Full plain-English summarization at simple reading levels relies on external LLM APIs. If external services suffer outages or reach quota limits, the system seamlessly falls back to degraded mode and explicitly tags API outputs (`[MODE: FALLBACK_RULE_BASED]`).

---

## 3. Security & Prompt-Injection Filtering

### Current Architecture
* LawPedia employs a two-pass defense against prompt injection:
  1. Structural XML element tag escaping (`&lt;/document_evidence&gt;`) to enforce strict instruction-vs-data separation.
  2. Multi-pass heuristic classifier scanning for instruction override patterns across English, Spanish, French, German, Unicode obfuscations, base64 tokens, and token-split phrases.

### Known Limitations
* **Adversarial Boundary**: Heuristic-based regex and keyword density checks raise the bar against standard jailbreaks, but complex multi-turn or novelty adversarial attacks targeting LLM tokenization logic cannot be guaranteed 100% immune by pattern matching alone.
* **Document Source Content**: If an uploaded PDF or document contains malicious text attempting to hijack downstream model behavior, SafetyGateway strips structural tags and tags output mode, but extreme semantic adversarial payloads may still require fine-tuned small guardrail models (e.g. Llama-Guard) in high-stakes environments.

---

## 4. Legal Scope & Jurisdictional Caveats

### Current Architecture
* LawPedia identifies governing law clauses and tags evidence spans with jurisdiction metadata.

### Known Limitations
* **No Statutory Override Lookup**: LawPedia analyzes the *text of uploaded contracts*, but does not dynamically query live state/national legislative databases. Mandatory statutory overrides (e.g., local state labor laws overriding contract non-compete clauses) require professional legal review.
* **Legal Information vs. Advice**: LawPedia provides document intelligence, clause comparison, and question preparation tools. It is explicitly designed to assist users in preparing for professional counsel, not replace licensed legal representation.
