"""
Semantic Contract & Policy Comparison Engine
"""

import re
from typing import Optional
from backend.schemas.eglr import ClauseObject, DocumentMetadata, ComparisonResult, ComparisonItem, RiskLevel


class ComparisonService:
    """
    Compares two contracts semantically across key legal dimensions,
    highlighting additions, modifications, risk shifts, and conflicts.
    """

    DIMENSIONS = [
        (name, [re.compile(p, re.IGNORECASE) for p in patterns])
        for name, patterns in [
            ("Termination Notice", [r"\btermination\b", r"\bnotice period\b", r"\bcure period\b"]),
            ("Liability Cap", [r"\bliability\b", r"\blimitation of liability\b", r"\bcap\b"]),
            ("Payment & Fee Terms", [r"\bpayment\b", r"\binvoice\b", r"\bfees?\b", r"\bdue date\b"]),
            ("Confidentiality Duration", [r"\bconfidential\b", r"\bnon-disclosure\b", r"\bsecrecy\b"]),
            ("Governing Law & Forum", [r"\bgoverning law\b", r"\bjurisdiction\b", r"\bforum\b", r"\barbitration\b"]),
            ("Indemnification Obligations", [r"\bindemnif\w*\b", r"\bhold harmless\b"]),
            ("Intellectual Property Rights", [r"\bintellectual property\b", r"\bip rights\b", r"\bownership\b", r"\bpatent\b"]),
            ("Dispute Resolution", [r"\bdispute\b", r"\bmediation\b", r"\barbitration\b"]),
            ("Renewal & Extension", [r"\brenew\w*\b", r"\bextension\b", r"\bauto-renew\b"]),
            ("Subcontracting & Assignment", [r"\bassignment\b", r"\bsubcontract\w*\b", r"\btransfer\b"])
        ]
    ]

    @staticmethod
    def _analyze_dimension(
        dim_name: str,
        c_a: Optional[ClauseObject],
        c_b: Optional[ClauseObject],
        meta_a: DocumentMetadata,
        meta_b: DocumentMetadata
    ) -> tuple[str, str, RiskLevel, Optional[str]]:
        if c_a and not c_b:
            status = "REMOVED"
            analysis = f"Provision '{dim_name}' present in {meta_a.filename} was omitted in {meta_b.filename}."
            risk = RiskLevel.MEDIUM
            delta = f"[- {meta_a.filename}: {c_a.text} -]"
            return status, analysis, risk, delta

        if not c_a and c_b:
            status = "ADDED"
            analysis = f"New provision '{dim_name}' added in {meta_b.filename}."
            risk = RiskLevel.LOW
            delta = f"{{+ {meta_b.filename}: {c_b.text} +}}"
            return status, analysis, risk, delta

        text_a_clean = re.sub(r"\s+", " ", c_a.text.strip())
        text_b_clean = re.sub(r"\s+", " ", c_b.text.strip())

        if text_a_clean.lower() == text_b_clean.lower():
            status = "UNCHANGED"
            analysis = f"'{dim_name}' provisions are identical across both document versions."
            risk = RiskLevel.LOW
            delta = f"Identical text: '{c_a.text}'"
            return status, analysis, risk, delta

        status = "MODIFIED"
        risk = RiskLevel.MEDIUM
        if "unlimited" in text_b_clean.lower() and "limited" in text_a_clean.lower():
            status = "CONFLICTING"
            risk = RiskLevel.HIGH
            analysis = f"CRITICAL RISK SHIFT: {dim_name} changed from limited liability to unlimited liability in {meta_b.filename}."
        elif "sole discretion" in text_b_clean.lower() and "mutual" in text_a_clean.lower():
            status = "MODIFIED"
            risk = RiskLevel.HIGH
            analysis = f"RISK SHIFT: Option changed from mutual consent to sole discretion in {meta_b.filename}."
        else:
            analysis = f"'{dim_name}' language modified between versions."

        delta = f"[- {meta_a.filename}: {c_a.text} -]\n\n{{+ {meta_b.filename}: {c_b.text} +}}"
        return status, analysis, risk, delta

    @staticmethod
    def compare_documents(
        meta_a: DocumentMetadata,
        clauses_a: list[ClauseObject],
        meta_b: DocumentMetadata,
        clauses_b: list[ClauseObject]
    ) -> ComparisonResult:
        """
        Executes multi-dimensional semantic comparison between Document A and Document B.
        """
        items: list[ComparisonItem] = []

        for dim_name, patterns in ComparisonService.DIMENSIONS:
            c_a = ComparisonService._find_matching_clause(patterns, clauses_a)
            c_b = ComparisonService._find_matching_clause(patterns, clauses_b)

            if not c_a and not c_b:
                continue

            status, analysis, risk, delta = ComparisonService._analyze_dimension(dim_name, c_a, c_b, meta_a, meta_b)

            items.append(
                ComparisonItem(
                    dimension=dim_name,
                    status=status,
                    doc_a_clause=c_a.clause_id if c_a else None,
                    doc_b_clause=c_b.clause_id if c_b else None,
                    doc_a_text=c_a.text if c_a else None,
                    doc_b_text=c_b.text if c_b else None,
                    side_by_side_delta=delta,
                    analysis=analysis,
                    risk_impact=risk
                )
            )

        summary = f"Compared '{meta_a.filename}' ({meta_a.document_version}) with '{meta_b.filename}' ({meta_b.document_version}). Found {len(items)} key comparative dimensions."

        return ComparisonResult(
            doc_a_id=meta_a.document_id,
            doc_b_id=meta_b.document_id,
            doc_a_name=meta_a.filename,
            doc_b_name=meta_b.filename,
            summary=summary,
            items=items
        )

    @staticmethod
    def _find_matching_clause(patterns: list[re.Pattern], clauses: list[ClauseObject]) -> Optional[ClauseObject]:
        for c in clauses:
            for pat in patterns:
                if pat.search(c.text) or pat.search(c.title):
                    return c
        return None
