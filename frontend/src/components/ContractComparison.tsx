import React, { useState } from 'react';
import { DocumentMetadata, ComparisonResult } from '../types';
import { GitCompare, ArrowRight, ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';

interface ContractComparisonProps {
  documents: DocumentMetadata[];
  onRunComparison: (docAId: string, docBId: string) => Promise<ComparisonResult>;
}

export const ContractComparison: React.FC<ContractComparisonProps> = ({ documents, onRunComparison }) => {
  const [docAId, setDocAId] = useState(documents[0]?.document_id || '');
  const [docBId, setDocBId] = useState(documents[1]?.document_id || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);

  const handleCompare = async () => {
    if (!docAId || !docBId) return;
    setLoading(true);
    try {
      const res = await onRunComparison(docAId, docBId);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CONFLICTING':
        return <span className="bg-red-100 text-red-800 border border-red-300 text-xs px-2.5 py-0.5 rounded-full font-bold">CRITICAL CONFLICT</span>;
      case 'MODIFIED':
        return <span className="bg-amber-100 text-amber-800 border border-amber-300 text-xs px-2.5 py-0.5 rounded-full font-bold">MODIFIED</span>;
      case 'ADDED':
        return <span className="bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs px-2.5 py-0.5 rounded-full font-bold">NEW ADDITION</span>;
      case 'REMOVED':
        return <span className="bg-rose-100 text-rose-800 border border-rose-300 text-xs px-2.5 py-0.5 rounded-full font-bold">REMOVED</span>;
      default:
        return <span className="bg-slate-100 text-slate-700 border border-slate-300 text-xs px-2.5 py-0.5 rounded-full font-semibold">UNCHANGED</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Document Selector Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <GitCompare className="w-5 h-5 text-blue-600" /> Semantic Contract & Policy Comparison
        </h2>
        <p className="text-xs text-slate-500 mb-4">
          Compares legal contracts across key dimensions (Notice periods, Liability caps, Indemnification, Governing Law) rather than superficial text diffs.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1.5">Select Original Document (A)</label>
            <select
              value={docAId}
              onChange={(e) => setDocAId(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 focus:border-blue-600 font-medium"
            >
              {documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.filename} ({d.document_version})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-center pb-2 hidden md:flex">
            <ArrowRight className="w-5 h-5 text-slate-400" />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-600 block mb-1.5">Select Amended Document (B)</label>
            <select
              value={docBId}
              onChange={(e) => setDocBId(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs text-slate-900 focus:border-blue-600 font-medium"
            >
              {documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.filename} ({d.document_version})
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={loading || !docAId || !docBId}
          className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
        >
          {loading ? 'Analyzing Comparative Dimensions...' : 'Execute Semantic Comparison'}
        </button>
      </div>

      {/* Comparison Matrix Results */}
      {result && (
        <div className="space-y-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-blue-600 text-xs text-slate-700">
            <span className="font-bold text-slate-900">Comparative Summary:</span> {result.summary}
          </div>

          <div className="space-y-4">
            {result.items.map((item, idx) => (
              <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    {item.dimension}
                  </h3>
                  <div>{getStatusBadge(item.status)}</div>
                </div>

                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200/80">
                  {item.analysis}
                </p>

                {/* Side-by-side text comparison */}
                {(item.doc_a_text || item.doc_b_text) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
                    <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1">
                      <span className="text-[11px] font-mono text-slate-500 uppercase">{result.doc_a_name} Excerpt</span>
                      <p className="text-slate-800 italic">{item.doc_a_text || 'Provision Not Present'}</p>
                    </div>

                    <div className="bg-blue-50/60 p-3.5 rounded-xl border border-blue-200 space-y-1">
                      <span className="text-[11px] font-mono text-blue-700 uppercase">{result.doc_b_name} Excerpt</span>
                      <p className="text-blue-950 italic">{item.doc_b_text || 'Provision Not Present'}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
