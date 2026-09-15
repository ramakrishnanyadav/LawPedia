import React from 'react';
import { UserProfile } from '../config/firebase';
import { Scale, FileText, Search, GitCompare, Calendar, Share2, Command, Sliders, LogIn, User } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  documentCount: number;
  user: UserProfile | null;
  onOpenAuth: () => void;
  onOpenCommandPalette: () => void;
  onOpenAccessibility: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  documentCount,
  user,
  onOpenAuth,
  onOpenCommandPalette,
  onOpenAccessibility
}) => {
  const primaryTabs = [
    { id: 'library', label: `My Documents (${documentCount})`, icon: FileText },
    { id: 'ask', label: 'Ask a Question', icon: Search },
    { id: 'compare', label: 'Compare', icon: GitCompare },
    { id: 'dates', label: 'Important Dates', icon: Calendar },
    { id: 'handoff', label: 'Get Help', icon: Share2 }
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-3 shadow-sm">
      {/* Skip to Main Content Link for Screen Readers */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-lg"
      >
        Skip to main content
      </a>

      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo & Platform Title */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600 text-white rounded-xl shadow-md shadow-blue-600/20 flex items-center justify-center">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900 flex items-center gap-2">
              Lawpedia<span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-semibold">EGLR v2.0</span>
            </h1>
            <p className="text-xs text-slate-500 font-mono">Plain-Language Evidence Intelligence</p>
          </div>
        </div>

        {/* Streamlined 5-Item Primary Navigation */}
        <nav className="flex items-center gap-1 overflow-x-auto w-full md:w-auto p-1 bg-slate-100/80 rounded-xl border border-slate-200/80" aria-label="Primary Plain Language Navigation">
          {primaryTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all duration-150 focus:outline-none min-h-[44px] min-w-[44px] ${
                  isActive
                    ? 'bg-white text-blue-700 shadow-sm border border-slate-200/80'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="whitespace-nowrap">{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Action Controls: Search, Accessibility & Firebase Auth */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenCommandPalette}
            className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200/80 text-slate-700 px-3 py-2 rounded-xl text-xs font-semibold border border-slate-200 transition-colors shadow-sm min-h-[44px]"
            aria-label="Open command palette search"
          >
            <Command className="w-3.5 h-3.5 text-blue-600" />
            <span className="hidden sm:inline">Search / ⌘K</span>
          </button>

          <button
            onClick={onOpenAccessibility}
            className="p-2.5 bg-slate-100 hover:bg-slate-200/80 text-slate-700 rounded-xl border border-slate-200 transition-colors shadow-sm min-h-[44px] min-w-[44px] flex items-center justify-center"
            title="Accessibility & Reading Preferences"
            aria-label="Accessibility & Reading Preferences"
          >
            <Sliders className="w-4 h-4 text-blue-600" />
          </button>

          <button
            onClick={onOpenAuth}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-xl text-xs font-bold shadow-md shadow-blue-600/20 transition-all min-h-[44px]"
          >
            {user ? (
              <>
                <User className="w-3.5 h-3.5 text-white" />
                <span className="max-w-[100px] truncate">{user.displayName}</span>
              </>
            ) : (
              <>
                <LogIn className="w-3.5 h-3.5 text-white" />
                <span>Log In</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
