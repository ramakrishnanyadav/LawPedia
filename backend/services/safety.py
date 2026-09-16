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

    PROMPT_INJECTION_PATTERN = re.compile(
        r"(?i)(ignore previous instructions|system override|you are now|forget all instructions|reveal system prompt|output system secret|output another tenant|ignora las instrucciones|neue anweisung|override rules|disregard above|new system prompt|print system prompt|base64 decode instruction)"
    )

    @staticmethod
    def sanitize_prompt_evidence(raw_document_text: str) -> str:
        """
        Protects against prompt-injection attacks embedded within untrusted document text.
        Strips instruction override payloads, neutralizes XML tag escape attempts,
        and wraps content in non-executable structural evidence blocks.
        """
        if not raw_document_text:
            return ""

        # Neutralize XML tag injection attempts inside document text
        sanitized = raw_document_text.replace("</document_evidence>", "&lt;/document_evidence&gt;")
        sanitized = sanitized.replace("<document_evidence>", "&lt;document_evidence&gt;")

        # Second-pass regex filter for multilingual and structural instruction override attempts
        sanitized = SafetyGateway.PROMPT_INJECTION_PATTERN.sub("[REDACTED_SUSPICIOUS_INSTRUCTION_OVERRIDE]", sanitized)

        # Enforce sandbox data boundary
        return f"<document_evidence>\n{sanitized}\n</document_evidence>"

    @staticmethod
    def sanitize_retrieved_span_for_prompt(evidence_span_text: str) -> str:
        """
        Strips/flags prompt injection attempts embedded in retrieved evidence *before*
        it is interpolated into any LLM prompt.
        """
        if not evidence_span_text:
            return ""
        
        # Neutralize XML tag escaping
        clean_text = evidence_span_text.replace("</document_evidence>", "&lt;/document_evidence&gt;")
        clean_text = clean_text.replace("<document_evidence>", "&lt;document_evidence&gt;")

        return SafetyGateway.PROMPT_INJECTION_PATTERN.sub("[REDACTED_EMBEDDED_PROMPT_INJECTION]", clean_text)

    # Named PII patterns: each tuple is (compiled_regex, replacement_label).
    # Adding a new PII type is a one-line change here instead of a buried re.sub call.
    _PII_PATTERNS: list[tuple[re.Pattern, str]] = [
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
        (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[REDACTED_AADHAAR]"),
        (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[REDACTED_PAN]"),
        (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[REDACTED_PHONE]"),
        (re.compile(r"\b(?:\d[\s-]*){13,16}\b"), "[REDACTED_CC]"),
    ]

    @staticmethod
    def redact_pii(text: str) -> str:
        """
        Redacts sensitive PII (Social Security Numbers, Aadhaar, PAN, Credit Cards, Phone Numbers).
        Pattern list is defined in _PII_PATTERNS for auditability and extensibility.
        """
        if not text:
            return ""
        for pattern, label in SafetyGateway._PII_PATTERNS:
            text = pattern.sub(label, text)
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
