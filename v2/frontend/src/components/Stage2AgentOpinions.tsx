import React from 'react';
import { IndependentOpinionsV2 } from '../types';
import { ShieldCheck, UserCheck, Briefcase, AlertTriangle, Quote, CheckCircle2, HelpCircle } from 'lucide-react';

interface Stage2AgentOpinionsProps {
  opinions: IndependentOpinionsV2;
}

export const Stage2AgentOpinions: React.FC<Stage2AgentOpinionsProps> = ({ opinions }) => {
  const getAgentHeader = (agentName: string) => {
    switch (agentName) {
      case 'Technical Agent':
        return { icon: ShieldCheck, color: 'text-blue-400', border: 'border-blue-500/40', bg: 'bg-blue-950/30' };
      case 'HR / Culture Agent':
        return { icon: UserCheck, color: 'text-emerald-400', border: 'border-emerald-500/40', bg: 'bg-emerald-950/30' };
      case 'Hiring Manager Agent':
        return { icon: Briefcase, color: 'text-purple-400', border: 'border-purple-500/40', bg: 'bg-purple-950/30' };
      case 'Skeptic Agent':
        return { icon: AlertTriangle, color: 'text-rose-400', border: 'border-rose-500/40', bg: 'bg-rose-950/30' };
      default:
        return { icon: ShieldCheck, color: 'text-slate-400', border: 'border-slate-700', bg: 'bg-slate-900' };
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-b border-slate-700 pb-3 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            Stage 2: Four Architecturally Isolated Agent Personas
          </h3>
          <p className="text-xs text-slate-400">
            Independent opinions evaluated in strict isolation (separate LLM calls) prior to Stage 3 debate.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.values(opinions.opinions).map((op) => {
          const style = getAgentHeader(op.agent_name);
          const Icon = style.icon;
          return (
            <div
              key={op.agent_name}
              className={`bg-slate-800/90 border ${style.border} rounded-xl p-5 shadow-lg space-y-4 flex flex-col justify-between`}
            >
              <div className="space-y-3">
                <div className="flex justify-between items-start border-b border-slate-700/60 pb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${style.bg} ${style.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm">{op.agent_name}</h4>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Confidence: {Math.round(op.confidence * 100)}%
                      </span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs font-extrabold px-3 py-1 bg-slate-900 border border-slate-700 rounded-lg text-white">
                      {op.verdict} ({op.overall_score ?? 'N/A'})
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-200 leading-relaxed">{op.reasoning}</p>

                {/* Supporting Quote Snippets */}
                {op.supporting_quotes.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                      Cited Source Evidence:
                    </span>
                    {op.supporting_quotes.map((q, qIdx) => (
                      <div
                        key={qIdx}
                        className="text-[11px] text-slate-300 bg-slate-900/80 p-2 rounded-lg border border-slate-800 flex items-start space-x-2"
                      >
                        <Quote className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                        <div>
                          <span>"{q.quote}"</span>
                          <span className="text-[10px] text-indigo-400 font-mono block mt-0.5">
                            Source: {q.source}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Insufficient Evidence Dimension Flags */}
              {op.insufficient_dimensions.length > 0 && (
                <div className="bg-amber-950/30 border border-amber-500/30 p-2.5 rounded-lg text-[11px] text-amber-200 flex items-start space-x-2">
                  <HelpCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-amber-300">Not Assessed:</strong> {op.insufficient_dimensions.join(', ')}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
