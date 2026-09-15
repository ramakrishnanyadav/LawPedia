import re
from typing import Optional
from backend.schemas.eglr import EvidenceSpan, FalsePremiseCheck
from backend.services.safety import SafetyGateway
from backend.services.retrieval import get_sentence_model


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

        # Apply SafetyGateway sanitization on all evidence spans before inspection
        sanitized_spans = []
        for span in evidence_spans:
            sanitized_text = SafetyGateway.sanitize_retrieved_span_for_prompt(span.evidence_span)
            sanitized_spans.append((span, sanitized_text))

        # 1. Days & Notice/Cure Period Contradictions
        query_days_match = re.search(r"\b(\d+)\s*(?:days?|months?)\b", query, re.IGNORECASE)
        if query_days_match:
            assumed_days = int(query_days_match.group(1))
            for orig_span, sanitized_text in sanitized_spans:
                ev_days_match = re.search(r"\b(\d+)\s*(?:days?|months?)\b", sanitized_text, re.IGNORECASE)
                if ev_days_match:
                    actual_days = int(ev_days_match.group(1))
                    if assumed_days != actual_days and abs(assumed_days - actual_days) > 1:
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise=f"User query assumed a {assumed_days}-day timeframe.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies a {actual_days}-day timeframe.",
                            evidence=orig_span
                        )

        # 2. Monetary Cap Contradictions
        query_cap_match = re.search(r"\$(\d+(?:,\d{3})*)", query)
        if query_cap_match:
            assumed_cap = query_cap_match.group(1).replace(",", "")
            for orig_span, sanitized_text in sanitized_spans:
                ev_cap_match = re.search(r"\$(\d+(?:,\d{3})*)", sanitized_text)
                if ev_cap_match:
                    actual_cap = ev_cap_match.group(1).replace(",", "")
                    if assumed_cap != actual_cap:
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise=f"User query assumed a financial amount of ${assumed_cap}.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies ${actual_cap}.",
                            evidence=orig_span
                        )

        # 3. Uptime Percentage SLA Contradictions (e.g. 95% vs 99.9%)
        query_pct_match = re.search(r"(\d+(?:\.\d+)?)%", query)
        if query_pct_match:
            assumed_pct = query_pct_match.group(1)
            for orig_span, sanitized_text in sanitized_spans:
                ev_pct_match = re.search(r"(\d+(?:\.\d+)?)%", sanitized_text)
                if ev_pct_match:
                    actual_pct = ev_pct_match.group(1)
                    if assumed_pct != actual_pct:
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise=f"User query assumed an SLA requirement of {assumed_pct}%.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} mandates a {actual_pct}% SLA requirement.",
                            evidence=orig_span
                        )

        # 4. State Law Jurisdiction Contradictions (e.g. Texas vs California)
        query_state_match = re.search(r"\b(california|delaware|new york|england|singapore|india|texas)\b", query, re.IGNORECASE)
        if query_state_match:
            assumed_state = query_state_match.group(1).title()
            for orig_span, sanitized_text in sanitized_spans:
                ev_state_match = re.search(r"\b(california|delaware|new york|england|singapore|india|texas)\b", sanitized_text, re.IGNORECASE)
                if ev_state_match:
                    actual_state = ev_state_match.group(1).title()
                    if assumed_state != actual_state:
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise=f"User query assumed governing law is {assumed_state}.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies governing law is {actual_state}.",
                            evidence=orig_span
                        )

        # 5. Payment Terms Net Contradiction (e.g. Net 90 vs Net 30)
        if "net " in query.lower():
            query_net_match = re.search(r"\bnet\s*(\d+)\b", query, re.IGNORECASE)
            if query_net_match:
                assumed_net = query_net_match.group(1)
                for orig_span, sanitized_text in sanitized_spans:
                    ev_net_match = re.search(r"\bnet\s*(\d+)\b", sanitized_text, re.IGNORECASE)
                    if ev_net_match and ev_net_match.group(1) != assumed_net:
                        actual_net = ev_net_match.group(1)
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise=f"User query assumed payment terms of Net {assumed_net}.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} specifies payment terms of Net {actual_net}.",
                            evidence=orig_span
                        )

        # 6. Audit Frequency Contradiction (e.g. monthly vs Annual audit)
        if "audit" in query.lower():
            if re.search(r"\b(monthly|weekly|quarterly)\b", query, re.IGNORECASE):
                for orig_span, sanitized_text in sanitized_spans:
                    if "annual audit" in sanitized_text.lower():
                        return FalsePremiseCheck(
                            has_false_premise=True,
                            detected_premise="User query assumed frequent (monthly/weekly) audit rights.",
                            correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} grants Annual audit rights.",
                            evidence=orig_span
                        )

        # 7. Dispute Resolution Contradiction (e.g. litigation vs Arbitration)
        if "litigation" in query.lower() or "court" in query.lower():
            for orig_span, sanitized_text in sanitized_spans:
                if "arbitration" in sanitized_text.lower():
                    return FalsePremiseCheck(
                        has_false_premise=True,
                        detected_premise="User query assumed disputes are resolved in litigation.",
                        correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} mandates binding Arbitration.",
                        evidence=orig_span
                    )

        # 8. Confidentiality Duration Contradiction (e.g. perpetual vs 3 years)
        if "perpetual" in query.lower() and "confidential" in query.lower():
            for orig_span, sanitized_text in sanitized_spans:
                if "3 years" in sanitized_text.lower() or "years" in sanitized_text.lower():
                    return FalsePremiseCheck(
                        has_false_premise=True,
                        detected_premise="User query assumed perpetual confidentiality.",
                        correction=f"INCORRECT PREMISE: Section '{orig_span.section}' of {orig_span.document_name} limits confidentiality to 3 years.",
                        evidence=orig_span
                    )

        return FalsePremiseCheck(has_false_premise=False)



