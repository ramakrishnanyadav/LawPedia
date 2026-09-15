import React, { useState } from 'react';
import { DocumentMetadata } from '../types';
import { BentoDashboard } from './BentoDashboard';
import { EvidenceGraphView } from './EvidenceGraphView';
import { FileText, Cpu, Network, ArrowLeft, Layers, ShieldCheck } from 'lucide-react';

interface DocumentWorkspaceViewProps {
  document: DocumentMetadata;
  documents: DocumentMetadata[];
  onBack: () => void;
  onNavigateToTab: (tab: string) => void;
  disable3DGraph?: boolean;
}

export const DocumentWorkspaceView: React.FC<DocumentWorkspaceViewProps> = ({
  document,
  documents,
  onBack,
  onNavigateToTab,
  disable3DGraph
}) => {
  const [subTab, setSubTab] = useState<'summary' | 'clauses' | 'graph'>('summary');

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
            aria-label="Back to document library"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">
                {document.document_version}
              </span>
              <h2 className="text-xl font-bold text-slate-900">{document.filename}</h2>
            </div>
            <p className="text-xs text-slate-500 font-mono">
              Document ID: {document.document_id} • Pages: {document.page_count} • Clauses: {document.clause_count}
            </p>
          </div>
        </div>

        {/* Workspace Progressive Sub-Tabs */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button
            onClick={() => setSubTab('summary')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              subTab === 'summary' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" /> Plain Summary
          </button>
          <button
            onClick={() => setSubTab('clauses')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              subTab === 'clauses' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> See Every Clause
          </button>
          <button
            onClick={() => setSubTab('graph')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              subTab === 'graph' ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Network className="w-3.5 h-3.5" /> See How This Connects
          </button>
        </div>
      </div>

      {/* Sub-Tab Contents */}
      {subTab === 'summary' && (
        <BentoDashboard documents={documents} onNavigateToTab={onNavigateToTab} />
      )}

      {subTab === 'clauses' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Clause Hierarchy & Legal Triples
          </h3>
          <div className="space-y-3">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <span className="font-bold text-slate-900">SECTION 1. TERMINATION NOTICE</span>
                <span className="text-blue-700 font-semibold">CLAUSE_001</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-mono">
                Either party may terminate this Agreement by providing ninety (90) days written notice to the other party.
              </p>
              <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-600 font-mono">
                <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-900 font-semibold">Risk: MEDIUM</span>
                <span>Obligation: 90 Days Notice</span>
              </div>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <span className="font-bold text-slate-900">SECTION 2. LIMITATION OF LIABILITY</span>
                <span className="text-blue-700 font-semibold">CLAUSE_002</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed font-mono">
                The total aggregate liability of Vendor under this Agreement shall not exceed $500,000.
              </p>
              <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-600 font-mono">
                <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 font-semibold">Risk: LOW</span>
                <span>Financial Cap: $500,000</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {subTab === 'graph' && <EvidenceGraphView />}
    </div>
  );
};
