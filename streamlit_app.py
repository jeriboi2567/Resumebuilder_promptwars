import os
import sys
import asyncio
from pathlib import Path
import streamlit as st

# Add v3 to sys.path so backend imports work seamlessly when deployed on Streamlit Cloud
v3_path = Path(__file__).parent / "v3"
if str(v3_path) not in sys.path:
    sys.path.insert(0, str(v3_path))

from backend.pipeline import MultiAgentPipelineOrchestratorV3
from backend.schemas.models import HiringRoleV3, PipelineRunResultV2, JobDescription
from backend.pdf_parser.parser import PDFDocumentParser
from backend.storage.repository import RoleStorageRepositoryV3

# Streamlit Page Configuration
st.set_page_config(
    page_title="Multi-Agent Candidate Evaluation System V3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme elegance
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background-color: #0f172a;
    }
    .agent-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .badge-hire {
        background-color: #059669;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: bold;
    }
    .badge-nohire {
        background-color: #e11d48;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: bold;
    }
    .quote-box {
        background-color: #0f172a;
        border-left: 3px solid #6366f1;
        padding: 8px 12px;
        margin: 6px 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to run async pipeline synchronously in Streamlit
def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

# Initialize Hackathon Sample Data Session State
@st.cache_resource
def get_sample_role() -> HiringRoleV3:
    hackathon_dir = Path(__file__).parent / "hackathon"
    sample_dir = Path(__file__).parent / "v2" / "sample_data"

    if hackathon_dir.exists():
        jd_p = hackathon_dir / "02_Job_Description.pdf"
        ra_p = hackathon_dir / "03_Resume_A.pdf"
        ta_p = hackathon_dir / "05_Transcript_A.pdf"
        rb_p = hackathon_dir / "04_Resume_B.pdf"
        tb_p = hackathon_dir / "06_Transcript_B.pdf"
    else:
        jd_p = sample_dir / "01_Job_Description.txt"
        ra_p = sample_dir / "03_Resume_A.txt"
        ta_p = sample_dir / "05_Transcript_A.txt"
        rb_p = sample_dir / "04_Resume_B.txt"
        tb_p = sample_dir / "06_Transcript_B.txt"

    def read_file(p: Path) -> str:
        if p.suffix.lower() == ".pdf":
            with open(p, "rb") as f:
                text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(f.read())
                return text
        else:
            with open(p, "r", encoding="utf-8") as f:
                return f.read()

    jd_text = read_file(jd_p)
    ra_text = read_file(ra_p)
    ta_text = read_file(ta_p)
    rb_text = read_file(rb_p)
    tb_text = read_file(tb_p)

    role_id = "role_cargonet_ai"
    candidate_pairs = [
        ("cand_A", ra_text, ta_text),
        ("cand_B", rb_text, tb_text)
    ]

    return run_async(MultiAgentPipelineOrchestratorV3.process_role_candidates(
        role_id=role_id,
        jd_text=jd_text,
        candidate_pairs=candidate_pairs
    ))

# Header Banner
st.title("🤖 Multi-Agent Candidate Evaluation System V3")
st.caption("General-Purpose Evidentiary Candidate Evaluation Platform • Hackathon Release")

# Load initial role into session state if not set
if "current_role" not in st.session_state:
    st.session_state["current_role"] = get_sample_role()

active_role: HiringRoleV3 = st.session_state["current_role"]

# Sidebar Navigation & General-Purpose Role Creation
with st.sidebar:
    st.header("🏢 Employer Hiring Control")
    st.subheader("Current Hiring Role")
    st.info(f"**{active_role.job_description.title}**\n\n{active_role.job_description.company}")

    st.markdown("---")
    st.subheader("➕ Add Candidate to Current Role")
    cand_resume_file = st.file_uploader("Upload Candidate Resume (PDF/TXT)", type=["pdf", "txt"], key="cand_res")
    cand_transcript_file = st.file_uploader("Upload Interview Transcript (PDF/TXT)", type=["pdf", "txt"], key="cand_tr")

    if st.button("Evaluate Candidate & Update Stage 6"):
        if cand_resume_file and cand_transcript_file:
            with st.spinner("Running 5-stage evidentiary evaluation and updating Stage 6 comparison..."):
                r_bytes = cand_resume_file.read()
                t_bytes = cand_transcript_file.read()
                r_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(r_bytes)
                t_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(t_bytes)

                cand_id = f"cand_{os.urandom(3).hex()}"
                updated_role = run_async(MultiAgentPipelineOrchestratorV3.process_role_candidates(
                    role_id=active_role.role_id,
                    jd_text=active_role.job_description.raw_text,
                    candidate_pairs=[(cand_id, r_text, t_text)]
                ))
                st.session_state["current_role"] = updated_role
                st.success("Candidate evaluated successfully!")
                st.rerun()
        else:
            st.error("Please upload both a Resume and Transcript file.")

    st.markdown("---")
    st.subheader("📝 Create New Hiring Role (New JD)")
    new_jd_file = st.file_uploader("Upload New Job Description (PDF/TXT)", type=["pdf", "txt"], key="new_jd")
    if st.button("Create New Hiring Role"):
        if new_jd_file:
            with st.spinner("Parsing Job Description & creating role..."):
                jd_bytes = new_jd_file.read()
                jd_text, _ = PDFDocumentParser.extract_text_from_pdf_bytes(jd_bytes)
                role_id = f"role_{os.urandom(4).hex()}"
                new_role = run_async(MultiAgentPipelineOrchestratorV3.process_role_candidates(
                    role_id=role_id,
                    jd_text=jd_text,
                    candidate_pairs=[]
                ))
                st.session_state["current_role"] = new_role
                st.success("New Hiring Role created!")
                st.rerun()

# Tabs Navigation
tab_stage6, tab_individual, tab_jd = st.tabs([
    "📊 Stage 6: Side-by-Side Comparison",
    "🔍 Stage 1-5: Individual Candidate Deep-Dive",
    "📄 Job Description & Requirements"
])

# TAB 1: STAGE 6 COMPARISON
with tab_stage6:
    st.header("Stage 6: Additive Comparative Ranking Engine")
    
    if active_role.stage6_comparison:
        comp = active_role.stage6_comparison

        col_count, col_top = st.columns(2)
        col_count.metric("Accumulated Candidates", len(comp.rankings))
        if comp.rankings:
            col_top.metric("Rank #1 Candidate", comp.rankings[0].candidate_name, f"Recommendation: {comp.rankings[0].final_recommendation}")

        st.subheader("🏆 Evidence-Weighted Candidate Ranking")
        for item in comp.rankings:
            with st.container():
                cols = st.columns([1, 4, 2])
                cols[0].markdown(f"### #{item.rank}")
                cols[1].markdown(f"**{item.candidate_name}** ({item.candidate_id})\n\n" + "\n".join([f"• {d}" for d in item.key_differentiators]))
                cols[2].markdown(f"**Recommendation:** `{item.final_recommendation}`\n\nPanel Confidence: `{int(item.confidence*100)}%`")
                st.markdown("---")

        st.subheader("📋 Shared Job Description Requirement Compliance Matrix")
        matrix_rows = []
        for req_row in comp.jd_compliance_matrix:
            row_dict = {"Requirement": req_row.requirement}
            for rank_item in comp.rankings:
                eval_data = req_row.candidate_evaluations.get(rank_item.candidate_id, {"status": "Not Assessed", "detail": "N/A"})
                row_dict[rank_item.candidate_name] = f"{eval_data['status']} ({eval_data['detail']})"
            matrix_rows.append(row_dict)

        st.dataframe(matrix_rows, use_container_width=True)

        st.subheader("💡 Panel Ranking Rationale")
        st.info(comp.comparison_rationale)
    else:
        st.warning("No candidates evaluated yet for this hiring role. Upload candidate files in the sidebar.")

# TAB 2: INDIVIDUAL DEEP-DIVE
with tab_individual:
    cand_ids = list(active_role.candidate_results.keys())
    if cand_ids:
        selected_cand_id = st.selectbox(
            "Select Candidate for 5-Stage Deep-Dive:",
            options=cand_ids,
            format_func=lambda cid: f"{active_role.candidate_results[cid].profile.candidate_name} ({active_role.candidate_results[cid].final_decision.recommendation})"
        )

        res: PipelineRunResultV2 = active_role.candidate_results[selected_cand_id]

        st.header(f"Candidate Evaluation Deep-Dive: {res.profile.candidate_name}")
        st.caption(f"Candidate ID: {res.profile.candidate_id} | Role Applied: {res.profile.role_applied}")

        col_rec, col_conf = st.columns(2)
        col_rec.metric("Final Recommendation", res.final_decision.recommendation)
        col_conf.metric("Panel Confidence", f"{int(res.final_decision.confidence*100)}%")

        st.markdown("---")

        # Stage 2 Agent Opinions
        st.subheader("Stage 2: Four Architecturally Isolated Agent Personas")
        grid_cols = st.columns(2)
        for idx, (agent_name, op) in enumerate(res.independent_opinions.opinions.items()):
            with grid_cols[idx % 2]:
                st.markdown(f"### {agent_name}")
                st.markdown(f"**Verdict:** `{op.verdict}` (Score: `{op.overall_score or 'N/A'}`)")
                st.write(op.reasoning)
                if op.supporting_quotes:
                    st.markdown("**Cited Quotes:**")
                    for q in op.supporting_quotes:
                        st.markdown(f"> *\"{q.quote}\"* ({q.source})")
                if op.insufficient_dimensions:
                    st.warning(f"**Not Assessed:** {', '.join(op.insufficient_dimensions)}")
                st.markdown("---")

        # Stage 3 Debate Thread
        st.subheader("Stage 3: Multi-Turn Structured Deliberation & Debate Transcript")
        st.markdown("**Post-Debate Stance Deltas:**")
        delta_table = []
        for name, delta in res.debate_state.stance_deltas.items():
            delta_table.append({
                "Agent Persona": name,
                "Initial Verdict": f"{delta.verdict_before} ({delta.score_before})",
                "Post-Debate Verdict": f"{delta.verdict_after} ({delta.score_after})",
                "Position Changed?": "YES (REVISED)" if delta.changed else "NO (FIRM)",
                "Driver": delta.change_reason
            })
        st.table(delta_table)

        st.markdown("**Turn-by-Turn Debate Dialogue Log:**")
        for turn in res.debate_state.turns:
            st.markdown(f"**Round {turn.round_number} - {turn.agent_name}** *(responding to {turn.responding_to})* [`{turn.stance}`]:")
            st.markdown(f"> \"{turn.message}\"")
            if turn.cites_quote:
                st.caption(f"Cited Evidence: {turn.cites_quote}")
            st.markdown("---")

        # Section B Rule
        st.subheader("Section B: Not Assessed / Insufficient Evidence (No-Guessing Rule)")
        if res.report.not_assessed_dimensions:
            for na in res.report.not_assessed_dimensions:
                st.warning(f"**[{na['agent']}] {na['dimension']}**: {na['reason']}")
        else:
            st.success("All JD evaluation dimensions had verified source evidence.")

        st.subheader("Decision Rationale")
        st.info(res.final_decision.decision_rationale)
    else:
        st.info("No candidate evaluations available yet.")

# TAB 3: JOB DESCRIPTION DETAILS
with tab_jd:
    st.header(f"Job Description: {active_role.job_description.title}")
    st.caption(f"Company: {active_role.job_description.company}")

    st.subheader("Required Skills")
    st.write(", ".join(active_role.job_description.required_skills))

    st.subheader("Responsibilities")
    for resp in active_role.job_description.responsibilities:
        st.markdown(f"- {resp}")

    st.subheader("Qualifications")
    for qual in active_role.job_description.qualifications:
        st.markdown(f"- {qual}")
