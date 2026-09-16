import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { MermaidViewer } from './MermaidViewer';
import { Layers, Database, RefreshCw, CheckCircle2 } from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  const [diagramType, setDiagramType] = useState<'system' | 'erd'>('system');
  const [chartData, setChartData] = useState<{ mermaid_code: string; is_valid: boolean } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDiagram = async (type: 'system' | 'erd') => {
    setIsLoading(true);
    try {
      const data = await api.getDiagram(type, type === 'system' ? 'MANABI Architecture' : 'MANABI Schema');
      setChartData(data);
    } catch (err) {
      console.error('Failed to load diagram:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagram(diagramType);
  }, [diagramType]);

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Architectural & Schema Diagram Viewer
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 font-semibold border border-teal-500/30">
              MERMAID.JS ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Visual representations of platform component boundaries, network topologies, and relational entity models.
          </p>
        </div>

        {/* Toggle Switches */}
        <div className="flex items-center gap-2 bg-surface-raised p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setDiagramType('system')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              diagramType === 'system'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>System Architecture</span>
          </button>

          <button
            onClick={() => setDiagramType('erd')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              diagramType === 'erd'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Database ERD</span>
          </button>
        </div>
      </div>

      {/* Main Diagram Canvas */}
      <div className="p-6 rounded-2xl glass-panel border border-white/10 space-y-4 min-h-[500px]">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono text-slate-300">
              {diagramType === 'system' ? 'MANABI Distributed Monolith Flow' : 'PostgreSQL pgvector Schema'}
            </span>
          </div>
          <button
            onClick={() => fetchDiagram(diagramType)}
            disabled={isLoading}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
        </div>

        {isLoading ? (
          <div className="h-96 flex items-center justify-center text-slate-500 gap-2">
            <RefreshCw className="w-5 h-5 animate-spin text-teal-400" />
            <span className="text-xs font-mono">Synthesizing Mermaid Diagram...</span>
          </div>
        ) : chartData ? (
          <MermaidViewer chart={chartData.mermaid_code} className="bg-transparent border-0" />
        ) : null}
      </div>
    </div>
  );
};
