# Lawpedia — Problem Statement Alignment & Traceability Matrix

This document provides a 1-to-1 mapping between every use case in the official problem statement and the concrete Lawpedia feature, module implementation, and demonstration scenario that validates it.

| Problem Statement Use Case | Lawpedia Feature | Implementing Module | Demo Scenario |
|---|---|---|---|
| **Simplifying complex legal documents** | Plain-language answer layer, Document Intelligence summary | `backend/services/extraction.py`, `backend/services/response.py` | Scenario 1: Simple document question |
| **Comparing contracts, agreements, or policies** | Semantic Contract Comparison matrix & risk shift analysis | `backend/services/comparison.py` | Scenario 2: Contract comparison |
| **Highlighting clauses, obligations, risks, inconsistencies** | Clause Explorer, Risk Indicators, Conflict Detection Engine | `backend/services/graph.py`, `backend/services/conflict.py` | Scenario 3: Conflicting clauses |
| **Answering questions based on provided documents** | Ask Workspace with claim-level provenance & verification | `backend/services/retrieval.py`, `backend/services/verification.py` | Scenario 5: False-premise question |
| **Helping users understand options / next steps** | Action Checklist, "Questions to ask a lawyer" | `backend/services/handoff.py`, `backend/services/response.py` | Scenario 10: Lawyer handoff report |
| **Generating summaries, checklists, actionable outputs** | Document Intelligence summary, Lawyer Handoff Pack | `backend/services/handoff.py` | Scenario 6: Important deadline extraction |
| **Preparing info/questions for a legal professional** | 10-part Lawyer Handoff Pack export | `backend/services/handoff.py` | Scenario 10: Lawyer handoff report |
| **Information/assistance, not replacing legal advice** | Safety Gateway disclaimers & explicit abstention | `backend/services/safety.py`, `backend/services/verification.py` | Scenario 8: Insufficient-evidence (Abstention) |

---

## Technical Verification Criteria Mapping

1. **Code Quality**:
   - Schema-first Pydantic v2 validation models (`backend/schemas/eglr.py`).
   - Modular backend architecture with clear separation of ingestion, retrieval, graph traversal, verification, and safety.
   - Fully type-hinted Python backend and strict TypeScript frontend.

2. **Security**:
   - Prompt Injection Defense boundary (`PDF -> Parser -> Evidence -> Constrained Sandbox Prompt`).
   - Threat Model documented in `/docs/threat_model.md` covering STRIDE analysis.
   - PII filtering and payload validation on all endpoints.

3. **Efficiency**:
   - Hybrid retrieval combining BM25 lexical indexing with Dense Vector Search and Reciprocal Rank Fusion (RRF).
   - Document-level embedding caching to avoid re-embedding unchanged documents.
   - Model routing: lightweight parsing & extraction vs. deep reasoning for complex queries.

4. **Testing**:
   - Unit tests (`tests/test_ingestion.py`, `tests/test_retrieval.py`, `tests/test_verification.py`).
   - Adversarial prompt injection tests (`tests/test_security_prompt_injection.py`).
   - Golden Dataset benchmark suite (`tests/test_golden_dataset.py`) measuring CSR, CDR, and FPRR.

5. **Accessibility**:
   - WCAG 2.2 AA compliant UI design.
   - Visible focus states, full keyboard navigation.
   - Text/table alternatives for SVG Legal Evidence Graph visualizer.
   - High-contrast badges with icons + text (not color alone).
