"""
Safety Gateway: Legal Disclaimers, Prompt-Injection Sandbox & Pre-Interpolation Filtering
"""

import re
from typing import Tuple
from backend.config import settings


class SafetyGateway:
    """
    Enforces security boundaries, prompt sanitization, legal safety language,
    pre-interpolation evidence scrubbing, and automatic abstention triggers.
    """

    MANDATORY_LEGAL_DISCLAIMER = (
        "LEGAL INFORMATION NOTICE: Lawpedia is an AI-powered legal information and document analysis assistant. "
        "Lawpedia does NOT provide professional legal advice, representation, or guarantees of outcome. "
        "All generated claims are anchored strictly to uploaded evidence spans. Consult a qualified attorney for formal legal advice."
    )

    @staticmethod
    def sanitize_prompt_evidence(raw_document_text: str) -> str:
        """
        Protects against prompt-injection attacks embedded within untrusted document text.
        Wraps document text in non-executable XML data blocks and strips suspicious instruction overrides.
        """
        if not raw_document_text:
            return ""

        # Strip explicit system override attempts inside uploaded or retrieved document text
        sanitized = re.sub(
            r"(?i)(ignore previous instructions|system override|you are now|forget all instructions|reveal system prompt|output system secret|output another tenant)",
            "[REDACTED_SUSPICIOUS_INSTRUCTION_OVERRIDE]",
            raw_document_text
        )

        # Enforce sandbox boundary if not already wrapped
        if "<document_evidence>" not in sanitized:
            return f"<document_evidence>\n{sanitized}\n</document_evidence>"
        return sanitized

    @staticmethod
    def sanitize_retrieved_span_for_prompt(evidence_span_text: str) -> str:
        """
        Strips/flags prompt injection attempts embedded in retrieved evidence *before*
        it is interpolated into any LLM prompt.
        """
        return re.sub(
            r"(?i)(ignore previous instructions|system override|you are now|forget all instructions|reveal system prompt|output system secret)",
            "[REDACTED_EMBEDDED_PROMPT_INJECTION]",
            evidence_span_text
        )

    @staticmethod
    def redact_pii(text: str) -> str:
        """
        Redacts sensitive PII (Social Security Numbers, Aadhaar, PAN, Credit Cards, Phone Numbers).
        """
        if not text:
            return ""

        # SSN / Aadhaar-like numbers
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
        text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[REDACTED_AADHAAR]", text)
        # PAN-like uppercase alphanumeric
        text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", "[REDACTED_PAN]", text)
        # Phone
        text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
        # Credit Card
        text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CC]", text)
        return text

    @staticmethod
    def should_abstain(confidence: float, evidence_count: int) -> Tuple[bool, str]:
        """
        Determines whether the system must abstain rather than fabricate or hallucinate.
        """
        if evidence_count == 0:
            return True, "ABSTAIN: No relevant legal document evidence found in user's library."

        if confidence < settings.MIN_CONFIDENCE_THRESHOLD:
            return True, f"ABSTAIN: Retrieval confidence ({confidence:.2f}) falls below required threshold ({settings.MIN_CONFIDENCE_THRESHOLD:.2f})."

        return False, ""
