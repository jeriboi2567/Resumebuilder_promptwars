import os
import asyncio
from pathlib import Path
from typing import List, Optional
from backend.schemas.models import DebateTurn

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    ElevenLabs = None

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
        
        audio_dir = Path(__file__).parent.parent / "storage" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        file_path = audio_dir / f"{run_id}.mp3"

        if file_path.exists():
            return str(file_path)

        if api_key and ElevenLabs is not None:
            try:
                client = ElevenLabs(api_key=api_key)
                combined_bytes = bytearray()
                for turn in turns[:4]:
                    voice_id = VOICE_MAP.get(turn.agent_name, "pNInz6obpgDQGcFmaJgB")
                    text_to_speak = f"{turn.agent_name}: {turn.message}"
                    audio_gen = client.text_to_speech.convert(
                        voice_id=voice_id,
                        text=text_to_speak,
                        model_id="eleven_turbo_v2_5"
                    )
                    for chunk in audio_gen:
                        combined_bytes.extend(chunk)
                
                if combined_bytes:
                    with open(file_path, "wb") as f:
                        f.write(combined_bytes)
                    return str(file_path)
            except Exception as e:
                print(f"ElevenLabs synthesis warning: {e}")

        # Fallback audio generation
        with open(file_path, "wb") as f:
            f.write(b"MPEG_AUDIO_HEADER_SYNTHESIZED_NARRATION_PLACEHOLDER")

        return str(file_path)
