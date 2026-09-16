"""
Lawyer Handoff Pack Generator
"""

import uuid
from datetime import datetime, timezone
from backend.schemas.eglr import (
    LawyerHandoffPack, DocumentMetadata, ClauseObject, EvidenceSpan, Obligation,
    PlainEnglishChecklist, ChecklistItem, RiskLevel
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
        all_parties = list({p for d in documents for p in d.parties})
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
        Generates actionable plain-English checklists grounded strictly in clauses and
        metadata from the actual uploaded documents. Every item traces back to a real
        clause or date in the document — no hardcoded fabricated citations.
        """
        checklist_id = f"CHECKLIST_{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        things_to_negotiate: list[ChecklistItem] = []
        risk_red_flags: list[ChecklistItem] = []
        dates_not_to_miss: list[ChecklistItem] = []

        for c in clauses:
            # Negotiation items: HIGH or CRITICAL risk clauses with obligations
            if c.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL) and c.obligations:
                obligation_text = c.obligations[0].obligation_text[:120]
                things_to_negotiate.append(
                    ChecklistItem(
                        category="NEGOTIATE",
                        title=f"Risk clause: {c.title[:80]}",
                        description=obligation_text,
                        clause_reference=f"{c.section}, page {c.page}",
                        urgency="HIGH" if c.risk_level == RiskLevel.CRITICAL else "MEDIUM"
                    )
                )

            # Red flags: CRITICAL risk clauses regardless of obligations
            if c.risk_level == RiskLevel.CRITICAL:
                risk_red_flags.append(
                    ChecklistItem(
                        category="RED_FLAG",
                        title=f"Critical clause: {c.title[:80]}",
                        description=c.text[:150],
                        clause_reference=f"{c.section}, page {c.page}",
                        urgency="HIGH"
                    )
                )
            # Medium-risk red flags also surfaced (with MEDIUM urgency)
            elif c.risk_level == RiskLevel.HIGH and not c.obligations:
                risk_red_flags.append(
                    ChecklistItem(
                        category="RED_FLAG",
                        title=f"High-risk clause: {c.title[:80]}",
                        description=c.text[:150],
                        clause_reference=f"{c.section}, page {c.page}",
                        urgency="MEDIUM"
                    )
                )

        # Key dates from document metadata
        for d in documents:
            if d.expiry_date:
                dates_not_to_miss.append(
                    ChecklistItem(
                        category="DEADLINE",
                        title=f"Contract Expiry — {d.filename}",
                        description=f"Contract expires {d.expiry_date}. Ensure non-renewal or renewal notice is submitted well in advance.",
                        clause_reference=f"Document metadata ({d.filename})",
                        urgency="HIGH"
                    )
                )
            if d.effective_date:
                dates_not_to_miss.append(
                    ChecklistItem(
                        category="DEADLINE",
                        title=f"Effective Date — {d.filename}",
                        description=f"Agreement becomes effective {d.effective_date}.",
                        clause_reference=f"Document metadata ({d.filename})",
                        urgency="MEDIUM"
                    )
                )

        # Obligation deadlines from clauses
        for c in clauses:
            for ob in c.obligations:
                if ob.deadline:
                    dates_not_to_miss.append(
                        ChecklistItem(
                            category="DEADLINE",
                            title=f"Obligation deadline ({ob.party})",
                            description=f"{ob.obligation_text[:120]}",
                            clause_reference=f"{c.section}, page {c.page}",
                            urgency="HIGH"
                        )
                    )

        # Honest empty-state messages — never backfill with fabricated content
        if not things_to_negotiate:
            things_to_negotiate = [ChecklistItem(
                category="NEGOTIATE",
                title="No high-risk clauses flagged",
                description="No HIGH or CRITICAL risk clauses with obligations were detected in this document.",
                urgency="LOW"
            )]
        if not risk_red_flags:
            risk_red_flags = [ChecklistItem(
                category="RED_FLAG",
                title="No critical risk clauses detected",
                description="No CRITICAL or unobligated HIGH risk clauses were found in this document.",
                urgency="LOW"
            )]
        if not dates_not_to_miss:
            dates_not_to_miss = [ChecklistItem(
                category="DEADLINE",
                title="No key dates extracted",
                description="No expiry dates, effective dates, or obligation deadlines were found in this document.",
                urgency="LOW"
            )]

        action_items = [
            "Confirm governing jurisdiction matches your local operating state.",
            "Verify all referenced exhibits and schedules are attached before signing.",
            "Schedule calendar reminders for all deadline dates listed above."
        ]

        return PlainEnglishChecklist(
            checklist_id=checklist_id,
            generated_at=now_str,
            things_to_negotiate=things_to_negotiate,
            dates_not_to_miss=dates_not_to_miss,
            risk_red_flags=risk_red_flags,
            action_items=action_items
        )

