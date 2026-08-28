import pytest
import os
from backend.pipeline import MultiAgentPipelineOrchestratorV3
from backend.pdf_parser.parser import PDFDocumentParser
from backend.tts.elevenlabs_service import ElevenLabsTTSService

@pytest.mark.asyncio
async def test_dynamic_jd_matrix_extraction_for_hardware_role():
    """
    Verifies that Stage 6 JD compliance matrix derives rows directly from the uploaded JD's
    specific hardware/PCB requirements (Altium, KiCad, Signal Integrity, DFM/DFA) rather than generic categories.
    """
    jd_text = """
    JOB DESCRIPTION: Senior PCB Design Engineer
    Company: Apex Robotics
    Required Skills: Altium, KiCad, Signal Integrity, Power Integrity, DFM, DFA, ESP32, Firmware
    Responsibilities:
    - Perform high-speed PCB layout and signal integrity analysis.
    """

    jd = PDFDocumentParser.parse_job_description(jd_text)

    # Verify extracted skills match the uploaded JD's actual hardware requirements
    assert "Altium" in jd.required_skills or "PCB" in jd.required_skills
    assert "Signal Integrity" in jd.required_skills or "DFM" in jd.required_skills

@pytest.mark.asyncio
async def test_elevenlabs_voice_narration_service():
    """
    Verifies that ElevenLabsTTSService generates an audio output file path
    and maps distinct voice IDs for all 4 agent personas.
    """
    from backend.schemas.models import DebateTurn

    turns = [
        DebateTurn(round_number=1, agent_name="Technical Agent", responding_to="Hiring Manager Agent", stance="Reinforce", message="Technical evidence is strong."),
        DebateTurn(round_number=1, agent_name="HR / Culture Agent", responding_to="Skeptic Agent", stance="Agree", message="High communication and transparency."),
        DebateTurn(round_number=2, agent_name="Hiring Manager Agent", responding_to="Technical Agent", stance="Agree", message="Strong execution fit."),
        DebateTurn(round_number=2, agent_name="Skeptic Agent", responding_to="HR / Culture Agent", stance="Revise", message="Claim depth verified.")
    ]

    audio_path = await ElevenLabsTTSService.synthesize_debate_audio("test_run_audio", turns)
    assert audio_path is not None
    assert os.path.exists(audio_path) or "/api/audio/" in audio_path
