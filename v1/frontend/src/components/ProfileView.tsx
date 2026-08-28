import React, { useState } from 'react';
import { CandidateProfile } from '../types';
import { User, Briefcase, Award, Quote, FileText, CheckCircle2, ChevronRight } from 'lucide-react';

interface ProfileViewProps {
  profile: CandidateProfile;
}

export const ProfileView: React.FC<ProfileViewProps> = ({ profile }) => {
  const [activeTab, setActiveTab] = useState<'extracted' | 'raw_resume' | 'raw_transcript'>('extracted');
  const [selectedTopic, setSelectedTopic] = useState<string>('all');

  const topics = ['all', ...Array.from(new Set(profile.quote_bank.map((q) => q.topic)))];

  const filteredQuotes = selectedTopic === 'all'
    ? profile.quote_bank
    : profile.quote_bank.filter((q) => q.topic === selectedTopic);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md flex flex-wrap justify-between items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white text-xl font-bold shadow-md">
            {profile.candidate_name.charAt(0)}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              {profile.candidate_name}
              <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {profile.seniority_level}
              </span>
            </h2>
            <p className="text-slate-400 flex items-center gap-2 text-sm mt-1">
              <Briefcase className="w-4 h-4 text-indigo-400" />
              Role Applied: <span className="text-slate-200 font-medium">{profile.role_applied}</span>
            </p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-700">
          <button
            onClick={() => setActiveTab('extracted')}
            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'extracted' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Structured Profile
          </button>
          <button
            onClick={() => setActiveTab('raw_resume')}
            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'raw_resume' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Raw Resume Text
          </button>
          <button
            onClick={() => setActiveTab('raw_transcript')}
            className={`px-4 py-2 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'raw_transcript' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Raw Transcript Text
          </button>
        </div>
      </div>

      {activeTab === 'extracted' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Skills & Experience */}
          <div className="lg:col-span-2 space-y-6">
            {/* Skills Card */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                <Award className="w-5 h-5 text-amber-400" />
                Claimed Technical Skills (with Source Citations)
              </h3>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs flex flex-col gap-1 hover:border-slate-500 transition-colors"
                  >
                    <span className="font-semibold text-slate-200">{skill.skill_name}</span>
                    <span className="text-[10px] text-indigo-400 font-mono flex items-center gap-1">
                      <ChevronRight className="w-3 h-3" />
                      {skill.citation.location}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Experience Card */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-2">
                <Briefcase className="w-5 h-5 text-indigo-400" />
                Professional Experience History
              </h3>
              {profile.experiences.map((exp, idx) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-700/80 rounded-lg p-4 space-y-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-indigo-300 text-sm">{exp.role}</h4>
                      <div className="text-xs text-slate-400">{exp.company}</div>
                    </div>
                    <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2 py-1 rounded">
                      {exp.duration}
                    </span>
                  </div>
                  <ul className="space-y-1.5 pl-2">
                    {exp.responsibilities.map((resp, rIdx) => (
                      <li key={rIdx} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-indigo-400 mt-0.5">•</span>
                        <span>{resp}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="pt-2 text-[10px] text-slate-400 font-mono flex items-center gap-1 border-t border-slate-800">
                    <FileText className="w-3 h-3 text-slate-500" />
                    Citation: {exp.citation.location} ({exp.citation.quote_snippet})
                  </div>
                </div>
              ))}
            </div>

            {/* Claims Bank Card */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                Verified Claims Bank (Quantifiable & Qualitative)
              </h3>
              <div className="space-y-3">
                {profile.claims.map((claim, idx) => (
                  <div key={idx} className="bg-slate-900 border border-slate-700/70 rounded-lg p-3 text-xs space-y-1">
                    <div className="flex justify-between items-center">
                      <span
                        className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                          claim.claim_type === 'quantitative'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        }`}
                      >
                        {claim.claim_type}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {claim.citation.location}
                      </span>
                    </div>
                    <p className="text-slate-200 font-medium">{claim.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Direct Quote Bank */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Quote className="w-5 h-5 text-purple-400" />
                Direct Quote Index
              </h3>
              <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-mono">
                {filteredQuotes.length} quotes
              </span>
            </div>

            {/* Topic Filter Pills */}
            <div className="flex flex-wrap gap-1.5 border-b border-slate-700 pb-3">
              {topics.map((topic) => (
                <button
                  key={topic}
                  onClick={() => setSelectedTopic(topic)}
                  className={`text-[11px] px-2.5 py-1 rounded-md font-medium capitalize transition-all ${
                    selectedTopic === topic
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-900 text-slate-400 hover:text-white'
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>

            {/* Quotes List */}
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
              {filteredQuotes.map((q) => (
                <div key={q.id} className="bg-slate-900 border border-slate-700/80 rounded-lg p-3 space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-purple-400 font-semibold uppercase text-[10px] tracking-wide">
                      {q.topic}
                    </span>
                    <span className="text-slate-400 font-mono text-[10px]">{q.location}</span>
                  </div>
                  <p className="text-slate-200 italic font-serif">"{q.quote}"</p>
                  {q.speaker && (
                    <div className="text-[10px] text-slate-400 text-right font-medium">
                      — {q.speaker}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : activeTab === 'raw_resume' ? (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h3 className="text-md font-bold text-slate-300 mb-3">Raw Resume Text Document</h3>
          <pre className="bg-slate-900 text-slate-300 p-4 rounded-lg text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-700">
            {profile.raw_resume_text}
          </pre>
        </div>
      ) : (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <h3 className="text-md font-bold text-slate-300 mb-3">Raw Interview Transcript Document</h3>
          <pre className="bg-slate-900 text-slate-300 p-4 rounded-lg text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-700">
            {profile.raw_transcript_text}
          </pre>
        </div>
      )}
    </div>
  );
};
