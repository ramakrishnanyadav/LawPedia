import React, { useState } from 'react';
import { AskQueryResponse, EvidenceSpan, SupportStatus } from '../types';
import { Search, ShieldAlert, CheckCircle2, AlertTriangle, HelpCircle, FileText, ChevronRight, CornerDownRight, Lightbulb } from 'lucide-react';

interface AskWorkspaceProps {
  onRunQuery: (query: string) => Promise<AskQueryResponse>;
}

export const AskWorkspace: React.FC<AskWorkspaceProps> = ({ onRunQuery }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AskQueryResponse | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<EvidenceSpan | null>(null);

  const sampleQueries = [
    "What is the termination notice period?",
    "Does the contract give me 30 days notice in v1.0?",
    "What are the liability caps across versions?",
    "What patent infringement penalties apply in Japan?"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await onRunQuery(query);
      setResponse(res);
      if (res.evidence_spans && res.evidence_spans.length > 0) {
        setSelectedSpan(res.evidence_spans[0]);
      } else {
        setSelectedSpan(null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const renderStatusBadge = (status: SupportStatus) => {
    switch (status) {
      case 'SUPPORTED':
        return (
          <span className="badge-supported px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <CheckCircle2 className="w-3.5 h-3.5" /> SUPPORTED BY EVIDENCE
          </span>
        );
      case 'PARTIALLY_SUPPORTED':
        return (
          <span className="badge-partially px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <AlertTriangle className="w-3.5 h-3.5" /> PARTIALLY SUPPORTED
          </span>
        );
      case 'CONTRADICTED':
        return (
          <span className="badge-contradicted px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <AlertTriangle className="w-3.5 h-3.5" /> CONTRADICTION DETECTED
          </span>
        );
      default:
        return (
          <span className="badge-insufficient px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <HelpCircle className="w-3.5 h-3.5" /> EXPLICIT ABSTENTION
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Input Box */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Search className="w-5 h-5 text-blue-600" /> Ask Workspace — Evidence-Grounded Legal Interrogation
        </h2>
        <p className="text-xs text-slate-500">
          Enter any legal question. Responses are decomposed into claims verified against uploaded source documents.
        </p>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. What is the notice period for contract termination?"
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3.5 pl-11 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-600 focus:bg-white focus:ring-2 focus:ring-blue-100 transition-all font-sans"
              aria-label="Legal Question Query Input"
            />
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-3.5" />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-xs font-bold transition-all shadow-md shadow-blue-600/20 disabled:opacity-50"
            >
              {loading ? 'Evaluating Evidence...' : 'Interrogate'}
            </button>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
              <Lightbulb className="w-3.5 h-3.5 text-amber-500" /> Sample Queries:
            </span>
            {sampleQueries.map((sq, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setQuery(sq)}
                className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors font-medium"
              >
                {sq}
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Response Results Section */}
      {response && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Answer Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Status Header */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4 border-l-4 border-l-blue-600">
              <div>
                <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block mb-1">Retrieval Grounding Status</span>
                <div className="flex items-center gap-3">
                  {renderStatusBadge(response.support_status)}
                </div>
              </div>
            </div>

            {/* False Premise Alert */}
            {response.false_premise_check?.has_false_premise && (
              <div className="bg-amber-50 border border-amber-300 rounded-2xl p-5 text-amber-950 space-y-1 shadow-sm">
                <div className="flex items-center gap-2 font-bold text-xs text-amber-800 uppercase tracking-wide">
                  <AlertTriangle className="w-4 h-4 text-amber-600" /> False Premise Detected & Corrected
                </div>
                <p className="text-sm font-medium">{response.false_premise_check.correction}</p>
              </div>
            )}

            {/* Plain Language Answer */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-600" /> Plain-Language Synthesis
              </h3>
              <p className="text-sm leading-relaxed text-slate-800 bg-slate-50 p-4 rounded-xl border border-slate-200/80 font-normal">
                {response.plain_language_answer}
              </p>
            </div>

            {/* Claim-Level Evidence Verification */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Claim-Level Verification Matrix
              </h3>
              <div className="space-y-3">
                {response.claims.map((c) => (
                  <button
                    type="button"
                    key={c.claim_id}
                    onClick={() => c.evidence && setSelectedSpan(c.evidence)}
                    className={`w-full text-left p-4 rounded-xl border transition-all cursor-pointer ${
                      selectedSpan?.clause_id === c.evidence?.clause_id
                        ? 'bg-blue-50/80 border-blue-500 shadow-sm'
                        : 'bg-slate-50/50 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <span className="text-[11px] font-mono text-slate-400">{c.claim_id}</span>
                        <p className="text-sm font-semibold text-slate-900">{c.claim}</p>
                        <p className="text-xs text-slate-600 italic">{c.verification_notes}</p>
                      </div>
                      <div>
                        {renderStatusBadge(c.support_status)}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Practical Next Steps */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Practical Next Steps</h3>
              <ul className="space-y-2">
                {response.practical_next_steps.map((step) => (
                  <li key={step} className="text-xs text-slate-700 flex items-start gap-2 font-medium">
                    <ChevronRight className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Safety Disclaimer */}
            <div className="bg-slate-100 border border-slate-200 p-4 rounded-xl text-xs text-slate-600 flex items-start gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <p>{response.legal_disclaimer}</p>
            </div>
          </div>

          {/* Evidence Inspector Side Panel */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm sticky top-24 space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <CornerDownRight className="w-4 h-4 text-blue-600" /> Evidence Inspector
              </h3>

              {selectedSpan ? (
                <div className="space-y-4 text-xs">
                  <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{selectedSpan.document_name}</span>
                      <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-mono font-semibold text-[11px]">
                        {selectedSpan.document_version}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-slate-600 font-mono text-[11px]">
                      <div>Section: {selectedSpan.section}</div>
                      <div>Clause: {selectedSpan.clause_id}</div>
                      <div>Page: {selectedSpan.page}</div>
                      <div>Jurisdiction: {selectedSpan.jurisdiction}</div>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <span className="text-slate-500 font-medium">Exact Source Evidence Span:</span>
                    <blockquote className="bg-blue-50/70 p-4 rounded-xl border border-blue-200 text-blue-950 font-mono leading-relaxed text-xs italic">
                      "{selectedSpan.evidence_span}"
                    </blockquote>
                  </div>

                  <div className="pt-2 text-slate-500 text-[11px] flex items-center justify-between border-t border-slate-100">
                    <span>Retrieval Confidence: {(selectedSpan.retrieval_confidence * 100).toFixed(1)}%</span>
                    <span>Effective: {selectedSpan.effective_date || 'N/A'}</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">Select a claim on the left to inspect its backing evidence span.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
