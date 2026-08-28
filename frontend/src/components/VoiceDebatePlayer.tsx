import React, { useState, useEffect } from 'react';
import { DebateTurn } from '../types';
import { Volume2, VolumeX, Play, Pause, RotateCcw } from 'lucide-react';

interface VoiceDebatePlayerProps {
  turns: DebateTurn[];
}

export const VoiceDebatePlayer: React.FC<VoiceDebatePlayerProps> = ({ turns }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTurnIdx, setCurrentTurnIdx] = useState<number>(-1);
  const [isSupported, setIsSupported] = useState(true);

  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      setIsSupported(false);
    }
  }, []);

  const stopAudio = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlaying(false);
    setCurrentTurnIdx(-1);
  };

  const speakTurn = (idx: number) => {
    if (idx >= turns.length) {
      setIsPlaying(false);
      setCurrentTurnIdx(-1);
      return;
    }

    setCurrentTurnIdx(idx);
    const turn = turns[idx];
    const textToSpeak = `${turn.agent_name}, responding to ${turn.responding_to}. Stance: ${turn.stance}. ${turn.message}`;

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 1.0;

    // Modulate pitch per persona for distinct voice audio feel
    if (turn.agent_name.includes('Technical')) {
      utterance.pitch = 0.9;
    } else if (turn.agent_name.includes('HR')) {
      utterance.pitch = 1.2;
    } else if (turn.agent_name.includes('Hiring Manager')) {
      utterance.pitch = 1.0;
    } else {
      // Skeptic
      utterance.pitch = 0.7;
    }

    utterance.onend = () => {
      speakTurn(idx + 1);
    };

    utterance.onerror = () => {
      setIsPlaying(false);
      setCurrentTurnIdx(-1);
    };

    window.speechSynthesis.speak(utterance);
  };

  const togglePlay = () => {
    if (!isSupported) return;

    if (isPlaying) {
      stopAudio();
    } else {
      setIsPlaying(true);
      speakTurn(0);
    }
  };

  return (
    <div className="bg-gradient-to-r from-purple-950/40 via-indigo-950/40 to-slate-900 border border-purple-500/30 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-md">
      <div className="flex items-center space-x-3">
        <div className="p-3 bg-purple-600/30 text-purple-300 rounded-lg border border-purple-500/40">
          <Volume2 className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h4 className="font-bold text-white text-sm flex items-center gap-2">
            Multi-Voice Audio Debate Player (TTS)
            <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded font-mono border border-purple-500/30">
              Bonus Feature
            </span>
          </h4>
          <p className="text-xs text-slate-300">
            Listen in as the 4 AI agent personas present and defend their evidentiary claims in real time.
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {isPlaying && currentTurnIdx >= 0 && (
          <span className="text-xs text-purple-300 font-mono bg-purple-950/80 px-3 py-1 rounded-full border border-purple-500/40 animate-pulse">
            Speaking: Turn {currentTurnIdx + 1}/{turns.length} ({turns[currentTurnIdx]?.agent_name})
          </span>
        )}

        <button
          onClick={togglePlay}
          disabled={!isSupported}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold text-xs transition-all shadow ${
            isPlaying
              ? 'bg-amber-600 hover:bg-amber-500 text-white'
              : 'bg-indigo-600 hover:bg-indigo-500 text-white'
          }`}
        >
          {isPlaying ? (
            <>
              <Pause className="w-4 h-4" />
              <span>Pause Audio</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Listen to Debate</span>
            </>
          )}
        </button>

        {isPlaying && (
          <button
            onClick={stopAudio}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
