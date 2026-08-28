import pytest
from backend.schemas.models import DebateTurn
from backend.tts.elevenlabs_service import ElevenLabsTTSService

@pytest.mark.asyncio
async def test_elevenlabs_audio_synthesis():
    turns = [
        DebateTurn(
            round_number=1,
            agent_name="Technical Agent",
            responding_to="Skeptic Agent",
            stance="Disagree",
            message="Alex's technical execution reducing P99 latency to 510ms is verified.",
            cites_quote="transcript [00:02:30]"
        )
    ]

    audio_url = await ElevenLabsTTSService.synthesize_debate_audio("test_run_01", turns)
    assert audio_url is not None
    assert "/api/audio/" in audio_url
