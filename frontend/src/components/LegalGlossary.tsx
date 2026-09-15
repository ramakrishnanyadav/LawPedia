import React, { useState } from 'react';
import { HelpCircle, Info } from 'lucide-react';

const GLOSSARY_DICTIONARY: Record<string, { plainTerm: string; definition: string }> = {
  indemnify: {
    plainTerm: "Pay for damages",
    definition: "Agreement to cover financial losses, legal costs, or damages suffered by the other party."
  },
  indemnification: {
    plainTerm: "Protection against loss",
    definition: "An obligation where one party compensates the other for costs, damages, or legal claims."
  },
  "force majeure": {
    plainTerm: "Unforeseeable disaster clause",
    definition: "Frees parties from obligation when extraordinary events (like natural disasters or wars) occur."
  },
  "liquidated damages": {
    plainTerm: "Pre-agreed breach fine",
    definition: "A specific amount of money agreed upon in advance to be paid if a contract rule is broken."
  },
  jurisdiction: {
    plainTerm: "Governing state court",
    definition: "The specific state, government body, or court system that has authority over this legal contract."
  },
  breach: {
    plainTerm: "Breaking a rule",
    definition: "Failing to perform any obligation promised under the legal agreement."
  },
  "cure period": {
    plainTerm: "Fix-it window",
    definition: "A specified number of days given to fix a breach before the contract can be terminated or penalized."
  },
  "liability cap": {
    plainTerm: "Maximum payment limit",
    definition: "The maximum total amount of money a company can be forced to pay under the contract."
  }
};

interface LegalGlossaryProps {
  term: string;
  displayText?: string;
}

export const LegalGlossary: React.FC<LegalGlossaryProps> = ({ term, displayText }) => {
  const [isOpen, setIsOpen] = useState(false);
  const normalizedKey = term.toLowerCase().strip ? term.toLowerCase().trim() : term.toLowerCase();
  const entry = GLOSSARY_DICTIONARY[normalizedKey];

  if (!entry) {
    return <span>{displayText || term}</span>;
  }

  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="underline decoration-blue-500 decoration-dotted underline-offset-4 text-blue-900 font-semibold hover:text-blue-700 focus:outline-none"
        aria-label={`Definition for legal term ${term}`}
      >
        {displayText || term}
        <HelpCircle className="w-3 h-3 text-blue-600 inline-block ml-0.5" />
      </button>

      {isOpen && (
        <div className="absolute left-0 bottom-full mb-1.5 z-50 w-64 bg-slate-900 text-white rounded-xl p-3 shadow-2xl text-xs space-y-1 animate-in fade-in zoom-in-95 duration-100">
          <div className="flex items-center justify-between text-blue-300 font-bold border-b border-slate-800 pb-1">
            <span>{term}</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-200">
              Plain: {entry.plainTerm}
            </span>
          </div>
          <p className="text-slate-300 text-[11px] leading-relaxed">{entry.definition}</p>
        </div>
      )}
    </span>
  );
};
