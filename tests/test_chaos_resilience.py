"""
Chaos Engineering Failure Injection & Graceful Degradation Tests
"""

import pytest
from backend.services.safety import SafetyGateway
from backend.services.verification import ClaimVerificationEngine
from backend.schemas.eglr import SupportStatus


def test_chaos_zero_evidence_graceful_abstention():
    """
    Simulates a total storage/index failure where 0 evidence spans are returned.
    Asserts system degrades gracefully to INSUFFICIENT_EVIDENCE abstention.
    """
    should_abstain, reason = SafetyGateway.should_abstain(confidence=0.0, evidence_count=0)
    assert should_abstain is True
    assert "No relevant legal document evidence found" in reason

    # Check claim verification handling zero evidence
    claims = ClaimVerificationEngine.verify_claims(["Vendor liability is capped at $500,000."], [])
    assert len(claims) == 1
    assert claims[0].support_status == SupportStatus.INSUFFICIENT_EVIDENCE
    assert "Abstained" in claims[0].verification_notes


def test_chaos_low_confidence_retrieval():
    """
    Simulates noisy or low-confidence vector index responses (confidence below MIN_CONFIDENCE_THRESHOLD = 0.30).
    Asserts system triggers strict abstention rather than fabricating legal answers.
    """
    should_abstain, reason = SafetyGateway.should_abstain(confidence=0.20, evidence_count=3)
    assert should_abstain is True
    assert "falls below required threshold" in reason
