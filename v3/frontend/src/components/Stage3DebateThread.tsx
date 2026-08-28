import React from 'react';
import { DebateState } from '../types';
import { MessageSquare, ArrowRight, Quote, RefreshCw, CheckCircle2 } from 'lucide-react';

interface Stage3DebateThreadProps {
  debateState: DebateState;
}

export const Stage3DebateThread: React.FC<Stage3DebateThreadProps> = ({ debateState }) => {
  const getAgentColor = (agentName: string) => {
    switch (agentName) {
      case 'Technical Agent':
        return { bg: 'bg-blue-950/60', border: 'border-blue-500/40', text: 'text-blue-400' };
      case 'HR / Culture Agent':
        return { bg: 'bg-emerald-950/60', border: 'border-emerald-500/40', text: 'text-emerald-400' };
      case 'Hiring Manager Agent':
        return { bg: 'bg-purple-950/60', border: 'border-purple-500/40', text: 'text-purple-400' };
      case 'Skeptic Agent':
        return { bg: 'bg-rose-950/60', border: 'border-rose-500/40', text: 'text-rose-400' };
      default:
        return { bg: 'bg-slate-800', border: 'border-slate-700', text: 'text-slate-300' };
    }
  };

  const getStanceBadge = (stance: string) => {
    switch (stance) {
      case 'Agree':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'Reinforce':
        return 'bg-teal-500/20 text-teal-300 border-teal-500/40';
      case 'Disagree':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'Revise':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-extrabold animate-pulse';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="space-y-6 bg-slate-800/90 border border-slate-700 rounded-xl p-6 shadow-xl">
      <div className="border-b border-slate-700 pb-4 flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-600/30 text-indigo-400 rounded-xl border border-indigo-500/30">
            <MessageSquare className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              Stage 3: Structured Multi-Turn Deliberation & Debate Transcript
            </h3>
            <p className="text-xs text-slate-400">
              Interactive multi-turn debate across isolated agent personas with explicit stance deltas and citations.
            </p>
          </div>
        </div>
        <div className="bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-lg text-xs text-slate-300 font-mono">
          Rounds Executed: <strong className="text-indigo-400">{debateState.rounds}</strong>
        </div>
      </div>

      {/* Stance Delta Summary Table */}
      <div className="bg-slate-900/90 border border-slate-700/80 rounded-xl p-4 space-y-3">
        <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-amber-400" />
          Post-Debate Stance Deltas & Opinion Revisions
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800 text-slate-400 uppercase text-[10px] font-mono">
              <tr>
                <th className="p-2.5">Agent Persona</th>
                <th className="p-2.5">Initial Opinion</th>
                <th className="p-2.5">Post-Debate Opinion</th>
                <th className="p-2.5">Position Changed?</th>
                <th className="p-2.5">Key Deliberation Driver</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {Object.values(debateState.stance_deltas).map((delta) => (
                <tr key={delta.agent_name} className="hover:bg-slate-800/50">
                  <td className="p-2.5 font-bold text-white">{delta.agent_name}</td>
                  <td className="p-2.5">
                    <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-300 border border-slate-700">
                      {delta.verdict_before} ({delta.score_before ?? 'N/A'})
                    </span>
                  </td>
                  <td className="p-2.5">
                    <span
                      className={`px-2 py-0.5 rounded border font-bold ${
                        delta.changed
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                          : 'bg-slate-800 text-slate-200 border-slate-700'
                      }`}
                    >
                      {delta.verdict_after} ({delta.score_after ?? 'N/A'})
                    </span>
                  </td>
                  <td className="p-2.5 font-mono">
                    {delta.changed ? (
                      <span className="text-amber-400 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> YES (REVISED)
                      </span>
                    ) : (
                      <span className="text-slate-400">NO (FIRM)</span>
                    )}
                  </td>
                  <td className="p-2.5 text-slate-300 text-[11px] max-w-xs leading-snug">
                    {delta.change_reason}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Chronological Debate Turn Cards */}
      <div className="space-y-4 pt-2">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Turn-by-Turn Debate Dialogue Log:
        </h4>

        {debateState.turns.map((turn, index) => {
          const colors = getAgentColor(turn.agent_name);
          return (
            <div
              key={index}
              className={`p-4 rounded-xl border ${colors.bg} ${colors.border} space-y-3 relative shadow-md`}
            >
              <div className="flex flex-wrap justify-between items-center gap-2 border-b border-slate-700/60 pb-2.5">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] bg-slate-900/80 px-2 py-0.5 rounded text-slate-400 font-mono font-bold">
                    Round {turn.round_number}
                  </span>
                  <span className={`text-sm font-bold ${colors.text}`}>
                    {turn.agent_name}
                  </span>
                  <span className="text-xs text-slate-400 flex items-center gap-1">
                    <ArrowRight className="w-3 h-3 text-slate-500" /> responding to <strong className="text-slate-200">{turn.responding_to}</strong>
                  </span>
                </div>

                <span className={`text-xs font-bold px-3 py-0.5 rounded-full border ${getStanceBadge(turn.stance)}`}>
                  Stance: {turn.stance}
                </span>
              </div>

              <p className="text-xs text-slate-200 leading-relaxed font-sans pl-1">
                "{turn.message}"
              </p>

              {turn.cites_quote && (
                <div className="text-[11px] text-indigo-300 bg-slate-900/80 p-2 rounded-lg border border-slate-800 flex items-center space-x-2 font-mono">
                  <Quote className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span>Cited Evidence: <strong>{turn.cites_quote}</strong></span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
