import re
from typing import Optional
from backend.schemas.eglr import EvidenceSpan, FalsePremiseCheck
from backend.services.safety import SafetyGateway

_RE_DAYS = re.compile(r"\b(\d+)\s*(?:days?|months?)\b", re.IGNORECASE)
_RE_CAP = re.compile(r"\$(\d+(?:,\d{3})*)")
_RE_PCT = re.compile(r"\b(\d+(?:\.\d+)?)\%")
_RE_STATE = re.compile(r"\b(california|delaware|new york|england|singapore|india|texas)\b", re.IGNORECASE)
_RE_NET = re.compile(r"\bnet\s*(\d+)\b", re.IGNORECASE)
_RE_AUDIT_FREQ = re.compile(r"\b(monthly|weekly|quarterly)\b", re.IGNORECASE)


def _check_days_contradiction(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    query_days_match = _RE_DAYS.search(query)
    if not query_days_match:
        return None
    assumed_days = int(query_days_match.group(1))
    for orig_span, sanitized_text in sanitized_spans:
        ev_days_match = _RE_DAYS.search(sanitized_text)
        if ev_days_match:
            actual_days = int(ev_days_match.group(1))
            if assumed_days != actual_days and abs(assumed_days - actual_days) > 1:
                return FalsePremiseCheck(
                    has_false_premise=True,
                    detected_premise=f"User query assumed a {assumed_days}-day timeframe.",
                    correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies a {actual_days}-day timeframe.",
                    evidence=orig_span
                )
    return None


def _check_cap_contradiction(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    query_cap_match = _RE_CAP.search(query)
    if not query_cap_match:
        return None
    assumed_cap = query_cap_match.group(1).replace(",", "")
    for orig_span, sanitized_text in sanitized_spans:
        ev_cap_match = _RE_CAP.search(sanitized_text)
        if ev_cap_match:
            actual_cap = ev_cap_match.group(1).replace(",", "")
            if assumed_cap != actual_cap:
                return FalsePremiseCheck(
                    has_false_premise=True,
                    detected_premise=f"User query assumed a financial amount of ${assumed_cap}.",
                    correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies ${actual_cap}.",
                    evidence=orig_span
                )
    return None


def _check_pct_contradiction(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    query_pct_match = _RE_PCT.search(query)
    if not query_pct_match:
        return None
    assumed_pct = query_pct_match.group(1)
    for orig_span, sanitized_text in sanitized_spans:
        ev_pct_match = _RE_PCT.search(sanitized_text)
        if ev_pct_match:
            actual_pct = ev_pct_match.group(1)
            if assumed_pct != actual_pct:
                return FalsePremiseCheck(
                    has_false_premise=True,
                    detected_premise=f"User query assumed an SLA requirement of {assumed_pct}%.",
                    correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} mandates a {actual_pct}% SLA requirement.",
                    evidence=orig_span
                )
    return None


def _check_state_contradiction(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    query_state_match = _RE_STATE.search(query)
    if not query_state_match:
        return None
    assumed_state = query_state_match.group(1).title()
    for orig_span, sanitized_text in sanitized_spans:
        ev_state_match = _RE_STATE.search(sanitized_text)
        if ev_state_match:
            actual_state = ev_state_match.group(1).title()
            if assumed_state != actual_state:
                return FalsePremiseCheck(
                    has_false_premise=True,
                    detected_premise=f"User query assumed governing law is {assumed_state}.",
                    correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies governing law is {actual_state}.",
                    evidence=orig_span
                )
    return None


def _check_net_contradiction(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    if "net " not in query.lower():
        return None
    query_net_match = _RE_NET.search(query)
    if not query_net_match:
        return None
    assumed_net = query_net_match.group(1)
    for orig_span, sanitized_text in sanitized_spans:
        ev_net_match = _RE_NET.search(sanitized_text)
        if ev_net_match and ev_net_match.group(1) != assumed_net:
            actual_net = ev_net_match.group(1)
            return FalsePremiseCheck(
                has_false_premise=True,
                detected_premise=f"User query assumed payment terms of Net {assumed_net}.",
                correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies payment terms of Net {actual_net}.",
                evidence=orig_span
            )
    return None


def _check_qualitative_contradictions(query: str, sanitized_spans: list[tuple[EvidenceSpan, str]]) -> Optional[FalsePremiseCheck]:
    q_lower = query.lower()
    for orig_span, sanitized_text in sanitized_spans:
        s_lower = sanitized_text.lower()
        if "audit" in q_lower and _RE_AUDIT_FREQ.search(q_lower) and "annual audit" in s_lower:
            return FalsePremiseCheck(
                has_false_premise=True,
                detected_premise="User query assumed frequent (monthly/weekly) audit rights.",
                correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} grants Annual audit rights.",
                evidence=orig_span
            )
        if ("litigation" in q_lower or "court" in q_lower) and "arbitration" in s_lower:
            return FalsePremiseCheck(
                has_false_premise=True,
                detected_premise="User query assumed disputes are resolved in litigation.",
                correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} mandates binding Arbitration.",
                evidence=orig_span
            )
        if "perpetual" in q_lower and "confidential" in q_lower and ("3 years" in s_lower or "years" in s_lower):
            return FalsePremiseCheck(
                has_false_premise=True,
                detected_premise="User query assumed perpetual confidentiality.",
                correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} limits confidentiality to 3 years.",
                evidence=orig_span
            )
    return None


class FalsePremiseDetector:
    """
    Deconstructs user questions to identify embedded premises, compares them
    against retrieved evidence spans, and highlights false assumptions with citations.
    """

    @staticmethod
    def inspect_query_premises(query: str, evidence_spans: list[EvidenceSpan]) -> FalsePremiseCheck:
        """
        Scans query for numeric, legal, or factual assumptions and checks if retrieved
        sanitized evidence directly contradicts the assumption.
        """
        if not query or not evidence_spans:
            return FalsePremiseCheck(has_false_premise=False)

        sanitized_spans = [
            (span, SafetyGateway.sanitize_retrieved_span_for_prompt(span.evidence_span))
            for span in evidence_spans
        ]

        checkers = [
            _check_days_contradiction,
            _check_cap_contradiction,
            _check_pct_contradiction,
            _check_state_contradiction,
            _check_net_contradiction,
            _check_qualitative_contradictions,
        ]

        for checker in checkers:
            res = checker(query, sanitized_spans)
            if res:
                return res

        return FalsePremiseCheck(has_false_premise=False)



