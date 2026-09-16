import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import {
  GraduationCap,
  Cpu,
  TrendingUp,
  Briefcase,
  Scale,
  Plus,
  MessageSquare,
  ChevronRight,
  Database,
  Layers,
} from 'lucide-react';
import { AgentId } from '../../types';

export const Sidebar: React.FC = () => {
  const {
    activeAgent,
    setActiveAgent,
    conversations,
    currentConversationId,
    setCurrentConversationId,
    setMessages,
  } = useAppStore();

  const agents: Array<{
    id: AgentId;
    name: string;
    tagline: string;
    color: string;
    icon: React.ReactNode;
    isFull: boolean;
  }> = [
    {
      id: 'academic',
      name: 'Academic Advisor',
      tagline: 'Curriculum, policies, LangGraph plan review',
      color: 'hover:border-blue-500/50 hover:bg-blue-500/5',
      icon: <GraduationCap className="w-4 h-4 text-blue-400" />,
      isFull: true,
    },
    {
      id: 'engineering',
      name: 'Engineering Architect',
      tagline: 'System design, calculators & Mermaid diagrams',
      color: 'hover:border-emerald-500/50 hover:bg-emerald-500/5',
      icon: <Cpu className="w-4 h-4 text-emerald-400" />,
      isFull: true,
    },
    {
      id: 'commerce',
      name: 'Commerce & Finance',
      tagline: 'Unit economics, valuation, cost models',
      color: 'hover:border-amber-500/50 hover:bg-amber-500/5',
      icon: <TrendingUp className="w-4 h-4 text-amber-400" />,
      isFull: false,
    },
    {
      id: 'management',
      name: 'Management & Strategy',
      tagline: 'OKRs, agile delivery, organizational scaling',
      color: 'hover:border-purple-500/50 hover:bg-purple-500/5',
      icon: <Briefcase className="w-4 h-4 text-purple-400" />,
      isFull: false,
    },
    {
      id: 'law',
      name: 'Legal Intelligence',
      tagline: 'Contracts, IP & compliance education',
      color: 'hover:border-pink-500/50 hover:bg-pink-500/5',
      icon: <Scale className="w-4 h-4 text-pink-400" />,
      isFull: false,
    },
  ];

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
  };

  return (
    <aside className="w-80 h-[calc(100vh-4rem)] border-r border-border/80 bg-surface/50 backdrop-blur-xl flex flex-col justify-between p-4 overflow-y-auto">
      {/* Upper: Agent Selector & New Session */}
      <div className="space-y-4">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-medium text-sm shadow-glow transition active:scale-[0.98]"
        >
          <Plus className="w-4 h-4" />
          <span>Start New Session</span>
        </button>

        {/* Domain Agents Section */}
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-1 mb-2 block">
            Select Domain Agent
          </span>
          <div className="space-y-1.5">
            {agents.map((ag) => {
              const isSelected = activeAgent === ag.id;
              return (
                <button
                  key={ag.id}
                  onClick={() => setActiveAgent(ag.id)}
                  className={`w-full text-left p-2.5 rounded-xl border transition flex items-start gap-3 ${
                    isSelected
                      ? 'border-brand-500/80 bg-brand-500/10 shadow-sm'
                      : `border-white/5 bg-surface-raised/40 ${ag.color}`
                  }`}
                >
                  <div className="p-2 rounded-lg bg-white/5 mt-0.5">{ag.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-semibold text-white truncate">{ag.name}</h4>
                      {ag.isFull && (
                        <span className="text-[9px] font-mono px-1 rounded bg-brand-500/20 text-brand-300 font-medium">
                          FULL
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400 truncate mt-0.5">{ag.tagline}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Recent Conversations */}
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-1 mb-2 block">
            Recent Sessions
          </span>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {conversations.length === 0 ? (
              <p className="text-xs text-slate-500 italic px-2 py-2">No past sessions yet.</p>
            ) : (
              conversations.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setCurrentConversationId(c.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs flex items-center justify-between transition ${
                    currentConversationId === c.id
                      ? 'bg-white/10 text-white font-medium'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <MessageSquare className="w-3.5 h-3.5 text-slate-500" />
                    <span className="truncate">{c.title}</span>
                  </div>
                  <ChevronRight className="w-3 h-3 text-slate-600" />
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Footer: Infrastructure Indicators */}
      <div className="pt-4 border-t border-white/5 space-y-2 text-[11px] text-slate-400 font-mono">
        <div className="flex items-center justify-between px-1">
          <span className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            PostgreSQL + pgvector
          </span>
          <span className="text-emerald-400">READY</span>
        </div>
        <div className="flex items-center justify-between px-1">
          <span className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            Model Gateway
          </span>
          <span className="text-slate-300">MULTI-PROVIDER</span>
        </div>
      </div>
    </aside>
  );
};
