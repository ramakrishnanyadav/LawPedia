import React, { useState } from 'react';
import { DocumentMetadata } from '../types';
import { Upload, FileText, Plus, Eye } from 'lucide-react';

interface DocumentLibraryProps {
  documents: DocumentMetadata[];
  onUpload: (filename: string, textContent: string, version: string) => Promise<void>;
  onSelectDocument: (doc: DocumentMetadata) => void;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({ documents, onUpload, onSelectDocument }) => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [filename, setFilename] = useState('');
  const [version, setVersion] = useState('v1.0');
  const [text, setText] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filename.trim() || !text.trim()) return;
    setUploading(true);
    try {
      await onUpload(filename, text, version);
      setShowUploadModal(false);
      setFilename('');
      setText('');
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" /> Evidence Library & Document Management
          </h2>
          <p className="text-xs text-slate-500">
            Upload contracts, policies, and amendments. Uploaded documents are parsed into structured provenance spans.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <Plus className="w-4 h-4" /> Upload Document / Amendment
        </button>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-xl border border-slate-200 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Upload className="w-5 h-5 text-blue-600" /> Ingest New Untrusted Legal Document
            </h3>

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="doc-filename" className="text-slate-600 font-semibold block mb-1">Document Name / File</label>
                  <input
                    id="doc-filename"
                    type="text"
                    value={filename}
                    onChange={(e) => setFilename(e.target.value)}
                    placeholder="e.g. Master_Services_Agreement_v3.txt"
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 placeholder-slate-400 focus:border-blue-600 font-medium"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="doc-version" className="text-slate-600 font-semibold block mb-1">Version String</label>
                  <input
                    id="doc-version"
                    type="text"
                    value={version}
                    onChange={(e) => setVersion(e.target.value)}
                    placeholder="e.g. v3.0"
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-medium"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="doc-text" className="text-slate-600 font-semibold block mb-1">Document Text Content</label>
                <textarea
                  id="doc-text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste legal contract text, clauses, or agreement provisions here..."
                  rows={8}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg p-3 text-slate-900 font-mono text-xs placeholder-slate-400 focus:border-blue-600 focus:bg-white"
                  required
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 text-slate-500 hover:text-slate-800 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-md shadow-blue-600/20"
                >
                  {uploading ? 'Parsing & Indexing...' : 'Parse & Index Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documents.map((doc) => (
          <div key={doc.document_id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 hover:border-blue-400 transition-all group">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">
                  {doc.document_version}
                </span>
                <h3 className="font-bold text-slate-900 text-sm group-hover:text-blue-700 transition-colors">
                  {doc.filename}
                </h3>
              </div>
              <FileText className="w-5 h-5 text-slate-400 group-hover:text-blue-600" />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 font-mono bg-slate-50 p-3 rounded-xl border border-slate-200/80">
              <div>Clauses: {doc.clause_count}</div>
              <div>Pages: {doc.page_count}</div>
              <div>Jurisdiction: {doc.jurisdiction}</div>
              <div>Effective: {doc.effective_date || 'N/A'}</div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-100">
              <button
                onClick={() => onSelectDocument(doc)}
                className="text-xs text-blue-700 hover:text-blue-900 font-bold flex items-center gap-1"
              >
                <Eye className="w-3.5 h-3.5" /> Inspect Clauses
              </button>
              <span className="text-[10px] text-slate-400 font-mono">{doc.document_id}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
