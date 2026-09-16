import React, { useState } from 'react';
import { api } from '../../services/api';
import {
  Calculator,
  HardDrive,
  Activity,
  Zap,
  Clock,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';

export const CalculatorView: React.FC = () => {
  const [activeCalc, setActiveCalc] = useState<'qps' | 'storage' | 'bandwidth' | 'cache' | 'latency'>('qps');
  const [result, setResult] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Form states
  const [qpsParams, setQpsParams] = useState({
    daily_active_users: 100000,
    actions_per_user_day: 50,
    peak_multiplier: 2.5,
    read_ratio: 0.8,
  });

  const [storageParams, setStorageParams] = useState({
    daily_records: 1000000,
    average_record_size_bytes: 500,
    retention_years: 3,
    indexing_overhead_percent: 25,
    replication_factor: 3,
  });

  const [bandwidthParams, setBandwidthParams] = useState({
    peak_qps: 1500,
    average_request_payload_bytes: 1024,
    average_response_payload_bytes: 8192,
  });

  const [cacheParams, setCacheParams] = useState({
    daily_read_requests: 10000000,
    average_cached_object_size_bytes: 2048,
    working_set_percentage: 20,
    headroom_multiplier: 1.3,
  });

  const [latencyParams, setLatencyParams] = useState({
    target_sla_ms: 200,
    network_rtt_ms: 35,
    gateway_proxy_ms: 10,
    cache_hit_rate: 0.85,
    cache_latency_ms: 2,
    db_query_latency_ms: 20,
    db_queries_per_request: 2,
  });

  const runCalculation = async () => {
    setIsLoading(true);
    setResult(null);
    try {
      let params = {};
      if (activeCalc === 'qps') params = qpsParams;
      else if (activeCalc === 'storage') params = storageParams;
      else if (activeCalc === 'bandwidth') params = bandwidthParams;
      else if (activeCalc === 'cache') params = cacheParams;
      else if (activeCalc === 'latency') params = latencyParams;

      const res = await api.calculate(activeCalc, params);
      setResult(res.result);
    } catch (err) {
      console.error('Calculation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Deterministic Engineering Calculator
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
              PYTHON DETERMINISTIC MATH
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Pure mathematical modeling for distributed systems capacity planning without LLM arithmetic guesswork.
          </p>
        </div>
      </div>

      {/* Tool Selector Tabs */}
      <div className="flex flex-wrap gap-2 p-1.5 rounded-2xl glass-panel border border-white/10">
        <button
          onClick={() => { setActiveCalc('qps'); setResult(null); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeCalc === 'qps'
              ? 'bg-emerald-600 text-white shadow-glow-emerald'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Activity className="w-4 h-4" />
          <span>QPS & Throughput</span>
        </button>

        <button
          onClick={() => { setActiveCalc('storage'); setResult(null); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeCalc === 'storage'
              ? 'bg-emerald-600 text-white shadow-glow-emerald'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <HardDrive className="w-4 h-4" />
          <span>Storage & Retention</span>
        </button>

        <button
          onClick={() => { setActiveCalc('bandwidth'); setResult(null); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeCalc === 'bandwidth'
              ? 'bg-emerald-600 text-white shadow-glow-emerald'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>Network Bandwidth</span>
        </button>

        <button
          onClick={() => { setActiveCalc('cache'); setResult(null); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeCalc === 'cache'
              ? 'bg-emerald-600 text-white shadow-glow-emerald'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Calculator className="w-4 h-4" />
          <span>Cache Pareto Sizing</span>
        </button>

        <button
          onClick={() => { setActiveCalc('latency'); setResult(null); }}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeCalc === 'latency'
              ? 'bg-emerald-600 text-white shadow-glow-emerald'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Latency Budget & SLA</span>
        </button>
      </div>

      {/* Calculator Body Grid: Form Inputs Left, Verified Output Right */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Form Inputs Panel */}
        <div className="p-5 rounded-2xl glass-panel border border-white/10 space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-emerald-400" />
            Parameter Inputs
          </h3>

          {/* QPS Form */}
          {activeCalc === 'qps' && (
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Daily Active Users (DAU)</label>
                <input
                  type="number"
                  value={qpsParams.daily_active_users}
                  onChange={(e) => setQpsParams({ ...qpsParams, daily_active_users: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Actions per User per Day</label>
                <input
                  type="number"
                  value={qpsParams.actions_per_user_day}
                  onChange={(e) => setQpsParams({ ...qpsParams, actions_per_user_day: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Peak Multiplier (x)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={qpsParams.peak_multiplier}
                    onChange={(e) => setQpsParams({ ...qpsParams, peak_multiplier: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Read Ratio (0.0 - 1.0)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={qpsParams.read_ratio}
                    onChange={(e) => setQpsParams({ ...qpsParams, read_ratio: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Storage Form */}
          {activeCalc === 'storage' && (
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Daily New Records</label>
                <input
                  type="number"
                  value={storageParams.daily_records}
                  onChange={(e) => setStorageParams({ ...storageParams, daily_records: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Average Record Size (Bytes)</label>
                <input
                  type="number"
                  value={storageParams.average_record_size_bytes}
                  onChange={(e) => setStorageParams({ ...storageParams, average_record_size_bytes: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Retention (Yrs)</label>
                  <input
                    type="number"
                    value={storageParams.retention_years}
                    onChange={(e) => setStorageParams({ ...storageParams, retention_years: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Index %</label>
                  <input
                    type="number"
                    value={storageParams.indexing_overhead_percent}
                    onChange={(e) => setStorageParams({ ...storageParams, indexing_overhead_percent: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Replicas</label>
                  <input
                    type="number"
                    value={storageParams.replication_factor}
                    onChange={(e) => setStorageParams({ ...storageParams, replication_factor: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Bandwidth Form */}
          {activeCalc === 'bandwidth' && (
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Peak QPS</label>
                <input
                  type="number"
                  value={bandwidthParams.peak_qps}
                  onChange={(e) => setBandwidthParams({ ...bandwidthParams, peak_qps: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Avg Request (Bytes)</label>
                  <input
                    type="number"
                    value={bandwidthParams.average_request_payload_bytes}
                    onChange={(e) => setBandwidthParams({ ...bandwidthParams, average_request_payload_bytes: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Avg Response (Bytes)</label>
                  <input
                    type="number"
                    value={bandwidthParams.average_response_payload_bytes}
                    onChange={(e) => setBandwidthParams({ ...bandwidthParams, average_response_payload_bytes: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Cache Form */}
          {activeCalc === 'cache' && (
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Daily Read Requests</label>
                <input
                  type="number"
                  value={cacheParams.daily_read_requests}
                  onChange={(e) => setCacheParams({ ...cacheParams, daily_read_requests: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Cached Object Size (Bytes)</label>
                <input
                  type="number"
                  value={cacheParams.average_cached_object_size_bytes}
                  onChange={(e) => setCacheParams({ ...cacheParams, average_cached_object_size_bytes: Number(e.target.value) })}
                  className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Working Set % (Pareto)</label>
                  <input
                    type="number"
                    value={cacheParams.working_set_percentage}
                    onChange={(e) => setCacheParams({ ...cacheParams, working_set_percentage: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Safety Headroom (x)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={cacheParams.headroom_multiplier}
                    onChange={(e) => setCacheParams({ ...cacheParams, headroom_multiplier: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Latency Form */}
          {activeCalc === 'latency' && (
            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Target SLA (ms)</label>
                  <input
                    type="number"
                    value={latencyParams.target_sla_ms}
                    onChange={(e) => setLatencyParams({ ...latencyParams, target_sla_ms: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Network RTT (ms)</label>
                  <input
                    type="number"
                    value={latencyParams.network_rtt_ms}
                    onChange={(e) => setLatencyParams({ ...latencyParams, network_rtt_ms: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-400 block mb-1">Cache Hit Rate (0.0-1.0)</label>
                  <input
                    type="number"
                    step="0.05"
                    value={latencyParams.cache_hit_rate}
                    onChange={(e) => setLatencyParams({ ...latencyParams, cache_hit_rate: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">DB Read Latency (ms)</label>
                  <input
                    type="number"
                    value={latencyParams.db_query_latency_ms}
                    onChange={(e) => setLatencyParams({ ...latencyParams, db_query_latency_ms: Number(e.target.value) })}
                    className="w-full glass-input p-2.5 rounded-xl text-white font-mono"
                  />
                </div>
              </div>
            </div>
          )}

          <button
            onClick={runCalculation}
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-glow-emerald transition active:scale-95 flex items-center justify-center gap-2"
          >
            {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            <span>Calculate Deterministic Metrics</span>
          </button>
        </div>

        {/* Results Panel */}
        <div className="p-5 rounded-2xl glass-panel border border-white/10 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2 mb-4">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Verified Calculations Output
            </h3>

            {!result ? (
              <div className="h-48 flex items-center justify-center text-xs text-slate-500 italic text-center">
                Configure parameters and click calculate to execute Python mathematical models.
              </div>
            ) : (
              <div className="space-y-3 font-mono text-xs">
                {Object.entries(result).map(([k, v]) => (
                  <div key={k} className="flex justify-between items-center p-2.5 rounded-xl bg-surface-raised/40 border border-white/5">
                    <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                    <span className="font-bold text-emerald-300 text-sm">{String(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-slate-400">
            <strong>Engineering Rule:</strong> Numerical results are executed via deterministic Python arithmetic (`app.tools.calculator`), guaranteeing zero LLM hallucination.
          </div>
        </div>
      </div>
    </div>
  );
};
