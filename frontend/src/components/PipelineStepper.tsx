import React from 'react';
import { UserCheck, ShieldAlert, MessagesSquare, Scale, FileText } from 'lucide-react';

interface PipelineStepperProps {
  currentStage: number;
  onSelectStage: (stage: number) => void;
}

export const PipelineStepper: React.FC<PipelineStepperProps> = ({ currentStage, onSelectStage }) => {
  const stages = [
    { id: 1, name: '1. Profile Builder', icon: UserCheck, desc: 'Shared Source of Truth' },
    { id: 2, name: '2. Isolated Opinions', icon: ShieldAlert, desc: '4 Parallel Agent Calls' },
    { id: 3, name: '3. Structured Debate', icon: MessagesSquare, desc: 'Multi-Turn Deliberation' },
    { id: 4, name: '4. Decision Judge', icon: Scale, desc: 'Weighted Synthesis' },
    { id: 5, name: '5. Final Report', icon: FileText, desc: 'Auditable Executive Report' },
  ];

  return (
    <div className="w-full bg-slate-800/80 backdrop-blur border border-slate-700 rounded-xl p-4 mb-6 shadow-lg">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {stages.map((stage) => {
          const Icon = stage.icon;
          const isActive = currentStage === stage.id;
          const isCompleted = currentStage > stage.id;

          return (
            <button
              key={stage.id}
              onClick={() => onSelectStage(stage.id)}
              className={`flex items-center space-x-3 p-3 rounded-lg border text-left transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-600/30 border-indigo-500 text-indigo-200 ring-2 ring-indigo-500/50 shadow-indigo-500/10'
                  : isCompleted
                  ? 'bg-slate-800 border-slate-600 text-emerald-400 hover:border-slate-500'
                  : 'bg-slate-900/50 border-slate-700/50 text-slate-400 hover:border-slate-600'
              }`}
            >
              <div
                className={`p-2 rounded-md ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : isCompleted
                    ? 'bg-emerald-600/20 text-emerald-400'
                    : 'bg-slate-800 text-slate-400'
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-semibold truncate">{stage.name}</div>
                <div className="text-xs text-slate-400 truncate">{stage.desc}</div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
