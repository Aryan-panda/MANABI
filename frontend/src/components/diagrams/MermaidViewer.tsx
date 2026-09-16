import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Copy, Check, Maximize2 } from 'lucide-react';

interface MermaidViewerProps {
  chart: string;
  id?: string;
  className?: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    darkMode: true,
    background: '#0a0d14',
    primaryColor: '#6366f1',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#818cf8',
    lineColor: '#94a3b8',
    secondaryColor: '#10b981',
    tertiaryColor: '#1e293b',
  },
  fontFamily: 'Inter, sans-serif',
});

export const MermaidViewer: React.FC<MermaidViewerProps> = ({ chart, id, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const uniqueId = useRef(id || `mermaid-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      try {
        setError(null);
        if (!chart.trim()) return;
        const { svg } = await mermaid.render(uniqueId.current, chart.trim());
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to render Mermaid diagram');
        }
      }
    };
    renderChart();
    return () => {
      isMounted = false;
    };
  }, [chart]);

  const handleCopy = () => {
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-950/40 border border-red-800/40 text-red-300 text-xs font-mono my-2">
        <p className="font-semibold mb-1">Mermaid Syntax Warning:</p>
        <p>{error}</p>
        <pre className="mt-2 p-2 bg-black/40 rounded text-slate-400 overflow-x-auto">{chart}</pre>
      </div>
    );
  }

  return (
    <div className={`relative group my-3 rounded-xl border border-white/10 bg-surface/80 backdrop-blur-md overflow-hidden ${className}`}>
      {/* Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/5 bg-white/[0.02]">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Interactive Diagram
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            className="p-1.5 rounded hover:bg-white/10 text-slate-400 hover:text-white transition text-xs flex items-center gap-1"
            title="Copy Mermaid Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Code'}</span>
          </button>
        </div>
      </div>

      {/* Rendered SVG Content */}
      <div
        ref={containerRef}
        className="p-4 overflow-x-auto flex justify-center items-center [&>svg]:max-w-full [&>svg]:h-auto"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
};
