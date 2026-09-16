"""
Legal Extraction Engine: GenAI Grounded Obligations, Rights, Conditions, Penalties & Risks
"""

import re
from typing import Optional
from backend.schemas.eglr import ClauseObject, Obligation, RiskLevel
from backend.services.safety import SafetyGateway

_RE_OBLIGATION_KEYWORD = re.compile(r"\b(shall|must|agrees to|is required to|covenants|undertakes to|shall maintain|shall keep)\b", re.IGNORECASE)
_RE_CONDITION = re.compile(r"\b(if|provided that|subject to|in the event of)\s+([^,.;]+)", re.IGNORECASE)
_RE_DEADLINES = [
    re.compile(r"\bwithin \d+ (?:days?|months?|years?)\b", re.IGNORECASE),
    re.compile(r"\bprior to [^,.;]+", re.IGNORECASE),
    re.compile(r"\bno later than [^,.;]+", re.IGNORECASE)
]
_RE_PENALTY = re.compile(r"\b(?:penalty|cure period|late fee|liquidated damages) of [^,.;]+|\binterest at \d+%", re.IGNORECASE)
_RE_RIGHTS_KEYWORD = re.compile(r"\b(may|entitled to|reserves the right to|has the right|shall be permitted to)\b", re.IGNORECASE)


class LegalExtractionService:
    """
    Extracts structured legal triples (Party, Obligation/Right, Condition, Deadline, Penalty)
    from clause text, strictly constrained to reference text appearing in the clause.
    """

    @staticmethod
    def _is_grounded_in_clause(extracted_text: str, clause_text: str) -> bool:
        """
        Validates that extracted text is a verbatim substring or high-overlap direct paraphrase of the clause.
        """
        if not extracted_text or not clause_text:
            return False
        
        # 1. Verbatim substring check
        clean_ext = extracted_text.strip().lower()
        clean_clause = clause_text.strip().lower()
        if clean_ext in clean_clause:
            return True
            
        # 2. High-overlap direct paraphrase check (word Jaccard similarity)
        ext_words = set(re.findall(r"\w+", clean_ext))
        clause_words = set(re.findall(r"\w+", clean_clause))
        if not ext_words or not clause_words:
            return False
        overlap = len(ext_words.intersection(clause_words)) / len(ext_words)
        return overlap >= 0.65

    @classmethod
    def _parse_sentence_obligation(cls, sent_clean: str, clause: ClauseObject) -> Optional[Obligation]:
        if not _RE_OBLIGATION_KEYWORD.search(sent_clean):
            return None

        party = "Party A"
        sent_lower = sent_clean.lower()
        for p in clause.entities:
            if p.lower() in sent_lower:
                party = p
                break

        cond_match = _RE_CONDITION.search(sent_clean)
        cond_text = cond_match.group(0).strip() if cond_match else None

        deadline = None
        for pat in _RE_DEADLINES:
            m = pat.search(sent_clean)
            if m:
                deadline = m.group(0).strip()
                break

        penalty_match = _RE_PENALTY.search(sent_clean)
        penalty = penalty_match.group(0).strip() if penalty_match else None

        risk = RiskLevel.HIGH if any(kw in sent_lower for kw in ("sole discretion", "immediate termination", "unlimited liability")) else RiskLevel.MEDIUM

        return Obligation(
            party=party,
            obligation_text=sent_clean,
            clause_id=clause.clause_id,
            conditional_on=cond_text,
            deadline=deadline,
            penalty=penalty,
            risk_level=risk
        )

    @classmethod
    def extract_obligations(cls, clause: ClauseObject) -> list[Obligation]:
        """
        Extracts structured obligations, strictly anchored to exact text present within the clause.
        Applies pre-interpolation prompt sanitization and verbatim grounding validation.
        """
        obligations: list[Obligation] = []
        sanitized_text = SafetyGateway.sanitize_retrieved_span_for_prompt(clause.text)
        sentences = re.split(r"(?<=[.!?])\s+", sanitized_text)

        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean or not cls._is_grounded_in_clause(sent_clean, clause.text):
                continue
            ob = cls._parse_sentence_obligation(sent_clean, clause)
            if ob:
                obligations.append(ob)

        return obligations

    @classmethod
    def extract_rights(cls, clause: ClauseObject) -> list[str]:
        """
        Extracts legal rights (may, entitled to, reserves the right to) with grounding validation.
        """
        rights: list[str] = []
        sanitized_text = SafetyGateway.sanitize_retrieved_span_for_prompt(clause.text)
        sentences = re.split(r"(?<=[.!?])\s+", sanitized_text)
        for sent in sentences:
            sent_clean = sent.strip()
            if _RE_RIGHTS_KEYWORD.search(sent_clean):
                if cls._is_grounded_in_clause(sent_clean, clause.text):
                    rights.append(sent_clean)
        return rights


