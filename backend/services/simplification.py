"""
Plain-Language Legal Simplification Engine (Grounded In Evidence Spans)
"""

import re
import logging
from typing import Optional
from backend.schemas.eglr import EvidenceSpan
from backend.services.safety import SafetyGateway


import time
import os
from backend.config import settings

_logger = logging.getLogger("lawpedia.simplification")

_TENANT_REQUEST_TIMESTAMPS: dict[str, list[float]] = {}
_CONSECUTIVE_LLM_ERRORS: int = 0
_CIRCUIT_BREAKER_UNTIL: float = 0.0


class LegalSimplificationService:
    """
    Transforms complex legalese into plain-language explanations strictly grounded
    in retrieved document evidence spans at target reading levels. Includes rate limiting
    and circuit breakers for LLM API cost protection.
    """

    @staticmethod
    def _is_rate_limited(tenant_id: str) -> bool:
        now = time.time()
        timestamps = _TENANT_REQUEST_TIMESTAMPS.get(tenant_id, [])
        # Keep only timestamps within last 60 seconds
        timestamps = [t for t in timestamps if now - t < 60.0]
        _TENANT_REQUEST_TIMESTAMPS[tenant_id] = timestamps
        if len(timestamps) >= settings.MAX_LLM_REQUESTS_PER_MINUTE_PER_TENANT:
            return True
        timestamps.append(now)
        return False

    @staticmethod
    def _is_circuit_breaker_open() -> bool:
        return time.time() < _CIRCUIT_BREAKER_UNTIL

    @staticmethod
    def _record_llm_success():
        global _CONSECUTIVE_LLM_ERRORS
        _CONSECUTIVE_LLM_ERRORS = 0

    @staticmethod
    def _record_llm_failure():
        global _CONSECUTIVE_LLM_ERRORS, _CIRCUIT_BREAKER_UNTIL
        _CONSECUTIVE_LLM_ERRORS += 1
        if _CONSECUTIVE_LLM_ERRORS >= 5:
            _CIRCUIT_BREAKER_UNTIL = time.time() + 60.0  # Open circuit breaker for 60 seconds

    @staticmethod
    def _try_openai_simplification(clean_text: str, reading_level: str) -> Optional[str]:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return None
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": f"You are a legal assistant. Simplify the provided clause at a {reading_level} reading level strictly using facts from the evidence provided."},
                    {"role": "user", "content": clean_text}
                ],
                max_tokens=250,
                temperature=0.1
            )
            if response.choices and response.choices[0].message.content:
                LegalSimplificationService._record_llm_success()
                return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL) [MODE: LLM_OPENAI]: {response.choices[0].message.content.strip()}"
        except Exception as err:
            LegalSimplificationService._record_llm_failure()
            _logger.warning("Notice: OpenAI API simplification fallback: %s", err)
        return None

    @staticmethod
    def _try_anthropic_simplification(clean_text: str, reading_level: str) -> Optional[str]:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model=settings.ANTHROPIC_MODEL_NAME,
                max_tokens=250,
                temperature=0.1,
                system=f"You are a legal assistant. Simplify the provided clause at a {reading_level} reading level strictly using facts from the evidence provided.",
                messages=[{"role": "user", "content": clean_text}]
            )
            if response.content and len(response.content) > 0:
                LegalSimplificationService._record_llm_success()
                return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL) [MODE: LLM_ANTHROPIC]: {response.content[0].text.strip()}"
        except Exception as err:
            LegalSimplificationService._record_llm_failure()
            _logger.warning("Notice: Anthropic API simplification fallback: %s", err)
        return None

    @staticmethod
    def simplify_clause(clause_text: str, reading_level: str = "simple", tenant_id: str = "tenant_default", section_title: str = "") -> str:
        """
        Simplifies legal clause text into plain language using LLM API (OpenAI/Anthropic) when available,
        falling back to grounded legalese translation while preserving strict SafetyGateway sanitization.
        Includes per-tenant rate limiting and circuit breakers.
        """
        sanitized = SafetyGateway.sanitize_prompt_evidence(clause_text)
        clean_text = re.sub(r"</?document_evidence>", "", sanitized).strip()

        if not LegalSimplificationService._is_rate_limited(tenant_id) and not LegalSimplificationService._is_circuit_breaker_open():
            res_oa = LegalSimplificationService._try_openai_simplification(clean_text, reading_level)
            if res_oa:
                return res_oa

            res_ant = LegalSimplificationService._try_anthropic_simplification(clean_text, reading_level)
            if res_ant:
                return res_ant

        # 3. Enhanced Clause-Aware Rule-Based Fallback (fallback_no_llm_configured)
        simplified = clean_text
        replacements = {
            r"\bshall\b": "must",
            r"\bherein\b": "in this document",
            r"\bthereof\b": "of it",
            r"\bhereto\b": "to this",
            r"\bnotwithstanding\b": "despite",
            r"\bindemnify and hold harmless\b": "protect from legal financial loss",
            r"\bterminate for convenience\b": "cancel at any time without special reason",
            r"\bliquidated damages\b": "agreed pre-set penalty amount",
            r"\bforce majeure\b": "unforeseeable major emergency event"
        }
        for pattern, rep in replacements.items():
            simplified = re.sub(pattern, rep, simplified, flags=re.IGNORECASE)

        clause_prefix = ""
        st_lower = section_title.lower()
        if "termination" in st_lower or "cancel" in st_lower:
            clause_prefix = "[Termination Provision] "
        elif "liability" in st_lower or "limit" in st_lower:
            clause_prefix = "[Liability Limit Provision] "
        elif "indemn" in st_lower:
            clause_prefix = "[Indemnity Provision] "

        if reading_level == "simple":
            return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL) [MODE: FALLBACK_RULE_BASED]: {clause_prefix}{simplified}"
        elif reading_level == "standard":
            return f"STANDARD SUMMARY [MODE: FALLBACK_RULE_BASED]: {clause_prefix}{clean_text}"
        else:
            return f"EXPERT ANALYSIS [MODE: FALLBACK_RULE_BASED]: {clause_prefix}{clean_text}"

    @staticmethod
    def simplify_evidence_spans(spans: list[EvidenceSpan], reading_level: str = "simple") -> str:
        """
        Generates a consolidated plain-language summary from retrieved evidence spans.
        """
        if not spans:
            return "No evidence spans available for plain-language simplification."

        simplified_blocks = []
        for span in spans:
            sanitized_span = SafetyGateway.sanitize_retrieved_span_for_prompt(span.evidence_span)
            simplified = LegalSimplificationService.simplify_clause(sanitized_span, reading_level)
            simplified_blocks.append(f"• Document '{span.document_name}' ({span.section}): {simplified}")

        return "\n".join(simplified_blocks)
