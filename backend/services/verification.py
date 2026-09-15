"""
Claim-Level Semantic Entailment Verification Engine
"""

import uuid
import re
import numpy as np
from typing import Optional
from backend.schemas.eglr import ClaimVerification, EvidenceSpan, SupportStatus


from backend.services.safety import SafetyGateway
from backend.services.retrieval import get_sentence_model


class ClaimVerificationEngine:
    """
    Deconstructs generated responses into individual legal claims and evaluates
    their semantic entailment against retrieved document evidence spans.
    """

    @staticmethod
    def verify_claims(claims_raw: list[str], evidence_spans: list[EvidenceSpan]) -> list[ClaimVerification]:
        """
        Maps raw generated claims against retrieved evidence spans using semantic entailment evaluation.
        """
        verifications: list[ClaimVerification] = []

        for idx, claim_text in enumerate(claims_raw):
            claim_id = f"CLAIM_{idx+1:03d}_{uuid.uuid4().hex[:4]}"
            matched_span: Optional[EvidenceSpan] = None

            if not evidence_spans:
                verifications.append(
                    ClaimVerification(
                        claim_id=claim_id,
                        claim=claim_text,
                        evidence=None,
                        support_status=SupportStatus.INSUFFICIENT_EVIDENCE,
                        verification_notes="Abstained: Zero evidence spans returned from document library."
                    )
                )
                continue

            # Semantic entailment match against sanitized evidence spans
            status, matched_span, notes = ClaimVerificationEngine._evaluate_semantic_entailment(claim_text, evidence_spans)

            verifications.append(
                ClaimVerification(
                    claim_id=claim_id,
                    claim=claim_text,
                    evidence=matched_span if status in (SupportStatus.SUPPORTED, SupportStatus.PARTIALLY_SUPPORTED, SupportStatus.CONTRADICTED) else None,
                    support_status=status,
                    verification_notes=notes
                )
            )

        return verifications

    @staticmethod
    def _evaluate_semantic_entailment(claim: str, evidence_spans: list[EvidenceSpan]) -> tuple[SupportStatus, Optional[EvidenceSpan], str]:
        """
        Evaluates semantic entailment (SUPPORTED, PARTIALLY_SUPPORTED, CONTRADICTED, INSUFFICIENT_EVIDENCE).
        Applies SafetyGateway.sanitize_retrieved_span_for_prompt to all evidence spans.
        """
        claim_lower = claim.lower()
        model = get_sentence_model()
        
        best_span = None
        best_score = 0.0

        for span in evidence_spans:
            # Enforce pre-interpolation prompt sanitization
            sanitized_evidence = SafetyGateway.sanitize_retrieved_span_for_prompt(span.evidence_span)
            ev_lower = sanitized_evidence.lower()
            
            # Check for direct contradiction (numeric or clause conditions)
            c_days = re.search(r"\b(\d+)\s*days\b", claim_lower)
            e_days = re.search(r"\b(\d+)\s*days\b", ev_lower)
            if c_days and e_days and c_days.group(1) != e_days.group(1):
                return (
                    SupportStatus.CONTRADICTED,
                    span,
                    f"Contradiction detected: Claim asserts {c_days.group(1)} days, whereas {span.document_name} specifies {e_days.group(1)} days."
                )

            # Check dense vector entailment score if model is available
            if model is not None:
                try:
                    v_claim = model.encode(claim, convert_to_numpy=True)
                    v_ev = model.encode(sanitized_evidence, convert_to_numpy=True)
                    score = float(np.dot(v_claim, v_ev) / (np.linalg.norm(v_claim) * np.linalg.norm(v_ev)))
                except Exception:
                    score = ClaimVerificationEngine._heuristic_concept_overlap(claim_lower, ev_lower)
            else:
                score = ClaimVerificationEngine._heuristic_concept_overlap(claim_lower, ev_lower)

            if score > best_score:
                best_score = score
                best_span = span

        if best_span and best_score >= 0.35:
            return (
                SupportStatus.SUPPORTED,
                best_span,
                f"Entailment verified with {best_span.retrieval_confidence * 100:.1f}% retrieval confidence in {best_span.document_name} ({best_span.section})."
            )
        elif best_span and best_score >= 0.15:
            return (
                SupportStatus.PARTIALLY_SUPPORTED,
                best_span,
                f"Partial semantic entailment in {best_span.document_name}; additional conditions apply."
            )
        else:
            return (
                SupportStatus.INSUFFICIENT_EVIDENCE,
                None,
                "Claim cannot be substantiated from retrieved document evidence."
            )

    @staticmethod
    def _heuristic_concept_overlap(text1: str, text2: str) -> float:
        """
        Optional cheap pre-filter heuristic based on word set intersection (not full semantic entailment).
        """
        words1 = set(re.findall(r"\w+", text1.lower())) - {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "is", "are"}
        words2 = set(re.findall(r"\w+", text2.lower())) - {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "is", "are"}
        if not words1:
            return 0.0
        return len(words1.intersection(words2)) / len(words1)

