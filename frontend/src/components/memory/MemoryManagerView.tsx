import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { MemoryItem } from '../../types';
import { Brain, Plus, Trash2, ShieldCheck, RefreshCw, Sparkles } from 'lucide-react';

export const MemoryManagerView: React.FC = () => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [keyInput, setKeyInput] = useState('');
  const [valInput, setValInput] = useState('');
  const [typeInput, setTypeInput] = useState('preference');
  const [isLoading, setIsLoading] = useState(false);

  const fetchMemories = async () => {
    setIsLoading(true);
    try {
      const data = await api.getMemories();
      setMemories(data);
    } catch (err) {
      console.error('Failed to fetch memories:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyInput.trim() || !valInput.trim()) return;
    try {
      const newMem = await api.addMemory(keyInput.trim(), valInput.trim(), typeInput);
      setMemories([newMem, ...memories]);
      setKeyInput('');
      setValInput('');
    } catch (err) {
      console.error('Failed to save memory:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteMemory(id);
      setMemories(memories.filter((m) => m.id !== id));
    } catch (err) {
      console.error('Failed to delete memory:', err);
    }
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Evidence-Based User Memory Engine
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-semibold border border-purple-500/30">
              DURABLE POSTGRESQL STATE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Section 24 Compliance: Memories require evidence escalation before claiming high confidence. Fully user-correctable.
          </p>
        </div>
      </div>

      {/* Add Memory Form */}
      <form onSubmit={handleAdd} className="p-5 rounded-2xl glass-panel border border-white/10 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Plus className="w-4 h-4 text-purple-400" />
          Record Explicit Preference or Verified Skill
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="text-slate-400 block mb-1">Type</label>
            <select
              value={typeInput}
              onChange={(e) => setTypeInput(e.target.value)}
              className="w-full glass-input p-2.5 rounded-xl text-white font-mono bg-surface"
            >
              <option value="preference">Preference</option>
              <option value="skill">Skill Proficiency</option>
              <option value="goal">Academic/Career Goal</option>
              <option value="academic_fact">Academic Fact</option>
            </select>
          </div>
          <div>
            <label className="text-slate-400 block mb-1">Key Name</label>
            <input
              type="text"
              placeholder="e.g. java_proficiency"
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
            />
          </div>
          <div>
            <label className="text-slate-400 block mb-1">Recorded Value</label>
            <input
              type="text"
              placeholder="e.g. intermediate"
              value={valInput}
              onChange={(e) => setValInput(e.target.value)}
              className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
            />
          </div>
        </div>

        <div className="flex justify-end pt-1">
          <button
            type="submit"
            disabled={!keyInput.trim() || !valInput.trim()}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white font-medium text-xs shadow-glow transition active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>Store Memory</span>
          </button>
        </div>
      </form>

      {/* Memory List */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs uppercase font-semibold tracking-wider text-slate-400 flex items-center gap-1.5">
            <Brain className="w-3.5 h-3.5 text-purple-400" />
            Stored User Memory Records ({memories.length})
          </span>
          <button
            onClick={fetchMemories}
            className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition"
          >
            <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {memories.length === 0 ? (
          <div className="p-8 rounded-2xl glass-panel border border-white/10 text-center text-xs text-slate-500 italic">
            No memories recorded yet. Record skills or engage with agents to accumulate evidence.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {memories.map((m) => (
              <div
                key={m.id}
                className="p-4 rounded-xl border border-white/10 glass-panel flex items-start justify-between gap-3 hover:border-purple-500/40 transition"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 border border-white/10 uppercase text-slate-400">
                      {m.type}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-semibold uppercase ${
                        m.confidence === 'high'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : m.confidence === 'medium'
                          ? 'bg-blue-500/20 text-blue-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
                      {m.confidence} Confidence
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-white font-mono">{m.key}</h4>
                  <p className="text-xs text-slate-300 font-medium">{m.value}</p>

                  <div className="text-[10px] text-slate-500 pt-1">
                    Evidence count: {m.evidence_count} observation(s)
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(m.id)}
                  className="p-1.5 rounded-lg hover:bg-red-500/10 text-slate-500 hover:text-red-400 transition"
                  title="Remove memory"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
