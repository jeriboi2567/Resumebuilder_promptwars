import React, { useState } from 'react';
import { CandidateReport } from '../types';
import { FileText, Copy, Download, Check, ShieldCheck, AlertCircle, Quote, Sparkles } from 'lucide-react';

interface FinalReportProps {
  report: CandidateReport;
}

export const FinalReport: React.FC<FinalReportProps> = ({ report }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(report.markdown_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `evaluation_report_${report.candidate_name.replace(/\s+/g, '_')}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-wrap justify-between items-center gap-4 shadow-md">
        <div className="flex items-center space-x-3">
          <FileText className="w-6 h-6 text-indigo-400" />
          <div>
            <h3 className="text-base font-bold text-white">Stage 5 Final Candidate Evaluation Report</h3>
            <p className="text-xs text-slate-400">Auditable report with full reasoning trail and verified citations</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleCopyMarkdown}
            className="flex items-center space-x-2 px-3.5 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-xs font-semibold transition-all border border-slate-600"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied Markdown!' : 'Copy Markdown'}</span>
          </button>

          <button
            onClick={handleDownloadJSON}
            className="flex items-center space-x-2 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-all shadow"
          >
            <Download className="w-4 h-4" />
            <span>Export JSON Audit Trail</span>
          </button>
        </div>
      </div>

      {/* Main Report Document Container */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-8 shadow-xl space-y-8">
        {/* Title & Metadata */}
        <div className="border-b border-slate-700 pb-6 flex justify-between items-start">
          <div>
            <div className="text-xs text-indigo-400 font-mono font-semibold uppercase tracking-wider mb-1">
              Confidential Evaluation Audit
            </div>
            <h1 className="text-3xl font-extrabold text-white">{report.candidate_name}</h1>
            <div className="text-sm text-slate-400 mt-1">
              Candidate ID: <span className="font-mono text-slate-300">{report.candidate_id}</span>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block font-medium">Final Hiring Status</span>
            <span className="text-2xl font-black text-emerald-400 mt-1 block">{report.final_recommendation}</span>
            <span className="text-xs text-indigo-300 font-mono">
              Confidence: {Math.round(report.confidence * 100)}%
            </span>
          </div>
        </div>

        {/* Agent Deliberation Verdict Matrix Table */}
        <div className="space-y-3">
          <h3 className="text-md font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            Agent Persona Stance Evolution Matrix
          </h3>
          <div className="overflow-x-auto rounded-lg border border-slate-700">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900 text-slate-400 uppercase font-mono text-[10px]">
                <tr>
                  <th className="p-3">Agent Persona</th>
                  <th className="p-3">Initial Stance</th>
                  <th className="p-3">Final Stance</th>
                  <th className="p-3">Stance Shifted?</th>
                  <th className="p-3">Key Deliberation Driver</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700 bg-slate-900/60">
                {report.agent_summaries.map((summ, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/50">
                    <td className="p-3 font-semibold text-white">{summ.agent_name}</td>
                    <td className="p-3 font-mono">{summ.initial_verdict} ({summ.initial_score.toFixed(1)})</td>
                    <td className="p-3 font-mono font-bold text-indigo-300">{summ.final_verdict} ({summ.final_score.toFixed(1)})</td>
                    <td className="p-3">
                      {summ.changed ? (
                        <span className="bg-purple-500/20 text-purple-300 text-[10px] px-2 py-0.5 rounded font-semibold border border-purple-500/40">
                          Yes (Shifted)
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[10px]">No Change</span>
                      )}
                    </td>
                    <td className="p-3 text-slate-300">{summ.change_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Strengths & Concerns Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <div className="bg-slate-900/80 border border-emerald-500/30 rounded-xl p-5 space-y-3">
            <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5" />
              Verified Key Strengths
            </h4>
            <div className="space-y-3">
              {report.strengths.map((st, idx) => (
                <div key={idx} className="bg-slate-800/80 border border-slate-700 rounded-lg p-3 text-xs space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span className="text-indigo-400 font-semibold">{st.agent}</span>
                    <span className="font-mono">{st.source}</span>
                  </div>
                  <p className="text-slate-200 italic font-serif">"{st.quote}"</p>
                </div>
              ))}
            </div>
          </div>

          {/* Concerns */}
          <div className="bg-slate-900/80 border border-amber-500/30 rounded-xl p-5 space-y-3">
            <h4 className="text-sm font-bold text-amber-400 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Key Concerns & Red Flags
            </h4>
            <div className="space-y-3">
              {report.concerns.map((cn, idx) => (
                <div key={idx} className="bg-slate-800/80 border border-slate-700 rounded-lg p-3 text-xs space-y-1">
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span className="text-amber-400 font-semibold">{cn.agent}</span>
                    <span className="font-mono">{cn.source}</span>
                  </div>
                  <p className="text-slate-200 italic font-serif">"{cn.quote}"</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Formatted Markdown Preview */}
        <div className="space-y-3 border-t border-slate-700 pt-6">
          <h3 className="text-md font-bold text-slate-300">Complete Markdown Report Output</h3>
          <pre className="bg-slate-900 text-slate-300 p-5 rounded-xl text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-700">
            {report.markdown_content}
          </pre>
        </div>
      </div>
    </div>
  );
};
