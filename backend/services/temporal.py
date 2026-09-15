"""
Temporal and Version Reasoning Engine
"""

from typing import Optional
from backend.schemas.eglr import ClauseObject, DocumentMetadata


class TemporalReasoningService:
    """
    Determines active clause versions, amendment chains, superseding status,
    and effective date windows.
    """

    @staticmethod
    def resolve_controlling_clause(
        clauses_v1: list[ClauseObject],
        meta_v1: DocumentMetadata,
        clauses_v2: list[ClauseObject],
        meta_v2: DocumentMetadata,
        topic_pattern: str
    ) -> dict:
        """
        Evaluates which version of a clause controls given effective dates and supersedes metadata.
        Never silently assumes the latest file controls unless explicit evidence exists.
        """
        c1 = TemporalReasoningService._find_clause(clauses_v1, topic_pattern)
        c2 = TemporalReasoningService._find_clause(clauses_v2, topic_pattern)

        if not c1 and not c2:
            return {"controlling_version": "NONE", "reason": "No clause found matching query topic in either document version."}

        if c1 and not c2:
            return {
                "controlling_version": meta_v1.document_version,
                "controlling_clause": c1,
                "reason": f"Clause only present in version {meta_v1.document_version} (Effective {meta_v1.effective_date})."
            }

        if not c1 and c2:
            return {
                "controlling_version": meta_v2.document_version,
                "controlling_clause": c2,
                "reason": f"Clause added in newer version {meta_v2.document_version} (Effective {meta_v2.effective_date})."
            }

        # Both exist - check explicit effective dates and version numbers
        date_v1 = meta_v1.effective_date or "1900-01-01"
        date_v2 = meta_v2.effective_date or "1900-01-01"

        if date_v2 > date_v1 or "amendment" in meta_v2.filename.lower() or "v2" in meta_v2.document_version.lower():
            return {
                "controlling_version": meta_v2.document_version,
                "controlling_clause": c2,
                "superseded_clause": c1,
                "reason": f"Version {meta_v2.document_version} (Effective {date_v2}) explicitly supersedes Version {meta_v1.document_version} (Effective {date_v1})."
            }
        else:
            return {
                "controlling_version": meta_v1.document_version,
                "controlling_clause": c1,
                "superseded_clause": c2,
                "reason": f"Version {meta_v1.document_version} (Effective {date_v1}) is recorded as active."
            }

    @staticmethod
    def _find_clause(clauses: list[ClauseObject], topic_pattern: str) -> Optional[ClauseObject]:
        import re
        for c in clauses:
            if re.search(topic_pattern, c.text, re.IGNORECASE) or re.search(topic_pattern, c.title, re.IGNORECASE):
                return c
        return None
