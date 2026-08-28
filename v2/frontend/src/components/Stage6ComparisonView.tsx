import React from 'react';
import { Stage6ComparativeRanking, JobDescription } from '../types';
import { Award, Layers, CheckCircle2, AlertTriangle, HelpCircle, XCircle, ChevronRight, Info } from 'lucide-react';

interface Stage6ComparisonViewProps {
  comparison: Stage6ComparativeRanking;
  jobDescription: JobDescription;
}

export const Stage6ComparisonView: React.FC<Stage6ComparisonViewProps> = ({ comparison, jobDescription }) => {
  const getStatusBadge = (status: string) => {
    if (status.includes('Verified') || status.includes('Exceeds')) {
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
    if (status.includes('Not Assessed')) {
      return 'bg-slate-700/80 text-slate-300 border-slate-600';
    }
    if (status.includes('Failed') || status.includes('Exaggerated')) {
      return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
    }
    return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
  };

  return (
    <div className="space-y-8">
      {/* Stage 6 Banner */}
      <div className="bg-gradient-to-r from-slate-800 via-indigo-950 to-purple-950 border border-indigo-500/40 rounded-xl p-6 shadow-xl flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl text-white shadow-lg">
            <Layers className="w-8 h-8" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-indigo-400 font-bold font-mono">
              Stage 6: Additive Comparative Ranking Engine
            </div>
            <h2 className="text-2xl font-extrabold text-white mt-0.5">
              Side-by-Side Batch Candidate Comparison
            </h2>
            <p className="text-xs text-slate-300 mt-1">
              Evaluated against Job Description: <strong className="text-white">{jobDescription.title}</strong>
            </p>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-700 p-3 rounded-lg text-right">
          <div className="text-[10px] text-slate-400 font-mono">Batch Execution Complete</div>
          <div className="text-sm font-bold text-emerald-400 font-mono">
            {comparison.rankings.length} Candidates Assessed
          </div>
        </div>
      </div>

      {/* Candidate Ranking Cards Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-400" />
          Evidence-Weighted Candidate Ranking
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {comparison.rankings.map((item) => (
            <div
              key={item.candidate_id}
              className={`bg-slate-800 border rounded-xl p-6 shadow-lg relative flex flex-col justify-between space-y-4 ${
                item.rank === 1 ? 'border-amber-500/60 ring-2 ring-amber-500/20' : 'border-slate-700'
              }`}
            >
              {/* Rank Badge */}
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center font-black text-lg font-mono ${
                      item.rank === 1
                        ? 'bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 shadow-md'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    #{item.rank}
                  </div>
                  <div>
                    <h4 className="text-xl font-bold text-white">{item.candidate_name}</h4>
                    <span className="text-xs text-slate-400 font-mono">{item.candidate_id}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`text-xs font-bold px-3 py-1 rounded-full ${
                      item.final_recommendation === 'Strong Hire'
                        ? 'bg-emerald-600 text-white'
                        : item.final_recommendation === 'Hire'
                        ? 'bg-emerald-700 text-emerald-100'
                        : 'bg-rose-600 text-white'
                    }`}
                  >
                    {item.final_recommendation}
                  </span>
                  <div className="text-[10px] text-indigo-300 font-mono mt-1">
                    Confidence: {Math.round(item.confidence * 100)}%
                  </div>
                </div>
              </div>

              {/* Key Differentiators */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wide block">
                  Key Evaluation Differentiators:
                </span>
                <ul className="space-y-1.5 pl-1">
                  {item.key_differentiators.map((diff, dIdx) => (
                    <li key={dIdx} className="text-xs text-slate-200 flex items-start gap-2">
                      <ChevronRight className="w-3.5 h-3.5 text-indigo-400 mt-0.5 shrink-0" />
                      <span>{diff}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Shared Job Description Requirement Compliance Matrix */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2 border-b border-slate-700 pb-3">
          <Info className="w-5 h-5 text-indigo-400" />
          Shared Job Description Requirement Compliance Matrix
        </h3>

        <div className="overflow-x-auto rounded-lg border border-slate-700">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900 text-slate-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="p-3.5">Job Description Requirement</th>
                {comparison.rankings.map((r) => (
                  <th key={r.candidate_id} className="p-3.5">
                    {r.candidate_name} (#{r.rank})
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700 bg-slate-900/60">
              {comparison.jd_compliance_matrix.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/50">
                  <td className="p-3.5 font-semibold text-white max-w-xs">{row.requirement}</td>
                  {comparison.rankings.map((r) => {
                    const evalData = row.candidate_evaluations[r.candidate_id] || {
                      status: 'Not Assessed',
                      detail: 'No data'
                    };
                    return (
                      <td key={r.candidate_id} className="p-3.5 max-w-xs">
                        <span
                          className={`text-[10px] font-bold px-2.5 py-1 rounded-full inline-block border mb-1 ${getStatusBadge(
                            evalData.status
                          )}`}
                        >
                          {evalData.status}
                        </span>
                        <div className="text-[11px] text-slate-300 leading-snug">{evalData.detail}</div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparative Rationale & Close Calls */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md space-y-4">
        <h3 className="text-md font-bold text-white border-b border-slate-700 pb-3">
          Comparative Ranking Rationale & Panel Confidence
        </h3>
        <p className="text-xs text-slate-200 leading-relaxed font-sans bg-slate-900/70 p-4 rounded-lg border border-slate-700">
          {comparison.comparison_rationale}
        </p>

        {comparison.close_calls && comparison.close_calls.length > 0 && (
          <div className="space-y-2 pt-2">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-wide block">
              Surfaced Panel Observations:
            </span>
            {comparison.close_calls.map((cc, idx) => (
              <div
                key={idx}
                className="bg-amber-950/30 border border-amber-500/30 p-3 rounded-lg text-xs text-amber-200"
              >
                {cc}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
