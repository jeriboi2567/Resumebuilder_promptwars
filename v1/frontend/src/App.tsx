import React, { useState, useEffect } from 'react';
import {
  SampleCandidateSummary, PipelineRunResult, CandidateProfile
} from './types';
import { PipelineStepper } from './components/PipelineStepper';
import { ProfileView } from './components/ProfileView';
import { OpinionCardGrid } from './components/OpinionCard';
import { DebateThread } from './components/DebateThread';
import { FinalDecisionCard } from './components/FinalDecisionCard';
import { FinalReport } from './components/FinalReport';
import {
  Users, Play, History, Loader2, Sparkles, RefreshCw, Cpu, Layers, CheckCircle2, ShieldAlert
} from 'lucide-react';

export default function App() {
  const [candidates, setCandidates] = useState<SampleCandidateSummary[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('cand_1');
  const [currentStage, setCurrentStage] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [runResult, setRunResult] = useState<PipelineRunResult | null>(null);
  const [pastRuns, setPastRuns] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load sample candidates and past runs on mount
  useEffect(() => {
    fetchCandidates();
    fetchPastRuns();
  }, []);

  // Auto-run evaluation when switching candidates for quick demo
  useEffect(() => {
    if (selectedCandidateId) {
      handleRunEvaluation(selectedCandidateId);
    }
  }, [selectedCandidateId]);

  const fetchCandidates = async () => {
    try {
      const res = await fetch('/api/candidates');
      if (res.ok) {
        const data = await res.json();
        setCandidates(data);
      }
    } catch (err) {
      console.error('Failed to fetch candidates:', err);
    }
  };

  const fetchPastRuns = async () => {
    try {
      const res = await fetch('/api/runs');
      if (res.ok) {
        const data = await res.json();
        setPastRuns(data);
      }
    } catch (err) {
      console.error('Failed to fetch past runs:', err);
    }
  };

  const handleRunEvaluation = async (candId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candId })
      });
      if (!res.ok) {
        throw new Error(`Evaluation failed with status ${res.status}`);
      }
      const data: PipelineRunResult = await res.json();
      setRunResult(data);
      fetchPastRuns();
    } catch (err: any) {
      setError(err.message || 'Error running evaluation pipeline');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPastRun = async (runId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/runs/${runId}`);
      if (res.ok) {
        const data = await res.json();
        setRunResult(data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch run details');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 pb-16 font-sans">
      {/* Top Navigation Header */}
      <header className="bg-slate-800/90 backdrop-blur border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl text-white shadow-md">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-white tracking-tight flex items-center gap-2">
                Multi-Agent Candidate Evaluation System
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30">
                  Strict Isolation & Debate Pipeline
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                4 Isolated Personas • Multi-Turn Debate • Weighted Judge Synthesis
              </p>
            </div>
          </div>

          {/* Sample Candidate Switcher */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
              <Users className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-400 hidden sm:inline">Select Candidate:</span>
              <select
                value={selectedCandidateId}
                onChange={(e) => setSelectedCandidateId(e.target.value)}
                className="bg-transparent text-white font-semibold focus:outline-none cursor-pointer"
              >
                {candidates.map((c) => (
                  <option key={c.id} value={c.id} className="bg-slate-800 text-white">
                    {c.name} ({c.role})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={() => handleRunEvaluation(selectedCandidateId)}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition-all shadow-md"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Executing Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Run Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 pt-6 space-y-6">
        {/* Pipeline Stepper Navigation */}
        <PipelineStepper currentStage={currentStage} onSelectStage={setCurrentStage} />

        {/* Error Alert */}
        {error && (
          <div className="bg-rose-950/60 border border-rose-500/50 rounded-xl p-4 text-xs text-rose-200 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Loading Overlay */}
        {loading ? (
          <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-16 text-center space-y-4 backdrop-blur my-8">
            <Loader2 className="w-12 h-12 text-indigo-400 animate-spin mx-auto" />
            <h3 className="text-xl font-bold text-white">Running Multi-Agent Deliberation Pipeline...</h3>
            <div className="max-w-md mx-auto space-y-2 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>[1] Extracting Structured Candidate Profile...</span>
                <span className="text-emerald-400 font-mono">Done</span>
              </div>
              <div className="flex justify-between">
                <span>[2] Running 4 Isolated Agent Personas...</span>
                <span className="text-emerald-400 font-mono">In Progress</span>
              </div>
              <div className="flex justify-between">
                <span>[3] Orchestrating Multi-Turn Debate & Stance Shift...</span>
                <span className="text-slate-500 font-mono">Pending</span>
              </div>
              <div className="flex justify-between">
                <span>[4] Synthesizing Final Recommendation (Judge)...</span>
                <span className="text-slate-500 font-mono">Pending</span>
              </div>
            </div>
          </div>
        ) : runResult ? (
          /* Active Stage Content View */
          <div>
            {currentStage === 1 && <ProfileView profile={runResult.profile} />}
            {currentStage === 2 && (
              <OpinionCardGrid independentOpinions={runResult.independent_opinions} />
            )}
            {currentStage === 3 && <DebateThread debateState={runResult.debate_state} />}
            {currentStage === 4 && <FinalDecisionCard decision={runResult.final_decision} />}
            {currentStage === 5 && <FinalReport report={runResult.report} />}
          </div>
        ) : (
          <div className="text-center py-16 text-slate-400 text-sm">
            Select a candidate and click "Run Pipeline" to start evaluation.
          </div>
        )}

        {/* Past Runs History Drawer */}
        {pastRuns.length > 0 && (
          <div className="bg-slate-800/70 border border-slate-700/80 rounded-xl p-5 shadow-md mt-12 space-y-3">
            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-400" />
              Persisted Run History ({pastRuns.length} runs saved)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {pastRuns.map((r) => (
                <button
                  key={r.run_id}
                  onClick={() => handleSelectPastRun(r.run_id)}
                  className="bg-slate-900 hover:bg-slate-800 border border-slate-700 p-3 rounded-lg text-left text-xs space-y-1 transition-all"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-white">{r.candidate_name}</span>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-500/30">
                      {r.final_recommendation}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 truncate">{r.role_applied}</div>
                  <div className="text-[10px] text-slate-500 font-mono">{r.run_id}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
