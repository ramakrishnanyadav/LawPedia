export type SupportStatus = "SUPPORTED" | "PARTIALLY_SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT_EVIDENCE" | "OUT_OF_SCOPE";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface EvidenceSpan {
  source_document_id: string;
  document_name: string;
  page: number;
  section: string;
  clause_id: string;
  evidence_span: string;
  document_version: string;
  effective_date?: string;
  jurisdiction?: string;
  retrieval_confidence: number;
}

export interface ClaimVerification {
  claim_id: string;
  claim: string;
  evidence?: EvidenceSpan;
  support_status: SupportStatus;
  verification_notes?: string;
}

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  title: string;
  mime_type: string;
  page_count: number;
  clause_count: number;
  effective_date?: string;
  jurisdiction: string;
  parties: string[];
  document_version: string;
  tenant_id: string;
  upload_timestamp: string;
}

export interface ClauseObject {
  clause_id: string;
  document_id: string;
  section: string;
  title: string;
  text: string;
  page: number;
  risk_level: RiskLevel;
  entities: string[];
  rights: string[];
}

export interface FalsePremiseCheck {
  has_false_premise: boolean;
  detected_premise?: string;
  correction?: string;
  evidence?: EvidenceSpan;
}

export interface AskQueryResponse {
  query: string;
  plain_language_answer: string;
  claims: ClaimVerification[];
  support_status: SupportStatus;
  false_premise_check: FalsePremiseCheck;
  important_conditions: string[];
  conflicts_or_uncertainty: string[];
  practical_next_steps: string[];
  questions_to_ask_lawyer: string[];
  evidence_spans: EvidenceSpan[];
  legal_disclaimer: string;
}

export interface ComparisonItem {
  dimension: string;
  status: "UNCHANGED" | "MODIFIED" | "ADDED" | "REMOVED" | "CONFLICTING";
  doc_a_clause?: string;
  doc_b_clause?: string;
  doc_a_text?: string;
  doc_b_text?: string;
  analysis: string;
  risk_impact: RiskLevel;
}

export interface ComparisonResult {
  doc_a_id: string;
  doc_b_id: string;
  doc_a_name: string;
  doc_b_name: string;
  summary: string;
  items: ComparisonItem[];
}

export interface LawyerHandoffPack {
  handoff_id: string;
  generated_at: string;
  matter_summary: string;
  parties_involved: string[];
  relevant_documents: string[];
  key_clauses: { clause_id: string; title: string; section: string; excerpt: string }[];
  important_dates: { event: string; date: string }[];
  potential_conflicts: string[];
  unanswered_questions: string[];
  evidence_references: EvidenceSpan[];
  questions_for_lawyer: string[];
}
