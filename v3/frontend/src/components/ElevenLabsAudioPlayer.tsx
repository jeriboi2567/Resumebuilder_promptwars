import React, { useState, useRef } from 'react';
import { DebateTurn } from '../types';
import { Volume2, Play, Pause } from 'lucide-react';

interface ElevenLabsAudioPlayerProps {
  audioUrl?: string;
  turns: DebateTurn[];
}

export const ElevenLabsAudioPlayer: React.FC<ElevenLabsAudioPlayerProps> = ({ audioUrl, turns }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
      }).catch(err => {
        console.error("Audio playback error:", err);
      });
    }
  };

  return (
    <div className="bg-gradient-to-r from-indigo-950 via-purple-950 to-slate-900 border border-purple-500/40 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-lg">
      <div className="flex items-center space-x-3">
        <div className="p-3 bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/40">
          <Volume2 className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h4 className="font-bold text-white text-sm flex items-center gap-2">
            ElevenLabs Multi-Voice AI Debate Narration
            <span className="text-[10px] bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-2 py-0.5 rounded font-mono font-bold">
              ElevenLabs Powered
            </span>
          </h4>
          <p className="text-xs text-slate-300">
            Synthesized multi-turn debate audio with 4 distinct persona voices (Adam, Rachel, Arnold, Sam).
          </p>
        </div>
      </div>

      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onEnded={() => setIsPlaying(false)}
          className="hidden"
        />
      )}

      <div className="flex items-center space-x-3">
        <button
          onClick={togglePlay}
          className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-bold transition-all shadow-lg hover:shadow-purple-500/20"
        >
          {isPlaying ? (
            <>
              <Pause className="w-4 h-4" />
              <span>Pause ElevenLabs Audio</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Play ElevenLabs Audio</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
