import os
import asyncio
from pathlib import Path
from typing import List, Optional
from backend.schemas.models import DebateTurn

VOICE_MAP = {
    "Technical Agent": "pNInz6obpgDQGcFmaJgB",      # Adam (analytical)
    "HR / Culture Agent": "21m00Tcm4TlvDq8ikWAM",   # Rachel (warm)
    "Hiring Manager Agent": "VR6AewLTigWG4xSOukaG", # Arnold (authoritative)
    "Skeptic Agent": "YoZ0tZAc8m5pfTKxUEwm"         # Sam (critical)
}

class ElevenLabsTTSService:
    @staticmethod
    async def synthesize_debate_audio(run_id: str, turns: List[DebateTurn]) -> Optional[str]:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            return f"/api/audio/{run_id}.mp3"

        audio_dir = Path(__file__).parent.parent / "storage" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        file_path = audio_dir / f"{run_id}.mp3"

        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(b"MPEG_AUDIO_HEADER_SYNTHESIZED_NARRATION_PLACEHOLDER")

        return f"/api/audio/{run_id}.mp3"
