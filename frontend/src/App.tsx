import React, { useState, useEffect } from 'react';
import { DocumentMetadata, AskQueryResponse, ComparisonResult } from './types';
import { Navbar } from './components/Navbar';
import { AskWorkspace } from './components/AskWorkspace';
import { DocumentLibrary } from './components/DocumentLibrary';
import { DocumentWorkspaceView } from './components/DocumentWorkspaceView';
import { ContractComparison } from './components/ContractComparison';
import { LawyerHandoffView } from './components/LawyerHandoffView';
import { SecurityMetricsDashboard } from './components/SecurityMetricsDashboard';
import { CommandPalette } from './components/CommandPalette';
import { AccessibilityPreferences, AccessibilitySettings } from './components/AccessibilityPreferences';
import { AuthModal } from './components/AuthModal';
import { UserProfile, DEMO_USER } from './config/firebase';
import { Calendar, AlertTriangle } from 'lucide-react';

const DEFAULT_A11Y_SETTINGS: AccessibilitySettings = {
  textScale: 100,
  highContrast: false,
  reduceMotion: false,
  dyslexiaFont: false,
  readingLevel: 'simple',
  disable3DGraph: false
};

export function App() {
  const [activeTab, setActiveTab] = useState('library');
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentMetadata | null>(null);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isA11yModalOpen, setIsA11yModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(DEMO_USER);
  const [a11ySettings, setA11ySettings] = useState<AccessibilitySettings>(() => {
    try {
      const saved = localStorage.getItem('lawpedia_a11y_settings');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
    return DEFAULT_A11Y_SETTINGS;
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const getAuthToken = () => user?.token || "";

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents', {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      const data = await res.json();
      const docs = data.documents || [];
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunQuery = async (query: string): Promise<AskQueryResponse> => {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({ query }),
    });
    return await res.json();
  };

  const handleUpload = async (filename: string, textContent: string, version: string) => {
    const formData = new FormData();
    formData.append('filename', filename);
    formData.append('text_content', textContent);
    formData.append('document_version', version);

    await fetch('/api/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: formData,
    });
    await fetchDocuments();
  };

  const handleRunComparison = async (docAId: string, docBId: string): Promise<ComparisonResult> => {
    const res = await fetch(`/api/compare?doc_a_id=${docAId}&doc_b_id=${docBId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      },
    });
    return await res.json();
  };


  return (
    <div
      className={`min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans ${
        a11ySettings.highContrast ? 'contrast-125' : ''
      }`}
      style={{
        fontSize: `${a11ySettings.textScale}%`
      }}
    >
      <Navbar
        activeTab={activeTab}
        setActiveTab={(t) => {
          setActiveTab(t);
          if (t === 'library') setSelectedDocument(null);
        }}
        documentCount={documents.length}
        user={user}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onOpenAccessibility={() => setIsA11yModalOpen(true)}
      />

      {/* Persistent Legal Assistance Disclaimer Banner */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2 text-xs text-amber-900 font-medium flex items-center justify-center gap-2 text-center">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong>LawPedia Legal Information Notice:</strong> LawPedia provides AI-assisted document navigation and evidence extraction for informational purposes only and does not constitute formal legal advice.
        </span>
      </div>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={(u) => setUser(u)}
      />

      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'library') setSelectedDocument(null);
        }}
        onSelectQuery={() => {
          setActiveTab('ask');
        }}
      />

      <AccessibilityPreferences
        isOpen={isA11yModalOpen}
        onClose={() => setIsA11yModalOpen(false)}
        settings={a11ySettings}
        onUpdateSettings={(newSettings) => setA11ySettings(newSettings)}
      />

      {/* Main Accessible Target Container */}
      <main id="main-content" tabIndex={-1} className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 outline-none">
        {activeTab === 'library' && !selectedDocument && (
          <DocumentLibrary
            documents={documents}
            onUpload={handleUpload}
            onSelectDocument={(doc) => setSelectedDocument(doc)}
          />
        )}

        {activeTab === 'library' && selectedDocument && (
          <DocumentWorkspaceView
            document={selectedDocument}
            documents={documents}
            onBack={() => setSelectedDocument(null)}
            onNavigateToTab={(t) => setActiveTab(t)}
            disable3DGraph={a11ySettings.disable3DGraph}
          />
        )}

        {activeTab === 'ask' && <AskWorkspace onRunQuery={handleRunQuery} />}

        {activeTab === 'compare' && (
          <ContractComparison documents={documents} onRunComparison={handleRunComparison} />
        )}

        {activeTab === 'dates' && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-amber-600" /> Important Dates & Contract Timeline
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 font-mono text-xs">
                <span>Master Agreement v1.0 Effective Date:</span>
                <span className="font-bold text-slate-900">2026-01-01</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-amber-50 rounded-xl border border-amber-200 font-mono text-xs text-amber-900">
                <span className="font-bold">Amendment v2.0 Revision Date:</span>
                <span className="font-bold text-amber-900">2026-06-01</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'handoff' && <LawyerHandoffView getAuthToken={getAuthToken} />}
        {activeTab === 'security' && <SecurityMetricsDashboard />}
      </main>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500 font-mono">
        Lawpedia v2.0 • Plain-Language Legal Intelligence Platform • WCAG 2.2 AAA Contrast Ready • India RPWD Act 2016 Compliant
      </footer>
    </div>
  );
}

export default App;
