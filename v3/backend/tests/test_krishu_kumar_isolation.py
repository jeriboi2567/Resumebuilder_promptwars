import pytest
from backend.pipeline import MultiAgentPipelineOrchestratorV3

@pytest.mark.asyncio
async def test_krishu_kumar_strict_evidence_isolation():
    jd_text = """
    JOB DESCRIPTION: Hardware / PCB Design Engineer
    Company: Robotics Health Tech
    Required Skills: Altium, KiCad, PCB Layout, ESP32, STM32, C/C++, Firmware, DFM, Signal Integrity
    Responsibilities:
    - Design 4-layer PCB layouts for wearable hardware.
    - Perform DFM/DFA checks with contract manufacturers.
    - Write C/C++ firmware for sensor integration.
    """

    resume_text = """
    KRISHU KUMAR
    Hardware & Embedded Systems Engineer
    Experience:
    - Designed 4-layer PCB for ESP32 wearable health monitor using Altium Designer.
    - Developed RoboSoccer omni-directional drive system firmware in C/C++.
    - Implemented FPGA traffic light controller in Verilog.
    Skills: PCB Layout, Altium, KiCad, ESP32, STM32, C/C++, Verilog, DFM
    """

    transcript_text = """
    Interview Transcript - Candidate: Krishu Kumar
    Q1: Walk us through your 4-layer PCB layout process for the ESP32 wearable monitor.
    A1: I placed component footprints in Altium, set up ground planes for noise immunity, and ran DFM checks.
    Q2: How did you test the C/C++ firmware for the RoboSoccer drive system?
    A2: I used an oscilloscope and logic analyzer to verify PWM motor driver signals.
    """

    role_id = "role_hardware_pcb_test"
    role = await MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=jd_text,
        candidate_pairs=[("cand_krishu", resume_text, transcript_text)]
    )

    assert "cand_krishu" in role.candidate_results
    res = role.candidate_results["cand_krishu"]
    
    # 1. Confirm Candidate Profile Name & Skills
    assert res.profile.candidate_name == "Krishu Kumar"
    assert any(s.skill_name in ["PCB", "ESP32", "Altium", "KiCad", "C/C++"] for s in res.profile.skills)

    # 2. Strict Cross-Candidate Data Leakage Verification
    full_output_text = (
        res.final_decision.decision_rationale + " " +
        res.report.markdown_content + " " +
        " ".join([op.reasoning for op in res.independent_opinions.opinions.values()])
    ).lower()

    # Must NOT contain software incident phrases or previous candidate leakage
    assert "production incident" not in full_output_text
    assert "incident ownership" not in full_output_text
    assert "microservices" not in full_output_text
    assert "ananya" not in full_output_text

    # 3. Must contain Krishu's actual hardware domain evidence
    assert "pcb" in full_output_text or "esp32" in full_output_text or "altium" in full_output_text
