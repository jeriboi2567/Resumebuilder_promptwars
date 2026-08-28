import React, { useState, useEffect } from 'react';
import {
  HiringRoleV3, PipelineRunResultV2
} from './types';
import { ElevenLabsAudioPlayer } from './components/ElevenLabsAudioPlayer';
import { Stage6ComparisonView } from './components/Stage6ComparisonView';
import { Stage3DebateThread } from './components/Stage3DebateThread';
import { Stage2AgentOpinions } from './components/Stage2AgentOpinions';
import { RoleUploaderModal } from './components/RoleUploaderModal';
import {
  Users, Upload, Layers, Loader2, Cpu, ShieldAlert, Briefcase, Plus
} from 'lucide-react';

export default function App() {
  const [viewMode, setViewMode] = useState<'individual' | 'comparison'>('comparison');
  const [rolesList, setRolesList] = useState<Array<{ role_id: string; title: string; company: string }>>([]);
  const [activeRole, setActiveRole] = useState<HiringRoleV3 | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    runSampleBatch();
  }, []);

  const runSampleBatch = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/sample-batch');
      if (!res.ok) {
        throw new Error(`Sample batch failed with status ${res.status}`);
      }
      const data = await res.json();
      // Format into HiringRoleV3 object for display
      const mockRole: HiringRoleV3 = {
        role_id: "role_cargonet_ai",
        job_description: data.job_description,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        candidate_results: data.candidate_results,
        stage6_comparison: data.stage6_comparison
      };
      setActiveRole(mockRole);
      setRolesList([{
        role_id: mockRole.role_id,
        title: mockRole.job_description.title,
        company: mockRole.job_description.company
      }]);
      if (Object.keys(data.candidate_results).length > 0) {
        setSelectedCandidateId(Object.keys(data.candidate_results)[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Error executing sample batch pipeline');
    } finally {
      setLoading(false);
    }
  };

  const fetchRoleDetails = async (roleId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/roles/${roleId}`);
      if (!res.ok) throw new Error("Failed to fetch role details.");
      const data: HiringRoleV3 = await res.json();
      setActiveRole(data);
      if (Object.keys(data.candidate_results).length > 0) {
        setSelectedCandidateId(Object.keys(data.candidate_results)[0]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const activeCandidateResult: PipelineRunResultV2 | undefined =
    activeRole?.candidate_results[selectedCandidateId];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 pb-16 font-sans">
      {/* Top Header Navigation */}
      <header className="bg-slate-800/90 backdrop-blur border-b border-slate-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-600 rounded-xl text-white shadow-md">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-white tracking-tight flex items-center gap-2">
                Multi-Agent Candidate Evaluation Platform V3
                <span className="text-[10px] bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-2.5 py-0.5 rounded-full font-bold font-mono shadow-sm">
                  V3 General Purpose
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                General-Purpose Employer Hiring Platform • Arbitrary Job Descriptions & Accumulated Candidate Batches
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-700">
              <button
                onClick={() => setViewMode('comparison')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-bold transition-all ${
                  viewMode === 'comparison'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Compare Candidates (Stage 6)</span>
              </button>

              <button
                onClick={() => setViewMode('individual')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-bold transition-all ${
                  viewMode === 'individual'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Individual Deep-Dive (5-Stage)</span>
              </button>
            </div>

            <button
              onClick={() => setIsUploadOpen(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold shadow-md"
            >
              <Plus className="w-4 h-4" />
              <span>Create Role / Add Candidate</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 pt-6 space-y-8">
        {error && (
          <div className="bg-rose-950/60 border border-rose-500/50 rounded-xl p-4 text-xs text-rose-200 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-16 text-center space-y-4 backdrop-blur my-8">
            <Loader2 className="w-12 h-12 text-indigo-400 animate-spin mx-auto" />
            <h3 className="text-xl font-bold text-white">Evaluating Candidate & Updating Stage 6 Comparison...</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Running 5-stage pipeline, inspecting verified quotes, checking insufficient evidence rules, and ranking accumulated candidates.
            </p>
          </div>
        ) : activeRole ? (
          <div>
            {viewMode === 'comparison' && activeRole.stage6_comparison && (
              <Stage6ComparisonView
                comparison={activeRole.stage6_comparison}
                jobDescription={activeRole.job_description}
              />
            )}

            {viewMode === 'individual' && (
              <div className="space-y-6">
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex justify-between items-center gap-4">
                  <div className="flex items-center space-x-3">
                    <Users className="w-5 h-5 text-indigo-400" />
                    <span className="text-sm font-bold text-white">Select Candidate for Deep-Dive:</span>
                    <select
                      value={selectedCandidateId}
                      onChange={(e) => setSelectedCandidateId(e.target.value)}
                      className="bg-slate-900 border border-slate-700 text-white font-semibold text-xs px-3 py-2 rounded-lg cursor-pointer"
                    >
                      {Object.values(activeRole.candidate_results).map((res) => (
                        <option key={res.profile.candidate_id} value={res.profile.candidate_id}>
                          {res.profile.candidate_name} ({res.final_decision.recommendation})
                        </option>
                      ))}
                    </select>
                  </div>

                  {activeCandidateResult && (
                    <div className="text-xs text-slate-400 font-mono">
                      Candidate ID: <span className="text-slate-200">{activeCandidateResult.profile.candidate_id}</span>
                    </div>
                  )}
                </div>

                {activeCandidateResult && (
                  <div className="space-y-6">
                    <ElevenLabsAudioPlayer
                      audioUrl={activeCandidateResult.audio_url}
                      turns={activeCandidateResult.debate_state.turns}
                    />

                    <Stage2AgentOpinions
                      opinions={activeCandidateResult.independent_opinions}
                    />

                    <Stage3DebateThread
                      debateState={activeCandidateResult.debate_state}
                    />

                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6">
                      <div className="border-b border-slate-700 pb-4 flex justify-between items-start">
                        <div>
                          <h2 className="text-2xl font-bold text-white">{activeCandidateResult.profile.candidate_name}</h2>
                          <p className="text-xs text-slate-400">{activeCandidateResult.profile.role_applied}</p>
                        </div>
                        <span className="text-sm font-bold px-3 py-1 bg-emerald-600 text-white rounded-full">
                          {activeCandidateResult.final_decision.recommendation}
                        </span>
                      </div>

                      <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl space-y-3">
                        <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                          Section B: Not Assessed / Insufficient Evidence (No-Guessing Rule)
                        </h4>
                        {activeCandidateResult.report.not_assessed_dimensions.length > 0 ? (
                          <ul className="space-y-2">
                            {activeCandidateResult.report.not_assessed_dimensions.map((na, idx) => (
                              <li key={idx} className="text-xs text-slate-300 flex items-start gap-2 bg-slate-800/80 p-2.5 rounded border border-slate-700">
                                <span className="text-amber-400 font-bold">•</span>
                                <div>
                                  <strong className="text-indigo-300">[{na.agent}] {na.dimension}:</strong> {na.reason}
                                </div>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div className="text-xs text-emerald-300">All JD evaluation dimensions had sufficient source evidence.</div>
                        )}
                      </div>

                      <div className="space-y-2">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Decision Rationale:</h4>
                        <p className="text-xs text-slate-200 leading-relaxed bg-slate-900/80 p-4 rounded-lg border border-slate-700">
                          {activeCandidateResult.final_decision.decision_rationale}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-16 text-slate-400">Loading Hiring Role platform...</div>
        )}

        <RoleUploaderModal
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          roles={rolesList}
          activeRoleId={activeRole?.role_id}
          onRoleUpdated={(role) => {
            setActiveRole(role);
            if (!rolesList.some(r => r.role_id === role.role_id)) {
              setRolesList([...rolesList, {
                role_id: role.role_id,
                title: role.job_description.title,
                company: role.job_description.company
              }]);
            }
            if (Object.keys(role.candidate_results).length > 0) {
              setSelectedCandidateId(Object.keys(role.candidate_results)[0]);
            }
          }}
        />
      </main>
    </div>
  );
}
