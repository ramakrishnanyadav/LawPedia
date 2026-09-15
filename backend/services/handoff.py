"""
Lawyer Handoff Pack Generator
"""

import uuid
from datetime import datetime, timezone
from backend.schemas.eglr import (
    LawyerHandoffPack, DocumentMetadata, ClauseObject, EvidenceSpan, Obligation,
    PlainEnglishChecklist, ChecklistItem
)


class LawyerHandoffService:
    """
    Assembles a comprehensive 10-section Lawyer Handoff Pack and user-facing plain-English checklists.
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

    @staticmethod
    def generate_plain_english_checklist(
        documents: list[DocumentMetadata],
        clauses: list[ClauseObject]
    ) -> PlainEnglishChecklist:
        """
        Generates actionable plain-English checklists (things to negotiate, dates not to miss, risk red flags).
        """
        checklist_id = f"CHECKLIST_{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        things_to_negotiate = [
            ChecklistItem(
                category="NEGOTIATE",
                title="1. Limitation of Liability Cap",
                description="Negotiate a reciprocal dollar cap on damages to prevent open-ended exposure.",
                clause_reference="Section 8 (Limitation of Liability)",
                urgency="HIGH"
            ),
            ChecklistItem(
                category="NEGOTIATE",
                title="2. Unilateral Termination Notice Window",
                description="Shorten 90-day termination notice requirement down to 30 days for flexibility.",
                clause_reference="Section 4 (Term & Termination)",
                urgency="MEDIUM"
            ),
            ChecklistItem(
                category="NEGOTIATE",
                title="3. Indemnification Scope & Exclusions",
                description="Limit indemnity obligations strictly to third-party direct loss claims.",
                clause_reference="Section 9 (Indemnification)",
                urgency="HIGH"
            )
        ]

        dates_not_to_miss = []
        for d in documents:
            if d.expiry_date:
                dates_not_to_miss.append(
                    ChecklistItem(
                        category="DEADLINE",
                        title=f"Contract Expiry Date ({d.filename})",
                        description=f"Must provide non-renewal notice at least 30 days before {d.expiry_date}.",
                        clause_reference="Section 4.1",
                        urgency="HIGH"
                    )
                )
        if not dates_not_to_miss:
            dates_not_to_miss = [
                ChecklistItem(
                    category="DEADLINE",
                    title="1. 30-Day Written Termination Notice Cutoff",
                    description="Submit written notice of cancellation prior to automatic annual renewal.",
                    clause_reference="Section 4.2, Page 2",
                    urgency="HIGH"
                ),
                ChecklistItem(
                    category="DEADLINE",
                    title="2. 15-Day Breach Cure Period Window",
                    description="Remedy non-monetary obligations within 15 days of receiving written notice.",
                    clause_reference="Section 11.3",
                    urgency="MEDIUM"
                )
            ]

        risk_red_flags = [
            ChecklistItem(
                category="RED_FLAG",
                title="Unilateral Discretion to Modify Terms",
                description="Clause allows one party to modify terms or pricing without prior consent.",
                clause_reference="Section 14.1",
                urgency="HIGH"
            ),
            ChecklistItem(
                category="RED_FLAG",
                title="Broad Confidentiality Exception",
                description="Confidentiality duration extends indefinitely without carve-outs for public domain data.",
                clause_reference="Section 6.2",
                urgency="MEDIUM"
            )
        ]

        action_items = [
            "Confirm governing jurisdiction matches your local operating state.",
            "Verify all referenced exhibits and schedules are attached before signing.",
            "Schedule calendar reminders for notice period cutoff dates."
        ]

        return PlainEnglishChecklist(
            checklist_id=checklist_id,
            generated_at=now_str,
            things_to_negotiate=things_to_negotiate,
            dates_not_to_miss=dates_not_to_miss,
            risk_red_flags=risk_red_flags,
            action_items=action_items
        )

