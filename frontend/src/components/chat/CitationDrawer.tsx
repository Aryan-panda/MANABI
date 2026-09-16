import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { X, BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';

export const CitationDrawer: React.FC = () => {
  const { activeCitations, isCitationDrawerOpen, toggleCitationDrawer } = useAppStore();

  if (!isCitationDrawerOpen) return null;

  return (
    <aside className="fixed inset-y-0 right-0 w-96 bg-surface-raised/95 backdrop-blur-2xl border-l border-white/10 z-50 p-6 flex flex-col justify-between shadow-2xl animate-in slide-in-from-right duration-200">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="font-bold text-base text-white">Authoritative Evidence</h3>
          </div>
          <button
            onClick={() => toggleCitationDrawer(false)}
            className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-slate-400 mt-3 mb-4 leading-relaxed">
          The following institutional and engineering sources were retrieved via pgvector similarity search to ground the assistant's response.
        </p>

        {/* Citations List */}
        <div className="space-y-3 overflow-y-auto max-h-[calc(100vh-12rem)] pr-1">
          {activeCitations.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No citations attached to this turn.</p>
          ) : (
            activeCitations.map((c, i) => (
              <div
                key={c.chunk_id || i}
                className="p-3.5 rounded-xl border border-white/10 bg-surface/80 space-y-2 hover:border-brand-500/40 transition"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-semibold text-white leading-snug">
                    {c.title || 'Official Document'}
                  </h4>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold shrink-0">
                    {(c.relevance_score * 100).toFixed(0)}% MATCH
                  </span>
                </div>

                <div className="text-[11px] text-brand-300 font-medium">
                  {c.section && <span>Section: {c.section}</span>}
                  {c.page && <span> • Page {c.page}</span>}
                </div>

                <p className="text-xs text-slate-300 bg-black/40 p-2.5 rounded-lg border border-white/5 font-mono text-[11px] leading-relaxed">
                  "{c.text}"
                </p>

                <div className="text-[10px] text-slate-500 truncate">
                  Source: {c.source}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="pt-4 border-t border-white/10 text-[11px] text-slate-500 text-center">
        Grounding verified by MANABI pgvector Engine
      </div>
    </aside>
  );
};
