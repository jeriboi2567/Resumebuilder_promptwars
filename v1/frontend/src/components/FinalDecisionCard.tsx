import React from 'react';
import { FinalDecision } from '../types';
import { Scale, CheckCircle2, AlertOctagon, Award, Info } from 'lucide-react';

interface FinalDecisionCardProps {
  decision: FinalDecision;
}

export const FinalDecisionCard: React.FC<FinalDecisionCardProps> = ({ decision }) => {
  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'Strong Hire':
        return { bg: 'bg-emerald-600', border: 'border-emerald-500', text: 'text-emerald-300' };
      case 'Hire':
        return { bg: 'bg-emerald-700', border: 'border-emerald-600', text: 'text-emerald-200' };
      case 'Lean No':
        return { bg: 'bg-amber-600', border: 'border-amber-500', text: 'text-amber-200' };
      default:
        return { bg: 'bg-rose-600', border: 'border-rose-500', text: 'text-rose-200' };
    }
  };

  const badgeStyle = getRecommendationBadge(decision.recommendation);

  return (
    <div className="space-y-6">
      {/* Top Banner: Final Recommendation & Confidence Gauge */}
      <div className={`bg-slate-800 border ${badgeStyle.border} rounded-xl p-6 shadow-xl flex flex-wrap justify-between items-center gap-6`}>
        <div className="flex items-center space-x-5">
          <div className={`p-4 rounded-xl ${badgeStyle.bg} text-white shadow-lg`}>
            <Award className="w-8 h-8" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
              Stage 4 Judge Recommendation
            </div>
            <h2 className="text-3xl font-extrabold text-white mt-0.5">{decision.recommendation}</h2>
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-1 font-mono">
              <Info className="w-3.5 h-3.5 text-indigo-400" />
              Synthesized via Evidence-Weighted Reasoning (Not Score Averaging)
            </div>
          </div>
        </div>

        {/* Confidence Gauge */}
        <div className="bg-slate-900/90 border border-slate-700 p-4 rounded-xl flex items-center space-x-4">
          <div>
            <div className="text-xs text-slate-400 font-medium">Panel Confidence</div>
            <div className="text-2xl font-mono font-bold text-indigo-300">
              {Math.round(decision.confidence * 100)}%
            </div>
          </div>
          <div className="w-24 bg-slate-800 h-3 rounded-full overflow-hidden border border-slate-700">
            <div
              className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full"
              style={{ width: `${decision.confidence * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Detailed Decision Rationale */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-700 pb-3">
              <Scale className="w-5 h-5 text-indigo-400" />
              Synthesizer Decision Rationale & Evidence Weighing
            </h3>
            <div className="text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-line bg-slate-900/60 p-4 rounded-lg border border-slate-700/60">
              {decision.decision_rationale}
            </div>
          </div>

          {/* Unresolved Disagreements Alert Banner */}
          {decision.unresolved_disagreements && decision.unresolved_disagreements.length > 0 ? (
            <div className="bg-amber-950/40 border border-amber-500/40 rounded-xl p-5 shadow-md space-y-3">
              <h4 className="text-sm font-bold text-amber-300 flex items-center gap-2">
                <AlertOctagon className="w-5 h-5 text-amber-400 shrink-0" />
                Unresolved Panel Disagreements (Exposed Transparently)
              </h4>
              <p className="text-xs text-amber-200/90 leading-relaxed">
                Rather than silently smoothing over panel debate, the system explicitly flags remaining areas of non-convergence:
              </p>
              <ul className="space-y-2">
                {decision.unresolved_disagreements.map((dis, idx) => (
                  <li
                    key={idx}
                    className="bg-slate-900/80 border border-amber-500/30 rounded-lg p-3 text-xs text-slate-200 flex items-start gap-2"
                  >
                    <span className="text-amber-400 font-bold">•</span>
                    <span>{dis}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-xl p-4 flex items-center space-x-3 text-xs text-emerald-300">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              <span>Complete Panel Convergence: All 4 agent personas aligned post-debate with zero unresolved red flags.</span>
            </div>
          )}
        </div>

        {/* Right Col: Evidence Weight Breakdown per Agent */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md space-y-4">
          <h3 className="text-md font-bold text-white border-b border-slate-700 pb-3">
            Assigned Evidence Quality Weights
          </h3>
          <p className="text-xs text-slate-400">
            Agents with verified quote citations and stable debate positions carry higher weight in the final recommendation.
          </p>

          <div className="space-y-4 pt-2">
            {Object.entries(decision.evidence_weights).map(([agent, weight]) => (
              <div key={agent} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-200">{agent}</span>
                  <span className="font-mono text-indigo-300">{(weight * 100).toFixed(0)}% weight</span>
                </div>
                <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-700">
                  <div
                    className="bg-indigo-500 h-full rounded-full"
                    style={{ width: `${weight * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
