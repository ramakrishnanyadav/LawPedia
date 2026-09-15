import React, { useState, useEffect } from 'react';
import { Search, FileText, Cpu, GitCompare, Network, Share2, Shield, X, ArrowRight, CornerDownLeft } from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTab: (tab: string) => void;
  onSelectQuery: (query: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectTab,
  onSelectQuery
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onClose(); // parent toggle
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    { id: 'ask', title: 'Ask Workspace — Interrogate Documents', icon: Search, type: 'Route' },
    { id: 'library', title: 'Document Library — Ingest & List Contracts', icon: FileText, type: 'Route' },
    { id: 'intelligence', title: 'Document Intelligence Bento Dashboard', icon: Cpu, type: 'Route' },
    { id: 'compare', title: 'Semantic Contract Comparison Matrix', icon: GitCompare, type: 'Route' },
    { id: 'graph', title: 'Legal Evidence Graph Topology (3D + Table)', icon: Network, type: 'Route' },
    { id: 'handoff', title: 'Lawyer Handoff Pack Generator', icon: Share2, type: 'Route' },
    { id: 'query_1', title: 'Query: What is the termination notice period?', icon: Search, type: 'Sample Query', text: 'What is the termination notice period?' },
    { id: 'query_2', title: 'Query: Compare liability caps across versions', icon: Search, type: 'Sample Query', text: 'What are the liability caps across versions?' },
    { id: 'query_3', title: 'Query: Check for false premise in 30-day notice assumption', icon: Search, type: 'Sample Query', text: 'Does the contract give me 30 days notice in v1.0?' }
  ];

  const filteredActions = actions.filter((a) =>
    a.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-start justify-center pt-20 p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
        {/* Search Header */}
        <div className="relative border-b border-slate-100 px-4 py-3.5 flex items-center gap-3">
          <Search className="w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Type a command, search clauses, or jump to route... (Esc to close)"
            className="w-full bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none font-sans"
            autoFocus
          />
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action Results */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-slate-50">
          {filteredActions.length > 0 ? (
            filteredActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.id}
                  onClick={() => {
                    if (action.type === 'Route') {
                      onSelectTab(action.id);
                    } else if (action.text) {
                      onSelectQuery(action.text);
                    }
                    onClose();
                  }}
                  className="w-full px-3.5 py-3 rounded-xl flex items-center justify-between text-left hover:bg-blue-50/60 hover:border-blue-200 border border-transparent transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-100 group-hover:bg-blue-600 group-hover:text-white text-slate-600 transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-900 block">
                        {action.title}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-500 uppercase">
                      {action.type}
                    </span>
                    <CornerDownLeft className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </button>
              );
            })
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 font-mono">
              No matching actions or queries found.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-50 px-4 py-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span>
            Press <kbd className="px-1.5 py-0.5 bg-white border border-slate-200 rounded shadow-sm text-slate-700">⌘K</kbd> anytime to open
          </span>
          <span>Lawpedia Command Interface</span>
        </div>
      </div>
    </div>
  );
};
