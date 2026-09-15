import React, { useState, useEffect } from 'react';
import { LawyerHandoffPack } from '../types';
import { Share2, Printer, Calendar, HelpCircle, FileText, Scale } from 'lucide-react';

interface LawyerHandoffViewProps {
  getAuthToken?: () => string;
}

export const LawyerHandoffView: React.FC<LawyerHandoffViewProps> = ({ getAuthToken }) => {
  const [pack, setPack] = useState<LawyerHandoffPack | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHandoff();
  }, []);

  const fetchHandoff = async () => {
    setLoading(true);
    try {
      const token = (getAuthToken ? getAuthToken() : '') || localStorage.getItem('lawpedia_token') || '';
      const res = await fetch('/api/handoff', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        if (data && Array.isArray(data.parties_involved)) {
          setPack(data);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Share2 className="w-5 h-5 text-blue-600" /> Lawyer Handoff Pack Generator
          </h2>
          <p className="text-xs text-slate-500">
            Produces a structured 10-part legal brief to streamline professional legal consultation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchHandoff}
            disabled={loading}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold border border-slate-200 transition-colors"
          >
            Refresh Handoff Brief
          </button>
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-600/20 transition-all flex items-center gap-1.5"
          >
            <Printer className="w-4 h-4" /> Export / Print Brief
          </button>
        </div>
      </div>

      {pack && (
        <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-8 print:shadow-none print:border-none print:p-0">
          {/* Header metadata */}
          <div className="border-b border-slate-200 pb-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-xs font-mono text-blue-700 uppercase tracking-widest font-bold block mb-1">
                Lawpedia Matter Brief #{pack.handoff_id}
              </span>
              <h3 className="text-xl font-bold text-slate-900">Legal Information Handoff Package</h3>
              <p className="text-xs text-slate-500">Generated at {pack.generated_at}</p>
            </div>
            <div className="flex items-center gap-2 bg-blue-50 p-3.5 rounded-xl border border-blue-200 text-xs text-blue-900 font-semibold">
              <Scale className="w-5 h-5 text-blue-600" />
              <span>Prepared for Professional Legal Counsel Review</span>
            </div>
          </div>

          {/* Section 1: Matter Summary */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              1. Matter Executive Summary
            </h4>
            <p className="text-sm text-slate-800 bg-slate-50 p-4 rounded-xl border border-slate-200">
              {pack.matter_summary}
            </p>
          </div>

          {/* Section 2 & 3: Parties & Documents */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">2. Identified Parties</h4>
              <ul className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1.5 text-xs text-slate-800">
                {pack.parties_involved.map((p) => (
                  <li key={p} className="flex items-center gap-2 font-semibold">
                    <span className="w-2 h-2 rounded-full bg-blue-600"></span> {p}
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">3. Relevant Documents</h4>
              <ul className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1.5 text-xs text-slate-800">
                {pack.relevant_documents.map((d) => (
                  <li key={d} className="flex items-center gap-2 font-mono">
                    <FileText className="w-3.5 h-3.5 text-blue-600" /> {d}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Section 4 & 5: Key Clauses & Obligations */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              4. Key Clauses & Extracted Obligations
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pack.key_clauses.map((c) => (
                <div key={c.clause_id} className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2 text-xs">
                  <div className="flex items-center justify-between font-mono text-slate-500">
                    <span>{c.section}</span>
                    <span className="text-blue-700 font-semibold">{c.clause_id}</span>
                  </div>
                  <h5 className="font-bold text-slate-900">{c.title}</h5>
                  <p className="text-slate-700 italic font-mono">"{c.excerpt}"</p>
                </div>
              ))}
            </div>
          </div>

          {/* Section 6: Important Dates */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-amber-600" /> 6. Critical Dates & Deadlines
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {pack.important_dates.map((d) => (
                <div key={d.event} className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs space-y-1">
                  <span className="text-slate-500 block font-mono">{d.event}</span>
                  <span className="font-mono text-amber-800 font-bold">{d.date}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Section 7 & 8: Conflicts & Unanswered Questions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-800">7. Identified Conflicts / Risk Shifts</h4>
              <div className="bg-amber-50 p-4 rounded-xl border border-amber-200 text-xs text-amber-950 space-y-2 font-medium">
                {pack.potential_conflicts.map((c) => (
                  <p key={c}>• {c}</p>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">8. Unanswered Questions</h4>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-2">
                {pack.unanswered_questions.map((u) => (
                  <p key={u}>• {u}</p>
                ))}
              </div>
            </div>
          </div>

          {/* Section 10: Questions to Ask a Lawyer */}
          <div className="space-y-3 bg-blue-50 p-6 rounded-2xl border border-blue-200">
            <h4 className="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-blue-600" /> 10. Questions to Ask Your Attorney
            </h4>
            <ul className="space-y-2 text-xs text-blue-950">
              {pack.questions_for_lawyer.map((q, i) => (
                <li key={q} className="flex items-start gap-2 font-medium">
                  <span className="font-bold text-blue-700">{i + 1}.</span>
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
