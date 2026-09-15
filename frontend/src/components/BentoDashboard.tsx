import React from 'react';
import { DocumentMetadata } from '../types';
import { Cpu, AlertTriangle, ShieldAlert, Clock, Scale, FileText, ArrowRight } from 'lucide-react';

interface BentoDashboardProps {
  documents: DocumentMetadata[];
  onNavigateToTab: (tab: string) => void;
}

export const BentoDashboard: React.FC<BentoDashboardProps> = ({ documents, onNavigateToTab }) => {
  const primaryDoc = documents[0];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono text-blue-700 uppercase tracking-wider block mb-1">
            Document Intelligence Overview • Bento Dashboard
          </span>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="w-6 h-6 text-blue-600" /> Executive Legal Scope & Risk Analysis
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigateToTab('compare')}
            className="px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-xl text-xs font-semibold border border-blue-200 transition-colors flex items-center gap-1.5"
          >
            Compare Versions <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Tile 1: Plain-Language Summary (Spans 2 columns) */}
        <div className="md:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-600" /> Executive Document Summary
            </h3>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-mono text-xs border border-blue-200">
              {primaryDoc?.filename || 'Master Agreement'}
            </span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
            This Master Services Agreement governs commercial IT service obligations between Enterprise Corp and TechVendor LLC.
            Key terms enforce a 90-day termination notice window in v1.0, amended to 30 days in v2.0, with liability capped at $1,000,000 under Maharashtra jurisdiction.
          </p>
        </div>

        {/* Tile 2: Identified Parties & Jurisdiction */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-600" /> Parties & Jurisdiction
          </h3>
          <div className="space-y-2 text-xs">
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="text-slate-500 block font-mono">Contracting Parties:</span>
              <span className="font-semibold text-slate-900">
                {primaryDoc?.parties.join(', ') || 'Enterprise Corp, TechVendor LLC'}
              </span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1">
              <span className="text-slate-500 block font-mono">Governing Law:</span>
              <span className="font-semibold text-blue-700">
                {primaryDoc?.jurisdiction || 'Maharashtra State Law'}
              </span>
            </div>
          </div>
        </div>

        {/* Tile 3: Key Obligations Count */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <span className="text-xs font-mono text-slate-500 uppercase">Extracted Legal Obligations</span>
          <p className="text-4xl font-extrabold text-blue-600">
            {documents.reduce((acc, d) => acc + d.clause_count, 0)}
          </p>
          <p className="text-xs text-slate-500">Indexed clauses across {documents.length} document version(s)</p>
        </div>

        {/* Tile 4: Deadlines & Timeline */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-600" /> Critical Dates & Deadlines
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-slate-600">v1.0 Effective:</span>
              <span className="font-mono font-semibold text-slate-900">2026-01-01</span>
            </div>
            <div className="flex items-center justify-between p-2.5 bg-amber-50 rounded-xl border border-amber-200 text-amber-900">
              <span className="font-medium">v2.0 Amendment:</span>
              <span className="font-mono font-semibold text-amber-800">2026-06-01</span>
            </div>
          </div>
        </div>

        {/* Tile 5: Risk Shift Summary */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-emerald-600" /> Risk Shift Indicator
          </h3>
          <div className="bg-emerald-50 p-3 rounded-xl border border-emerald-200 text-xs text-emerald-800 space-y-1">
            <span className="font-semibold">Moderate Liability Expansion</span>
            <p>Liability cap raised from $500k to $1M in v2.0, providing enhanced claim coverage.</p>
          </div>
        </div>

        {/* Tile 6: Potential Inconsistencies Alert (Full Width Spans 3 columns) */}
        <div className="md:col-span-3 bg-red-50/70 p-6 rounded-2xl border border-red-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-red-900 uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600" /> Potential Inconsistent Provision Detected
            </h3>
            <span className="px-2.5 py-0.5 rounded-full bg-red-100 text-red-800 text-xs font-semibold border border-red-300">
              Conflict Alert
            </span>
          </div>
          <p className="text-xs text-red-950 leading-relaxed">
            <strong>Notice Period Mismatch:</strong> Master Agreement v1.0 specifies a 90-day termination notice requirement, whereas Amendment v2.0 explicitly reduces notice to 30 days. Ensure counsel reviews amendment superseding rules.
          </p>
        </div>
      </div>
    </div>
  );
};
