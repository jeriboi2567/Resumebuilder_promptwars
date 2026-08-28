import React from 'react';
import { DebateState, DebateTurn, AgentStanceDelta } from '../types';
import { VoiceDebatePlayer } from './VoiceDebatePlayer';
import { MessageSquare, ArrowRight, RefreshCw, CheckCircle, AlertCircle, Quote } from 'lucide-react';

interface DebateThreadProps {
  debateState: DebateState;
}

export const DebateThread: React.FC<DebateThreadProps> = ({ debateState }) => {
  const getStanceBadge = (stance: string) => {
    switch (stance) {
      case 'Agree':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'Disagree':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'Revise':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'Reinforce':
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
      default:
        return 'bg-slate-700 text-slate-300';
    }
  };

  const getAgentAvatar = (name: string) => {
    if (name.includes('Technical')) return { bg: 'bg-cyan-600', letter: 'T' };
    if (name.includes('HR')) return { bg: 'bg-pink-600', letter: 'HR' };
    if (name.includes('Hiring Manager')) return { bg: 'bg-emerald-600', letter: 'HM' };
    return { bg: 'bg-amber-600', letter: 'S' };
  };

  const deltasList = Object.values(debateState.stance_deltas);

  return (
    <div className="space-y-8">
      {/* Audio Voice Debate Player */}
      <VoiceDebatePlayer turns={debateState.turns} />

      {/* Before / After Position Delta Tracker */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-lg space-y-4">
        <div className="flex justify-between items-center border-b border-slate-700 pb-3">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-indigo-400" />
            Agent Position Movement (Before vs. After Debate)
          </h3>
          <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-full border border-indigo-500/30">
            Provable Debate Delta
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {deltasList.map((delta: AgentStanceDelta) => (
            <div
              key={delta.agent_name}
              className={`bg-slate-900 border rounded-lg p-3.5 space-y-2 text-xs transition-all ${
                delta.changed
                  ? 'border-purple-500/60 ring-1 ring-purple-500/30 shadow-purple-900/10'
                  : 'border-slate-700/80'
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-bold text-white">{delta.agent_name}</span>
                {delta.changed ? (
                  <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded font-semibold border border-purple-500/40 animate-pulse">
                    Position Shifted
                  </span>
                ) : (
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                    Held Firm
                  </span>
                )}
              </div>

              {/* Score Shift Bar */}
              <div className="flex items-center justify-between bg-slate-800/80 p-2 rounded border border-slate-700/60">
                <div className="text-center">
                  <div className="text-[10px] text-slate-400">Before</div>
                  <div className="font-mono font-bold text-slate-200">{delta.score_before.toFixed(1)}</div>
                </div>
                <ArrowRight className="w-4 h-4 text-indigo-400" />
                <div className="text-center">
                  <div className="text-[10px] text-slate-400">After</div>
                  <div
                    className={`font-mono font-bold ${
                      delta.changed ? 'text-purple-300' : 'text-slate-200'
                    }`}
                  >
                    {delta.score_after.toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="text-[11px] text-slate-300 leading-snug">
                <span className="text-slate-400 font-medium">Driver: </span>
                {delta.change_reason}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Multi-Round Structured Debate Thread */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg space-y-6">
        <div className="flex justify-between items-center border-b border-slate-700 pb-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-400" />
            Structured Multi-Turn Deliberation Transcript
          </h3>
          <span className="text-xs text-slate-400 font-mono">
            {debateState.rounds} Rounds | {debateState.turns.length} Exchanges
          </span>
        </div>

        {/* Turns Stream */}
        <div className="space-y-6">
          {debateState.turns.map((turn: DebateTurn, idx: number) => {
            const avatar = getAgentAvatar(turn.agent_name);

            return (
              <div key={idx} className="flex gap-4">
                {/* Agent Avatar */}
                <div
                  className={`w-10 h-10 rounded-full ${avatar.bg} text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-md`}
                >
                  {avatar.letter}
                </div>

                {/* Turn Message Card */}
                <div className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl p-4 space-y-3 shadow-sm">
                  <div className="flex flex-wrap justify-between items-center gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-white text-sm">{turn.agent_name}</span>
                      <span className="text-xs text-slate-400">
                        responding to <strong className="text-indigo-300">{turn.responding_to}</strong>
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] text-slate-400 font-mono">Round {turn.round_number}</span>
                      <span
                        className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getStanceBadge(
                          turn.stance
                        )}`}
                      >
                        {turn.stance}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{turn.message}</p>

                  {turn.cites_quote && (
                    <div className="bg-slate-800/80 border border-slate-700 rounded-lg p-2 text-[11px] text-indigo-300 flex items-center gap-2 font-mono">
                      <Quote className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span>Evidence Citation: {turn.cites_quote}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
