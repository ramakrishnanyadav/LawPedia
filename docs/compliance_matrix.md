# Lawpedia — Master Compliance & Standards Control Matrix

This document maps international security, AI governance, and compliance standards to the specific technical controls and test suites built into Lawpedia.

---

## Master Compliance Control Cross-Reference

| Framework | Control ID | Control Description | Lawpedia Technical Implementation | Verifying Artifact / Test Suite |
|---|---|---|---|---|
| **OWASP LLM** | **LLM01** | Prompt Injection Defense | Untrusted text wrapped inside `<document_evidence>` sandbox; override keyword redaction. | `tests/test_security_prompt_injection.py` |
| **OWASP LLM** | **LLM02** | Insecure Output Handling | Output text sanitized before DOM rendering; strict schema validation on claims. | `frontend/src/components/AskWorkspace.tsx` |
| **OWASP LLM** | **LLM06** | Sensitive Info Disclosure | PII detection pipeline + pre-retrieval `tenant_id` vector filtering. | `tests/test_tenant_isolation.py` |
| **OWASP LLM** | **LLM09** | Overreliance / Hallucination | Claim-level verification engine + mandatory `INSUFFICIENT_EVIDENCE` abstention. | `tests/test_verification.py`, `tests/test_golden_dataset.py` |
| **OWASP ASVS** | **V4.1** | Access Control Enforcement | Strict tenant data boundary checks on all endpoints (`403`/`404` enforcement). | `tests/test_tenant_isolation.py` |
| **OWASP ASVS** | **V5.1** | Input Validation & Sanitization | Magic byte MIME verification, 25MB file limits, Pydantic v2 schema validation. | `tests/test_ingestion.py` |
| **NIST AI RMF** | **MAP 1.1** | AI System Context & Boundaries | Legal safety boundary disclaimers; non-lawyer assistance framing. | `backend/services/safety.py` |
| **NIST AI RMF** | **MEASURE 2.2**| Claim Support Verification | Claim Support Rate (CSR) tracking on 100-question Golden Dataset. | `tests/test_golden_dataset.py` |
| **ISO 27001** | **A.8.24** | Use of Cryptography | TLS 1.3 transport encryption; secrets loaded via environment Vault settings. | `backend/config.py` |
| **SOC 2** | **CC6.1** | Logical Access Controls | User & tenant IDOR prevention on document, graph, and audit log stores. | `tests/test_tenant_isolation.py` |
| **DPDP Act** | **Sec. 8(4)** | Security Safeguards | Aadhaar, PAN, SSN, phone, email redaction prior to processing. | `tests/test_security_prompt_injection.py` |
