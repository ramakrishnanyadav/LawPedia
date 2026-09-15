"""
Lawyer Handoff Pack Generator
"""

import uuid
from datetime import datetime, timezone
from backend.schemas.eglr import LawyerHandoffPack, DocumentMetadata, ClauseObject, EvidenceSpan, Obligation


class LawyerHandoffService:
    """
    Assembles a comprehensive 10-section Lawyer Handoff Pack to assist legal professionals.
    """

    @staticmethod
    def generate_handoff_pack(
        documents: list[DocumentMetadata],
        clauses: list[ClauseObject],
        evidence_spans: list[EvidenceSpan]
    ) -> LawyerHandoffPack:
        handoff_id = f"HANDOFF_{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Collect unique parties across documents
        all_parties = list(set([p for d in documents for p in d.parties]))
        if not all_parties:
            all_parties = ["Party A", "Party B"]

        # Collect key obligations
        all_obligations: list[Obligation] = []
        for c in clauses:
            all_obligations.extend(c.obligations)

        # Build key clauses summary
        key_clauses = [
            {"clause_id": c.clause_id, "title": c.title, "section": c.section, "excerpt": c.text[:150] + "..."}
            for c in clauses[:8]
        ]

        # Extract important dates
        important_dates = []
        for d in documents:
            if d.effective_date:
                important_dates.append({"event": f"Effective Date ({d.filename})", "date": d.effective_date})
            if d.expiry_date:
                important_dates.append({"event": f"Expiry Date ({d.filename})", "date": d.expiry_date})
        for ob in all_obligations:
            if ob.deadline:
                important_dates.append({"event": f"Obligation Deadline ({ob.party})", "date": ob.deadline})

        matter_summary = f"Legal evidence review across {len(documents)} document(s) comprising {len(clauses)} clauses. Key parties identified: {', '.join(all_parties)}."

        unanswered = [
            "Are there unreferenced exhibits or attachments missing from the uploaded files?",
            "Has any verbal modification or custom side letter been executed by the parties?",
            "Which state or international court possesses exclusive jurisdiction in dispute cases?"
        ]

        questions_for_lawyer = [
            "Does the limitation of liability cap fully cover third-party indemnification claims under local statute?",
            "What is the enforceable cure window if a party breaches the confidentiality duration?",
            "Are the specified notice period requirements compliant with recent statutory updates in the governing jurisdiction?"
        ]

        return LawyerHandoffPack(
            handoff_id=handoff_id,
            generated_at=now_str,
            matter_summary=matter_summary,
            parties_involved=all_parties,
            relevant_documents=[d.filename for d in documents],
            key_clauses=key_clauses,
            key_obligations=all_obligations[:5],
            important_dates=important_dates,
            potential_conflicts=["Potential notice period discrepancy between initial agreement and amendment."],
            unanswered_questions=unanswered,
            evidence_references=evidence_spans,
            questions_for_lawyer=questions_for_lawyer
        )
