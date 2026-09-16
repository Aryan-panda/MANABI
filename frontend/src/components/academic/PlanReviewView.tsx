import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { StudentProfile, AttendanceRecord } from '../../types';
import {
  GraduationCap,
  AlertTriangle,
  CheckCircle2,
  Clock,
  BookOpen,
  ArrowRight,
  RefreshCw,
  Award,
} from 'lucide-react';

export const PlanReviewView: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [rawPlan, setRawPlan] = useState<string>(
    `Proposed 6th Semester Plan:
1. CS301: Distributed Systems (4 credits)
2. CS304: Database Internals & Storage Engines (4 credits)
3. CS308: Machine Learning Systems (3 credits)
4. CS401: Advanced Distributed Computing (4 credits)
5. HS301: Engineering Ethics & Professional Practice (2 credits)
Total requested credits: 17 credits`
  );
  const [reviewResult, setReviewResult] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStudent = async () => {
      try {
        const p = await api.getStudentProfile('STU1001');
        setProfile(p);
        const a = await api.getAttendance('STU1001');
        setAttendance(a);
      } catch (err: any) {
        console.error('Failed to load SIS data:', err);
      }
    };
    fetchStudent();
  }, []);

  const handleReview = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.reviewPlan(rawPlan, 'STU1001');
      setReviewResult(result);
    } catch (err: any) {
      setError(err.message || 'Plan review failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header Banner */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-white tracking-tight">
              Academic Degree Plan Reviewer
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-semibold border border-blue-500/30">
              LANGGRAPH STATEFUL ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Automated multi-step graph: prerequisite analysis, workload estimation, risk identification, and plan optimization.
          </p>
        </div>
      </div>

      {/* Top Grid: Student Profile Card & Attendance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Profile Card */}
        <div className="p-4 rounded-2xl glass-panel border border-white/10 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">{profile?.full_name || 'Aryan Panda'}</h3>
              <p className="text-xs text-slate-400">{profile?.student_id || 'STU1001'}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 text-xs">
            <div>
              <span className="text-slate-500 block text-[11px]">Program</span>
              <span className="text-slate-200 font-medium truncate block">B.Tech CSE</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[11px]">Cumulative GPA</span>
              <span className="text-emerald-400 font-bold">{profile?.cgpa || 8.85} / 10.0</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[11px]">Credits Completed</span>
              <span className="text-slate-200">{profile?.credits_earned || 124} / 160</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[11px]">Academic Standing</span>
              <span className="text-blue-400 font-medium">{profile?.academic_status || 'Good Standing'}</span>
            </div>
          </div>
        </div>

        {/* Live Attendance Warnings */}
        <div className="md:col-span-2 p-4 rounded-2xl glass-panel border border-white/10 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              Live Course Attendance (Threshold: 75%)
            </h4>
            <span className="text-[10px] text-slate-500">Official SIS Registry</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            {attendance.map((att) => (
              <div
                key={att.course_code}
                className={`p-2.5 rounded-xl border flex items-center justify-between text-xs ${
                  att.is_critical
                    ? 'border-amber-500/40 bg-amber-500/10 text-amber-200'
                    : 'border-white/5 bg-surface-raised/40 text-slate-300'
                }`}
              >
                <div>
                  <span className="font-mono font-bold block">{att.course_code}</span>
                  <span className="text-[11px] text-slate-400 truncate block max-w-[180px]">
                    {att.course_name}
                  </span>
                </div>
                <div className="text-right">
                  <span className={`font-bold font-mono ${att.is_critical ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {att.percentage.toFixed(1)}%
                  </span>
                  {att.is_critical && (
                    <span className="text-[10px] block text-amber-400 font-semibold">BORDERLINE</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Plan Input & LangGraph Review Action */}
      <div className="p-5 rounded-2xl glass-panel border border-white/10 space-y-4">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Proposed Semester Academic Plan
          </label>
          <textarea
            value={rawPlan}
            onChange={(e) => setRawPlan(e.target.value)}
            rows={5}
            className="w-full rounded-xl glass-input p-3 text-xs text-white font-mono placeholder-slate-500 focus:outline-none"
            placeholder="List courses, credit values, and intended study targets..."
          />
        </div>

        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Triggers LangGraph nodes: <code className="text-indigo-300">prerequisite_analysis</code> → <code className="text-indigo-300">workload_analysis</code> → <code className="text-indigo-300">risk_identification</code> → <code className="text-indigo-300">revised_plan</code>
          </p>
          <button
            onClick={handleReview}
            disabled={isLoading || !rawPlan.trim()}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium text-xs shadow-glow transition active:scale-95"
          >
            {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            <span>Run LangGraph Review</span>
          </button>
        </div>
      </div>

      {/* Review Output Section */}
      {reviewResult && (
        <div className="space-y-4 animate-in fade-in duration-300">
          {/* Status Banner */}
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              reviewResult.is_valid
                ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
            }`}
          >
            <div className="flex items-center gap-3">
              {reviewResult.is_valid ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-amber-400" />
              )}
              <div>
                <h4 className="text-sm font-bold">{reviewResult.summary}</h4>
                <p className="text-xs opacity-80">
                  {reviewResult.is_valid
                    ? 'All prerequisites satisfied and credits within policy guidelines.'
                    : 'Discrepancies identified; review actionable recommendations below.'}
                </p>
              </div>
            </div>
          </div>

          {/* Cards Grid: Prerequisites, Workload, Risks */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Prereq Issues */}
            <div className="p-4 rounded-xl glass-panel border border-white/10 space-y-2">
              <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-blue-400" />
                Prerequisites Check
              </h5>
              {reviewResult.prerequisite_issues?.length === 0 ? (
                <p className="text-xs text-emerald-400 font-medium">✓ All course prerequisites met</p>
              ) : (
                <div className="space-y-2">
                  {reviewResult.prerequisite_issues?.map((iss: any, i: number) => (
                    <div key={i} className="p-2 rounded-lg bg-red-950/30 border border-red-800/40 text-[11px] text-red-300">
                      <span className="font-bold block">{iss.course}</span>
                      <span>{iss.recommendation}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Workload */}
            <div className="p-4 rounded-xl glass-panel border border-white/10 space-y-2">
              <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-emerald-400" />
                Workload Load Analysis
              </h5>
              <div className="space-y-1 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-500">Total Credits:</span>
                  <span className="font-bold">{reviewResult.workload_analysis?.total_credits}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Workload Status:</span>
                  <span className="font-bold text-emerald-400">{reviewResult.workload_analysis?.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Weekly Study Hours:</span>
                  <span>{reviewResult.workload_analysis?.estimated_weekly_study_hours} hrs</span>
                </div>
              </div>
            </div>

            {/* Identified Risks */}
            <div className="p-4 rounded-xl glass-panel border border-white/10 space-y-2">
              <h5 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Risk Factor Scorecard
              </h5>
              {reviewResult.risk_factors?.length === 0 ? (
                <p className="text-xs text-emerald-400 font-medium">✓ Zero high-severity risks identified</p>
              ) : (
                <div className="space-y-1.5">
                  {reviewResult.risk_factors?.map((risk: any, i: number) => (
                    <div key={i} className="p-2 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300">
                      <span className="font-bold block">[{risk.severity}] {risk.type}</span>
                      <span>{risk.description}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Full Revised Plan Synthesis */}
          <div className="p-5 rounded-2xl glass-panel border border-white/10 markdown-body text-xs leading-relaxed">
            <h4 className="text-sm font-bold text-white mb-2 pb-1 border-b border-white/10">
              LangGraph Synthesized Academic Report
            </h4>
            <div className="whitespace-pre-wrap text-slate-300">
              {reviewResult.revised_plan}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
