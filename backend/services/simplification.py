"""
Plain-Language Legal Simplification Engine (Grounded In Evidence Spans)
"""

import re
from backend.schemas.eglr import EvidenceSpan
from backend.services.safety import SafetyGateway


class LegalSimplificationService:
    """
    Transforms complex legalese into plain-language explanations strictly grounded
    in retrieved document evidence spans at target reading levels.
    """

    @staticmethod
    def simplify_clause(clause_text: str, reading_level: str = "simple") -> str:
        """
        Simplifies legal clause text into plain language using LLM API (OpenAI/Anthropic) when available,
        falling back to grounded legalese translation while preserving strict SafetyGateway sanitization.
        """
        sanitized = SafetyGateway.sanitize_prompt_evidence(clause_text)
        clean_text = re.sub(r"</?document_evidence>", "", sanitized).strip()

        # 1. Attempt OpenAI API completion if configured
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"You are a legal assistant. Simplify the provided clause at a {reading_level} reading level strictly using facts from the evidence provided."},
                        {"role": "user", "content": clean_text}
                    ],
                    max_tokens=250,
                    temperature=0.1
                )
                if response.choices and response.choices[0].message.content:
                    return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL): {response.choices[0].message.content.strip()}"
            except Exception as err:
                print("Notice: OpenAI API simplification fallback:", err)

        # 2. Attempt Anthropic API completion if configured
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=anthropic_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=250,
                    temperature=0.1,
                    system=f"You are a legal assistant. Simplify the provided clause at a {reading_level} reading level strictly using facts from the evidence provided.",
                    messages=[{"role": "user", "content": clean_text}]
                )
                if response.content and len(response.content) > 0:
                    return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL): {response.content[0].text.strip()}"
            except Exception as err:
                print("Notice: Anthropic API simplification fallback:", err)

        # 3. Grounded rule-based fallback
        if reading_level == "simple":
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

            return f"PLAIN SUMMARY ({reading_level.upper()} LEVEL): {simplified}"
        elif reading_level == "standard":
            return f"STANDARD SUMMARY: {clean_text}"
        else:
            return f"EXPERT ANALYSIS: {clean_text}"

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
