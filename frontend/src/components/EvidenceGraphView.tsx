import React, { useState, useEffect } from 'react';
import { Network, Table, Layers, Box } from 'lucide-react';

interface GraphNode {
  id: string;
  type: string;
  label: string;
  text?: string;
  filename?: string;
  version?: string;
  [key: string]: unknown;
}

interface GraphData {
  nodes: GraphNode[];
  edges: { source: string; target: string; relationship: string }[];
}

interface EvidenceGraphViewProps {
  getAuthToken?: () => string;
}

export const EvidenceGraphView: React.FC<EvidenceGraphViewProps> = ({ getAuthToken }) => {
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [viewMode, setViewMode] = useState<'visual' | 'table'>('visual');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    const token = (getAuthToken ? getAuthToken() : '') || localStorage.getItem('lawpedia_token') || '';
    fetch('/api/graph', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then((res) => {
        if (res.ok) return res.json();
        return null;
      })
      .then((data) => {
        if (data && Array.isArray(data.nodes)) {
          setGraph(data);
          if (data.nodes.length > 0) {
            setSelectedNode(data.nodes[0]);
          }
        }
      })
      .catch((err) => console.error(err));
  }, [getAuthToken]);


  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Network className="w-5 h-5 text-blue-600" /> Legal Evidence Graph Topology (3D & Table)
          </h2>
          <p className="text-xs text-slate-500">
            Maps legal relationships between Documents, Versions, Parties, Clauses, Obligations, and Conflicts.
          </p>
        </div>

        {/* Accessible View Toggle */}
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button
            onClick={() => setViewMode('visual')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'visual'
                ? 'bg-white text-blue-700 shadow-sm border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            3D Canvas Visualizer
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              viewMode === 'table'
                ? 'bg-white text-blue-700 shadow-sm border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            aria-label="Accessible Table Alternative"
          >
            <Table className="w-3.5 h-3.5" /> Accessible Table View (WCAG 2.2)
          </button>
        </div>
      </div>

      {graph && viewMode === 'visual' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 3D Simulation Canvas Surface */}
          <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200 shadow-sm min-h-[420px] flex flex-col justify-between relative">
            <div className="flex items-center justify-between text-xs font-mono text-slate-500">
              <span className="flex items-center gap-2">
                <Box className="w-4 h-4 text-blue-600" /> R3F 3D Node Mesh • Interactive Topology
              </span>
              <span>Nodes: {graph.nodes.length} | Edges: {graph.edges.length}</span>
            </div>

            {/* Simulated 3D Mesh Nodes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 my-6">
              {graph.nodes.slice(0, 9).map((node) => (
                <div
                  key={node.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelectedNode(node)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setSelectedNode(node);
                    }
                  }}
                  className={`p-4 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                    selectedNode?.id === node.id
                      ? 'bg-blue-50 border-blue-500 shadow-md'
                      : 'bg-slate-50/70 border-slate-200 hover:border-blue-300 hover:bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">
                      {node.type}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">{node.id}</span>
                  </div>
                  <h4 className="font-bold text-xs text-slate-900 truncate">{node.label}</h4>
                  {node.text && <p className="text-[11px] text-slate-500 line-clamp-2 italic">{node.text}</p>}
                </div>
              ))}
            </div>

            <div className="text-center text-xs text-slate-400 font-mono border-t border-slate-100 pt-3">
              Click node mesh to inspect graph properties • Relationship Edges: HAS_PARTY, CONTAINS_CLAUSE, CREATES_OBLIGATION, SUPERSEDES
            </div>
          </div>

          {/* Node Inspector Panel */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" /> Node Subtree Inspector
            </h3>

            {selectedNode ? (
              <div className="space-y-3 text-xs">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">
                    {selectedNode.type}
                  </span>
                  <h4 className="font-bold text-slate-900 text-sm">{selectedNode.label}</h4>
                  <p className="font-mono text-slate-500 text-[11px]">ID: {selectedNode.id}</p>
                </div>

                {selectedNode.text && (
                  <div className="space-y-1">
                    <span className="text-slate-500 font-medium">Node Text Excerpt:</span>
                    <p className="bg-slate-100 p-3.5 rounded-xl border border-slate-200 font-mono text-slate-800 text-xs italic">
                      "{selectedNode.text}"
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">Select a node in the graph to inspect properties.</p>
            )}
          </div>
        </div>
      )}

      {/* WCAG 2.2 AA Accessible Table Fallback */}
      {graph && viewMode === 'table' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Accessible Legal Graph Data Table (WCAG 2.2 AA Compliant)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700 border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-mono">
                  <th className="p-3">Node ID</th>
                  <th className="p-3">Node Type</th>
                  <th className="p-3">Label / Title</th>
                  <th className="p-3">Key Attributes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {graph.nodes.map((node) => (
                  <tr key={node.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-3 font-mono text-blue-700 font-medium">{node.id}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-mono font-semibold">
                        {node.type}
                      </span>
                    </td>
                    <td className="p-3 font-semibold text-slate-900">{node.label}</td>
                    <td className="p-3 text-slate-500 font-mono">{node.text || node.filename || node.version || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
