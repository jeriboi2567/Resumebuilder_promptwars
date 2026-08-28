import React, { useState } from 'react';
import { Upload, FileText, Plus, Trash2, X, Loader2, Briefcase } from 'lucide-react';
import { HiringRoleV3 } from '../types';
import { API_BASE_URL } from '../config';

interface RoleUploaderModalProps {
  isOpen: boolean;
  onClose: () => void;
  roles: Array<{ role_id: str; title: str; company: str }>;
  activeRoleId?: string;
  onRoleUpdated: (role: HiringRoleV3) => void;
}

export const RoleUploaderModal: React.FC<RoleUploaderModalProps> = ({
  isOpen,
  onClose,
  roles,
  activeRoleId,
  onRoleUpdated
}) => {
  const [mode, setMode] = useState<'add_candidate' | 'create_role'>('add_candidate');
  const [selectedRoleId, setSelectedRoleId] = useState<string>(activeRoleId || (roles.length > 0 ? roles[0].role_id : ''));
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [candidatePairs, setCandidatePairs] = useState<Array<{ resume: File | null; transcript: File | null }>>([
    { resume: null, transcript: null }
  ]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAddCandidatePair = () => {
    setCandidatePairs([...candidatePairs, { resume: null, transcript: null }]);
  };

  const handleRemoveCandidatePair = (index: number) => {
    if (candidatePairs.length <= 1) return;
    setCandidatePairs(candidatePairs.filter((_, idx) => idx !== index));
  };

  const handleFileChange = (index: number, type: 'resume' | 'transcript', file: File | null) => {
    const updated = [...candidatePairs];
    updated[index][type] = file;
    setCandidatePairs(updated);
  };

  const handleCreateRoleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdFile) {
      setError("Please select a Job Description PDF/TXT file.");
      return;
    }

    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("jd_file", jdFile);

      const res = await fetch(`${API_BASE_URL}/api/roles`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Failed to create hiring role (Status ${res.status})`);
      }

      const newRole: HiringRoleV3 = await res.json();
      onRoleUpdated(newRole);
      onClose();
    } catch (err: any) {
      setError(err.message || "Error creating hiring role.");
    } finally {
      setUploading(false);
    }
  };

  const handleAddCandidatesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoleId) {
      setError("Please select a Hiring Role.");
      return;
    }

    const incomplete = candidatePairs.some(pair => !pair.resume || !pair.transcript);
    if (incomplete) {
      setError("Please provide both a Resume and Transcript file for each candidate.");
      return;
    }

    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      candidatePairs.forEach(pair => {
        if (pair.resume) formData.append("resume_files", pair.resume);
        if (pair.transcript) formData.append("transcript_files", pair.transcript);
      });

      const res = await fetch(`${API_BASE_URL}/api/roles/${selectedRoleId}/candidates`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Failed to add candidates (Status ${res.status})`);
      }

      const updatedRole: HiringRoleV3 = await res.json();
      onRoleUpdated(updatedRole);
      onClose();
    } catch (err: any) {
      setError(err.message || "Error adding candidate to hiring role.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-700"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="space-y-1 border-b border-slate-700 pb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-indigo-400" />
            General-Purpose Employer Hiring Platform
          </h3>
          <p className="text-xs text-slate-400">
            Create custom Job Roles and accumulate candidates over time for arbitrary hiring workflows.
          </p>

          <div className="flex space-x-2 pt-2">
            <button
              onClick={() => setMode('add_candidate')}
              className={`px-3 py-1 rounded text-xs font-bold ${
                mode === 'add_candidate' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300'
              }`}
            >
              Add Candidate to Existing Role
            </button>
            <button
              onClick={() => setMode('create_role')}
              className={`px-3 py-1 rounded text-xs font-bold ${
                mode === 'create_role' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300'
              }`}
            >
              Create New Hiring Role (New JD)
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-500/50 p-3 rounded-lg text-xs text-rose-200">
            {error}
          </div>
        )}

        {mode === 'create_role' ? (
          <form onSubmit={handleCreateRoleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase text-indigo-300">
                Upload New Job Description (PDF / TXT)
              </label>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                className="w-full text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer bg-slate-900 p-2 rounded-lg border border-slate-700"
              />
              {jdFile && (
                <div className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5" /> Selected: {jdFile.name}
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-slate-700">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={uploading}
                className="flex items-center space-x-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold disabled:opacity-50"
              >
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                <span>Create Hiring Role</span>
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleAddCandidatesSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase text-indigo-300">
                Select Target Hiring Role:
              </label>
              <select
                value={selectedRoleId}
                onChange={(e) => setSelectedRoleId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white text-xs p-2.5 rounded-lg"
              >
                {roles.map((r) => (
                  <option key={r.role_id} value={r.role_id}>
                    {r.title} ({r.company})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="block text-xs font-bold uppercase text-indigo-300">
                  Upload Candidate Pair (Resume PDF + Transcript PDF)
                </label>
                <button
                  type="button"
                  onClick={handleAddCandidatePair}
                  className="flex items-center space-x-1 px-3 py-1 bg-slate-700 text-slate-200 rounded text-xs font-semibold"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Candidate
                </button>
              </div>

              {candidatePairs.map((pair, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-700/80 p-4 rounded-xl space-y-3 relative">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">Candidate #{idx + 1}</span>
                    {candidatePairs.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveCandidatePair(idx)}
                        className="text-rose-400 hover:text-rose-300 text-xs flex items-center gap-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" /> Remove
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <span className="text-[10px] text-slate-400 block mb-1">Resume PDF/TXT</span>
                      <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => handleFileChange(idx, 'resume', e.target.files?.[0] || null)}
                        className="w-full text-xs text-slate-300 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-[11px] file:bg-slate-800 file:text-slate-200 bg-slate-950 p-1 rounded border border-slate-800"
                      />
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block mb-1">Transcript PDF/TXT</span>
                      <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => handleFileChange(idx, 'transcript', e.target.files?.[0] || null)}
                        className="w-full text-xs text-slate-300 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-[11px] file:bg-slate-800 file:text-slate-200 bg-slate-950 p-1 rounded border border-slate-800"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-slate-700">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={uploading}
                className="flex items-center space-x-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold disabled:opacity-50"
              >
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                <span>Evaluate & Append Candidates</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
