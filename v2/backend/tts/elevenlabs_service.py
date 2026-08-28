import os
import httpx
from pathlib import Path
from typing import List, Optional
from backend.schemas.models import DebateTurn
from dotenv import load_dotenv

# Load .env file safely
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
AUDIO_STORAGE_DIR = Path(__file__).parent.parent / "storage" / "audio"

# Voice ID Mappings for ElevenLabs Default Pre-made Voices
VOICE_MAP = {
    "Technical Agent": "pNInz6obpgDQGcFmaJgB",      # Adam (Analytical, firm male)
    "HR / Culture Agent": "21m00Tcm4TlvDq8ikWAM",     # Rachel (Warm, clear female)
    "Hiring Manager Agent": "VR6AewLTigWG4xSOukaG", # Arnold (Authoritative male)
    "Skeptic Agent": "YoZ0tZAc8m5pfTKxUEwm",        # Sam (Critical, deliberate male)
}

class ElevenLabsTTSService:
    """
    ElevenLabs Voice Debate Synthesis Service.
    Sequentially synthesizes Stage 3 DebateTurn list with distinct persona voices.
    """

    @staticmethod
    def _ensure_dir():
        AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    async def synthesize_debate_audio(cls, run_id: str, turns: List[DebateTurn]) -> Optional[str]:
        cls._ensure_dir()
        file_path = AUDIO_STORAGE_DIR / f"{run_id}.mp3"

        if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_elevenlabs_key_here":
            # Stub file for offline mode
            with open(file_path, "wb") as f:
                f.write(b"MOCK_AUDIO_HEADER_ELEVENLABS_FALLBACK")
            return f"/api/audio/{run_id}.mp3"

        combined_audio_bytes = bytearray()

        async with httpx.AsyncClient(timeout=30.0) as client:
            for turn in turns[:4]:  # Top debate turns
                voice_id = VOICE_MAP.get(turn.agent_name, "21m00Tcm4TlvDq8ikWAM")
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY
                }
                
                payload = {
                    "text": f"{turn.agent_name}, responding to {turn.responding_to}. Stance: {turn.stance}. {turn.message}",
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }

                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        combined_audio_bytes.extend(resp.content)
                except Exception:
                    continue

        if len(combined_audio_bytes) > 0:
            with open(file_path, "wb") as f:
                f.write(combined_audio_bytes)
            return f"/api/audio/{run_id}.mp3"

        # Fallback stub
        with open(file_path, "wb") as f:
            f.write(b"MOCK_AUDIO_HEADER_ELEVENLABS_FALLBACK")
        return f"/api/audio/{run_id}.mp3"
