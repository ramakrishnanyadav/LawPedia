"""
Legal Extraction Engine: GenAI Grounded Obligations, Rights, Conditions, Penalties & Risks
"""

import re
from backend.schemas.eglr import ClauseObject, Obligation, RiskLevel
from backend.services.safety import SafetyGateway


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
    def extract_obligations(cls, clause: ClauseObject) -> list[Obligation]:
        """
        Extracts structured obligations, strictly anchored to exact text present within the clause.
        Applies pre-interpolation prompt sanitization and verbatim grounding validation.
        """
        obligations: list[Obligation] = []
        sanitized_text = SafetyGateway.sanitize_retrieved_span_for_prompt(clause.text)

        # Sentence-level grounded parsing
        sentences = re.split(r"(?<=[.!?])\s+", sanitized_text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue

            # Grounding validation check
            if not cls._is_grounded_in_clause(sent_clean, clause.text):
                continue

            if re.search(r"\b(shall|must|agrees to|is required to|covenants|undertakes to|shall maintain|shall keep)\b", sent_clean, re.IGNORECASE):
                party = "Party A"
                for p in clause.entities:
                    if p.lower() in sent_clean.lower():
                        party = p
                        break
                
                cond_match = re.search(r"\b(if|provided that|subject to|in the event of)\s+([^,.;]+)", sent_clean, re.IGNORECASE)
                cond_text = cond_match.group(0).strip() if cond_match else None

                deadline_match = re.search(r"\b(within \d+ (?:days?|months?|years?)|prior to [^,.;]+|no later than [^,.;]+)", sent_clean, re.IGNORECASE)
                deadline = deadline_match.group(0).strip() if deadline_match else None

                penalty_match = re.search(r"\b(penalty of [^,.;]+|cure period of [^,.;]+|late fee of [^,.;]+|interest at \d+%|liquidated damages of [^,.;]+)", sent_clean, re.IGNORECASE)
                penalty = penalty_match.group(0).strip() if penalty_match else None

                risk = RiskLevel.MEDIUM
                if "sole discretion" in sent_clean.lower() or "immediate termination" in sent_clean.lower() or "unlimited liability" in sent_clean.lower():
                    risk = RiskLevel.HIGH

                obligations.append(
                    Obligation(
                        party=party,
                        obligation_text=sent_clean,
                        clause_id=clause.clause_id,
                        conditional_on=cond_text,
                        deadline=deadline,
                        penalty=penalty,
                        risk_level=risk
                    )
                )

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
            if re.search(r"\b(may|entitled to|reserves the right to|has the right|shall be permitted to)\b", sent_clean, re.IGNORECASE):
                if cls._is_grounded_in_clause(sent_clean, clause.text):
                    rights.append(sent_clean)
        return rights

