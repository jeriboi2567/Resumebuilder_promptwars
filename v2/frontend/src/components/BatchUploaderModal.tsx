import React, { useState } from 'react';
import { Upload, FileText, Plus, Trash2, X, Loader2 } from 'lucide-react';

interface BatchUploaderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: (batchData: any) => void;
}

export const BatchUploaderModal: React.FC<BatchUploaderModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess
}) => {
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [candidatePairs, setCandidatePairs] = useState<Array<{ resume: File | null; transcript: File | null }>>([
    { resume: null, transcript: null },
    { resume: null, transcript: null }
  ]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAddCandidate = () => {
    setCandidatePairs([...candidatePairs, { resume: null, transcript: null }]);
  };

  const handleRemoveCandidate = (index: number) => {
    if (candidatePairs.length <= 1) return;
    setCandidatePairs(candidatePairs.filter((_, idx) => idx !== index));
  };

  const handleFileChange = (
    index: number,
    type: 'resume' | 'transcript',
    file: File | null
  ) => {
    const updated = [...candidatePairs];
    updated[index][type] = file;
    setCandidatePairs(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdFile) {
      setError("Please select a Job Description PDF/Text file.");
      return;
    }

    const incomplete = candidatePairs.some(pair => !pair.resume || !pair.transcript);
    if (incomplete) {
      setError("Please provide both a Resume and Transcript file for each candidate.");
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("jd_file", jdFile);

    candidatePairs.forEach(pair => {
      if (pair.resume) formData.append("resume_files", pair.resume);
      if (pair.transcript) formData.append("transcript_files", pair.transcript);
    });

    try {
      const res = await fetch("/api/evaluate-batch", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Upload failed with status ${res.status}`);
      }

      const data = await res.json();
      onUploadSuccess(data);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to process batch upload.");
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
            <Upload className="w-6 h-6 text-indigo-400" />
            Batch PDF & Document Upload
          </h3>
          <p className="text-xs text-slate-400">
            Upload 1 Job Description and $N$ Candidate (Resume PDF, Transcript PDF) pairs for parallel evaluation.
          </p>
        </div>

        {error && (
          <div className="bg-rose-950/60 border border-rose-500/50 p-3 rounded-lg text-xs text-rose-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Job Description Upload */}
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase text-indigo-300">
              1. Shared Job Description (PDF / TXT)
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

          {/* Candidate PDF Pairs */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <label className="block text-xs font-bold uppercase text-indigo-300">
                2. Candidate File Pairs (Resume PDF + Transcript PDF)
              </label>
              <button
                type="button"
                onClick={handleAddCandidate}
                className="flex items-center space-x-1 px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-xs font-semibold"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Candidate Pair</span>
              </button>
            </div>

            <div className="space-y-3">
              {candidatePairs.map((pair, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-700/80 p-4 rounded-xl space-y-3 relative">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">Candidate #{idx + 1}</span>
                    {candidatePairs.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveCandidate(idx)}
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
                        className="w-full text-xs text-slate-300 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-[11px] file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 bg-slate-950 p-1.5 rounded border border-slate-800"
                      />
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-400 block mb-1">Transcript PDF/TXT</span>
                      <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => handleFileChange(idx, 'transcript', e.target.files?.[0] || null)}
                        className="w-full text-xs text-slate-300 file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:text-[11px] file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 bg-slate-950 p-1.5 rounded border border-slate-800"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3 border-t border-slate-700 pt-4">
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
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing Batch Pipeline...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Run Batch Evaluation</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
