# Lawpedia — SRE Service Level Objectives (SLOs) & Reliability Targets

This document defines the Service Level Objectives (SLOs), Service Level Indicators (SLIs), Error Budgets, and Mean Time to Detect/Recover (MTTD/MTTR) targets for **Lawpedia**.

---

## Service Level Objectives (SLOs)

| Service Endpoint / Capability | Service Level Indicator (SLI) | Target SLO | Monthly Error Budget | Graceful Degradation Strategy |
|---|---|---|---|---|
| **Legal Query API (`/api/query`)** | % of requests completed < 500ms | **99.5%** | 0.5% (~216 mins) | Fallback to BM25 lexical search if vector index is degraded. |
| **Document Ingestion (`/api/upload`)** | % of 50-page PDFs parsed < 10s | **99.0%** | 1.0% (~432 mins) | Queue-based asynchronous background processing. |
| **API Availability (`/api/*`)** | % of successful 2xx/3xx HTTP responses | **99.9%** | 0.1% (~43 mins) | Auto-abstention (`INSUFFICIENT_EVIDENCE`) instead of 500. |
| **Claim Support Rate (CSR)** | Supported generated claims / total claims | **≥ 95.0%** | 5.0% unsupported | Mandatory explicit abstention when grounding is absent. |

---

## Operational Incident Targets

- **Target MTTD (Mean Time to Detect)**: < 2 minutes via automated SLO burn-rate alerting.
- **Target MTTR (Mean Time to Recover)**: < 5 minutes via automated container health checks and circuit breakers.
