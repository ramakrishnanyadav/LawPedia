# Lawpedia — Comprehensive STRIDE & PASTA Threat Model & Data Flow Analysis

Lawpedia treats all uploaded legal documents as **untrusted source data**, never as executable instructions. This document details the threat model, system trust boundaries, data flow diagram, and automated security controls.

---

## Data Flow Diagram & Trust Boundaries

```
[ User Web Browser ] 
        │ 
        │ (HTTPS / TLS 1.3 - Auth Token + Request Payload)
        ▼
╔══════════════════════════════════════════════════════════════╗
║ TRUST BOUNDARY 1: API GATEWAY & AUTHENTICATION LAYER        ║
║ - JWT/OIDC AuthN/AuthZ Validation                            ║
║ - Tenant Isolation Context Injection (tenant_id)             ║
║ - Request Size & Magic-Byte MIME Enforcement                 ║
╚═══════╤══════════════════════════════════════════════════════╝
        │
        ├───────────────────────────┐
        ▼                           ▼
┌──────────────┐            ┌──────────────────────────────────┐
║ Ingestion    ║            ║ TRUST BOUNDARY 2: LLM GATEWAY    ║
║ Parser       ║            ║ - Prompt Injection Sandbox       ║
║ - OCR        ║            ║   (<document_evidence> wrap)     ║
║ - Structural ║            ║ - Redaction of PII (DPDP 2023)   ║
║   Offset     ║            ║ - Verification Engine Entailment ║
║   Tracing    ║            └───────────────┬──────────────────┘
└───────┬──────┘                            │ (External API / Constrained Sandbox)
        │                                   ▼
        │                           ┌──────────────────┐
        │                           ║ Foundation Model ║
        │                           ║ (Interpreter)    ║
        │                           └──────────────────┘
        ▼
╔══════════════════════════════════════════════════════════════╗
║ TRUST BOUNDARY 3: TENANT-ISOLATED DATA STORE                 ║
║ - Vector Store (Filtered by tenant_id)                       ║
║ - BM25 Lexical Index (Filtered by tenant_id)                 ║
║ - Legal Evidence Graph Subtrees (Filtered by tenant_id)      ║
║ - Immutable Structured Audit Logs                            ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Top 8 Threat Vectors & Automated Mitigations Matrix

| # | Threat Vector (STRIDE / PASTA) | Risk Level | Mitigation Control | Automated Test Verification |
|---|---|---|---|---|
| **T1** | **Direct & Indirect Prompt Injection** (Tampering) | CRITICAL | Parse documents to structured evidence spans; wrap inside `<document_evidence>` sandbox; redact override keywords. | `tests/test_security_prompt_injection.py` |
| **T2** | **Cross-Tenant Data Leakage / IDOR** (Information Disclosure) | CRITICAL | Hard tenant filter (`tenant_id`) enforced on vector, lexical, graph, and audit log DB queries. | `tests/test_tenant_isolation.py` |
| **T3** | **PII Exposure / DPDP Non-Compliance** (Information Disclosure) | HIGH | PII detection & redaction engine (SSN, Aadhaar, PAN, phone, email) before LLM egress. | `tests/test_security_prompt_injection.py` |
| **T4** | **Parser Decompression / XML Bomb DoS** (Denial of Service) | HIGH | Magic-byte file validation, 25MB upload cap, 100-page limit, parsing timeout bounds. | `tests/test_ingestion.py` |
| **T5** | **Hallucination / Citation Fabrication** (Elevation of Privilege) | HIGH | Claim-level entailment checking against retrieved evidence; force `INSUFFICIENT_EVIDENCE` abstention. | `tests/test_verification.py`, `tests/test_golden_dataset.py` |
| **T6** | **Audit Trail Evasion / Log Tampering** (Repudiation) | MEDIUM | Immutable structured JSON audit logger recording user ID, tenant ID, action, timestamp, and IP. | `tests/test_tenant_isolation.py` |
| **T7** | **Vector Index / Storage Failure** (Denial of Service) | MEDIUM | Graceful degradation to BM25 lexical search with reduced confidence banner. | `tests/test_chaos_resilience.py` |
| **T8** | **Stored XSS via Rendered Clauses** (Tampering / Elevation) | MEDIUM | React text sanitization and HTML escaping on all rendered clause text and answers. | `frontend/src/components/AskWorkspace.tsx` |

---

## Security Compliance Mapping

- **OWASP LLM Top 10**: LLM01 (Prompt Injection), LLM02 (Insecure Output), LLM06 (Sensitive Info Disclosure), LLM09 (Misconfiguration).
- **OWASP ASVS v4.0**: Level 2 Verification Requirements (V4 Access Control, V5 Input Validation, V8 Data Protection).
- **India DPDP Act 2023**: Section 6 (Data Minimization & Purpose Limitation), Section 8 (Security Safeguards & Breach Notification), Section 12 (Right to Erasure).
