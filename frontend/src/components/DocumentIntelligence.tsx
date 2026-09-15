import React from 'react';
import { DocumentMetadata } from '../types';
import { Cpu, CheckCircle2, AlertTriangle, Shield, Clock } from 'lucide-react';

interface DocumentIntelligenceProps {
  documents: DocumentMetadata[];
}

export const DocumentIntelligence: React.FC<DocumentIntelligenceProps> = ({ documents }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-600" /> Document Intelligence Overview
        </h2>
        <p className="text-xs text-slate-500">
          Synthesizes holistic risk indicators, party obligations, and temporal chains across your document library.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <span className="text-xs font-mono text-slate-500 uppercase">Total Ingested Legal Documents</span>
          <p className="text-3xl font-extrabold text-blue-600">{documents.length}</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <span className="text-xs font-mono text-slate-500 uppercase">Indexed Clause Provenance Spans</span>
          <p className="text-3xl font-extrabold text-emerald-600">
            {documents.reduce((acc, d) => acc + d.clause_count, 0)}
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <span className="text-xs font-mono text-slate-500 uppercase">Governing Jurisdictions Detected</span>
          <p className="text-3xl font-extrabold text-amber-600">
            {Array.from(new Set(documents.map((d) => d.jurisdiction))).length}
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Active Document Library Summary
        </h3>
        <div className="space-y-3">
          {documents.map((d) => (
            <div key={d.document_id} className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="font-bold text-slate-900 text-sm">{d.filename}</span>
                <p className="text-xs text-slate-500">Parties: {d.parties.join(', ') || 'General'}</p>
              </div>
              <div className="flex items-center gap-3 text-xs font-mono">
                <span className="px-2.5 py-1 rounded bg-blue-100 text-blue-800 font-bold">
                  Version: {d.document_version}
                </span>
                <span className="px-2.5 py-1 rounded bg-slate-200 text-slate-800 font-semibold">
                  Effective: {d.effective_date || '2026-01-01'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
