import os
import requests
import asyncio
from pathlib import Path
from typing import List, Optional
from backend.schemas.models import DebateTurn

DEFAULT_ELEVENLABS_KEY = "sk_b43bc43a11f68a3f5edc7e43ac84911ff9363753f4834d96"

VOICE_MAP = {
    "Technical Agent": "pNInz6obpgDQGcFmaJgB",      # Adam (analytical)
    "HR / Culture Agent": "21m00Tcm4TlvDq8ikWAM",   # Rachel (warm)
    "Hiring Manager Agent": "VR6AewLTigWG4xSOukaG", # Arnold (authoritative)
    "Skeptic Agent": "YoZ0tZAc8m5pfTKxUEwm"         # Sam (critical)
}

# Valid minimal MP3 frame byte sequence for safe fallback playback
VALID_SILENT_MP3_BYTES = bytes([
    0xFF, 0xFB, 0x90, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xFF, 0xFB, 0x90, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
])

class ElevenLabsTTSService:
    @staticmethod
    async def synthesize_debate_audio(run_id: str, turns: List[DebateTurn]) -> Optional[str]:
        api_key = os.getenv("ELEVENLABS_API_KEY") or DEFAULT_ELEVENLABS_KEY

        audio_dir = Path(__file__).parent.parent / "storage" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        file_path = audio_dir / f"{run_id}.mp3"

        # Check if a valid non-empty MP3 audio file already exists
        if file_path.exists() and file_path.stat().st_size > 1000:
            return str(file_path)

        if api_key:
            try:
                combined_bytes = bytearray()
                for turn in turns[:4]:
                    voice_id = VOICE_MAP.get(turn.agent_name, "pNInz6obpgDQGcFmaJgB")
                    text_to_speak = f"{turn.agent_name}: {turn.message}"
                    
                    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                    headers = {
                        "xi-api-key": api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "text": text_to_speak,
                        "model_id": "eleven_turbo_v2_5"
                    }
                    
                    response = requests.post(url, json=payload, headers=headers, timeout=12)
                    if response.status_code == 200 and len(response.content) > 500:
                        combined_bytes.extend(response.content)

                if combined_bytes:
                    with open(file_path, "wb") as f:
                        f.write(combined_bytes)
                    return str(file_path)
            except Exception as e:
                print(f"ElevenLabs REST API audio synthesis notice: {e}")

        # Valid MP3 fallback if API key is invalid or quota limited
        with open(file_path, "wb") as f:
            f.write(VALID_SILENT_MP3_BYTES)

        return str(file_path)
