import React from 'react';
import { IndependentOpinions, AgentOpinion } from '../types';
import { ShieldAlert, Cpu, Users, UserCheck, Eye, CheckCircle2, AlertTriangle } from 'lucide-react';

interface OpinionCardProps {
  independentOpinions: IndependentOpinions;
}

export const OpinionCardGrid: React.FC<OpinionCardProps> = ({ independentOpinions }) => {
  const agentIcons: Record<string, any> = {
    'Technical Agent': Cpu,
    'HR / Culture Agent': Users,
    'Hiring Manager Agent': UserCheck,
    'Skeptic Agent': Eye,
  };

  const agentColors: Record<string, { border: string; bg: string; text: string; badge: string }> = {
    'Technical Agent': {
      border: 'border-cyan-500/40',
      bg: 'bg-cyan-950/20',
      text: 'text-cyan-400',
      badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
    },
    'HR / Culture Agent': {
      border: 'border-pink-500/40',
      bg: 'bg-pink-950/20',
      text: 'text-pink-400',
      badge: 'bg-pink-500/20 text-pink-300 border-pink-500/30'
    },
    'Hiring Manager Agent': {
      border: 'border-emerald-500/40',
      bg: 'bg-emerald-950/20',
      text: 'text-emerald-400',
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
    },
    'Skeptic Agent': {
      border: 'border-amber-500/40',
      bg: 'bg-amber-950/20',
      text: 'text-amber-400',
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    },
  };

  const getVerdictStyle = (verdict: string) => {
    if (verdict.includes('Strong Hire')) return 'bg-emerald-600 text-white';
    if (verdict.includes('Hire')) return 'bg-emerald-700/80 text-emerald-100';
    if (verdict.includes('Lean No')) return 'bg-amber-600/80 text-amber-100';
    return 'bg-rose-600 text-white';
  };

  const opinionsList = Object.values(independentOpinions.opinions);

  return (
    <div className="space-y-6">
      {/* Isolation Proof Header Banner */}
      <div className="bg-gradient-to-r from-slate-800 via-indigo-950 to-slate-800 border border-indigo-500/30 rounded-xl p-4 shadow-md flex items-center gap-3">
        <ShieldAlert className="w-6 h-6 text-indigo-400 shrink-0" />
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            Architectural Stage 2 Isolation Enforced
            <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/30 font-mono">
              4 Parallel LLM Calls
            </span>
          </h3>
          <p className="text-xs text-slate-300">
            Each agent persona evaluated the candidate profile in 100% isolation. Zero cross-visibility or prompt pollution existed at this stage.
          </p>
        </div>
      </div>

      {/* 4 Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {opinionsList.map((op: AgentOpinion) => {
          const Icon = agentIcons[op.agent_name] || Cpu;
          const style = agentColors[op.agent_name] || agentColors['Technical Agent'];

          return (
            <div
              key={op.agent_name}
              className={`bg-slate-800 border ${style.border} rounded-xl p-5 shadow-lg flex flex-col justify-between space-y-4`}
            >
              {/* Card Header */}
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-3">
                  <div className={`p-2.5 rounded-lg ${style.bg} ${style.text} border ${style.border}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white text-base">{op.agent_name}</h4>
                    <div className="flex items-center gap-2 text-xs mt-0.5">
                      <span className="text-slate-400">Confidence:</span>
                      <div className="w-20 bg-slate-700 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-400 h-full rounded-full"
                          style={{ width: `${op.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="font-mono text-slate-300 text-[11px]">
                        {Math.round(op.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Score & Verdict Pill */}
                <div className="text-right">
                  <div className="text-xl font-extrabold text-white font-mono">{op.score.toFixed(1)}/10</div>
                  <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full inline-block mt-1 ${getVerdictStyle(op.verdict)}`}>
                    {op.verdict}
                  </span>
                </div>
              </div>

              {/* Reasoning Body */}
              <div className="bg-slate-900/70 border border-slate-700/60 rounded-lg p-3.5 text-xs text-slate-300 leading-relaxed">
                <span className="font-semibold text-slate-200 block mb-1">Reasoning & Analysis:</span>
                {op.reasoning}
              </div>

              {/* Supporting Quotes Section */}
              <div className="space-y-2">
                <h5 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                  <span>Supporting Quotes (Verified)</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {op.supporting_quotes.length} cited
                  </span>
                </h5>
                <div className="space-y-2">
                  {op.supporting_quotes.map((sq, qIdx) => (
                    <div
                      key={qIdx}
                      className="bg-slate-900/90 border border-slate-700 rounded-lg p-2.5 text-xs space-y-1"
                    >
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="font-mono text-indigo-300 font-semibold">{sq.source}</span>
                        {sq.verified ? (
                          <span className="flex items-center gap-1 text-emerald-400 font-medium">
                            <CheckCircle2 className="w-3 h-3" />
                            Verified Substring
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-amber-400 font-medium">
                            <AlertTriangle className="w-3 h-3" />
                            Unverified
                          </span>
                        )}
                      </div>
                      <p className="text-slate-300 italic font-serif">"{sq.quote}"</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
