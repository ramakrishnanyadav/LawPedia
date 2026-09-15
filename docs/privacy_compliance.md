# Lawpedia — Regulatory Privacy Compliance Matrix (India DPDP Act 2023 & GDPR)

Lawpedia is designed to comply with privacy frameworks, specifically **India's Digital Personal Data Protection (DPDP) Act 2023** and the **General Data Protection Regulation (GDPR)**.

---

## 1. India DPDP Act 2023 Compliance Matrix

| Section / Principle | DPDP Act 2023 Requirement | Lawpedia Technical Implementation | Automated Test / Artifact |
|---|---|---|---|
| **Section 4 & 6** | **Lawful Purpose & Consent Limitation** | Documents processed solely for contract analysis; tenant-isolated workspace boundaries. | `docs/threat_model.md` |
| **Section 8(4)** | **Data Security Safeguards** | PII redaction pipeline (`backend/services/safety.py`) masking SSN, Aadhaar, PAN, phone, and email before LLM transmission. | `tests/test_security_prompt_injection.py` |
| **Section 8(5)** | **Data Breach Notification & Logging** | Immutable structured audit log (`backend/services/audit.py`) tracking every document access, query, and download. | `backend/services/audit.py` |
| **Section 12** | **Right to Erasure / Data Purge** | Tenant purge API purging document metadata, parsed clauses, vector embeddings, and graph subtrees upon tenant request. | `tests/test_tenant_isolation.py` |
| **Section 9** | **Special Protection for Vulnerable Data** | Strict tenant isolation ensuring no cross-organization training or index leakage. | `tests/test_tenant_isolation.py` |

---

## 2. GDPR Compliance Mapping

| GDPR Article | Requirement | Lawpedia Implementation |
|---|---|---|
| **Article 5(1)(c)** | Data Minimization | Only extracted clauses and relevant evidence spans are retained for indexing. |
| **Article 6(1)** | Lawfulness of Processing | Authenticated, tenant-scoped access controls. |
| **Article 17** | Right to be Forgotten | Complete removal of vectors, graph nodes, and audit references upon document deletion. |
| **Article 32** | Security of Processing | AES-256 equivalent at-rest storage and TLS 1.3 in-transit transport. |
