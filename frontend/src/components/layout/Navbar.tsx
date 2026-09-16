import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import {
  GraduationCap,
  Cpu,
  TrendingUp,
  Briefcase,
  Scale,
  Sparkles,
  BookOpen,
  Calculator,
  Brain,
  Layers,
} from 'lucide-react';
import { AgentId } from '../../types';

export const Navbar: React.FC = () => {
  const { activeAgent, activeTab, setActiveTab } = useAppStore();

  const agentDetails: Record<AgentId, { name: string; color: string; icon: React.ReactNode }> = {
    academic: {
      name: 'Academic Advisor',
      color: 'from-blue-500 to-indigo-600',
      icon: <GraduationCap className="w-4 h-4 text-blue-400" />,
    },
    engineering: {
      name: 'Engineering Architect',
      color: 'from-emerald-500 to-teal-600',
      icon: <Cpu className="w-4 h-4 text-emerald-400" />,
    },
    commerce: {
      name: 'Commerce & Finance',
      color: 'from-amber-500 to-orange-600',
      icon: <TrendingUp className="w-4 h-4 text-amber-400" />,
    },
    management: {
      name: 'Management & Strategy',
      color: 'from-purple-500 to-violet-600',
      icon: <Briefcase className="w-4 h-4 text-purple-400" />,
    },
    law: {
      name: 'Legal Intelligence',
      color: 'from-pink-500 to-rose-600',
      icon: <Scale className="w-4 h-4 text-pink-400" />,
    },
  };

  const current = agentDetails[activeAgent];

  return (
    <header className="h-16 border-b border-border/80 bg-surface/70 backdrop-blur-xl px-6 flex items-center justify-between z-30 sticky top-0">
      {/* Brand & Platform Identity */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 p-0.5 shadow-glow flex items-center justify-center">
          <div className="w-full h-full bg-surface rounded-[10px] flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-brand-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              MANABI
            </h1>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 font-mono font-medium border border-brand-500/30">
              MODULAR MONOLITH
            </span>
          </div>
          <p className="text-xs text-slate-400 hidden sm:block">Agentic Intelligence & Learning Platform</p>
        </div>
      </div>

      {/* Center Tool Navigation Tabs */}
      <nav className="flex items-center gap-1 bg-surface-raised/80 p-1 rounded-xl border border-white/5 shadow-inner">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'chat'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Chat Agent</span>
        </button>

        <button
          onClick={() => setActiveTab('plan_reviewer')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'plan_reviewer'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          <span>Academic Reviewer</span>
        </button>

        <button
          onClick={() => setActiveTab('calculator')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'calculator'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Calculator className="w-3.5 h-3.5" />
          <span>Capacity Calculator</span>
        </button>

        <button
          onClick={() => setActiveTab('architecture')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'architecture'
              ? 'bg-teal-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Architecture Diagrams</span>
        </button>

        <button
          onClick={() => setActiveTab('memory')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
            activeTab === 'memory'
              ? 'bg-purple-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Brain className="w-3.5 h-3.5" />
          <span>User Memory</span>
        </button>
      </nav>

      {/* Right: Active Persona Pill & System Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs">
          {current.icon}
          <span className="font-medium text-slate-200">{current.name}</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-mono text-[11px] text-emerald-400">ONLINE</span>
        </div>
      </div>
    </header>
  );
};
