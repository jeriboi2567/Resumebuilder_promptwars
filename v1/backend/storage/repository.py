import os
import json
from pathlib import Path
from typing import List, Optional
from backend.schemas.models import PipelineRunResult

STORAGE_DIR = Path(__file__).parent / "runs"

class RunStorageRepository:
    """
    Persistence layer for candidate evaluation pipeline runs.
    Saves full PipelineRunResult (profile, opinions, debate, decision, report) as JSON files.
    """

    @staticmethod
    def _ensure_dir():
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def save_run(cls, result: PipelineRunResult) -> str:
        cls._ensure_dir()
        file_path = STORAGE_DIR / f"{result.run_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        return str(file_path)

    @classmethod
    def get_run(cls, run_id: str) -> Optional[PipelineRunResult]:
        cls._ensure_dir()
        file_path = STORAGE_DIR / f"{run_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return PipelineRunResult.model_validate(data)

    @classmethod
    def list_runs(cls) -> List[dict]:
        cls._ensure_dir()
        runs = []
        for p in STORAGE_DIR.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    runs.append({
                        "run_id": data.get("run_id"),
                        "timestamp": data.get("timestamp"),
                        "candidate_name": data.get("profile", {}).get("candidate_name"),
                        "role_applied": data.get("profile", {}).get("role_applied"),
                        "final_recommendation": data.get("final_decision", {}).get("recommendation"),
                        "confidence": data.get("final_decision", {}).get("confidence")
                    })
            except Exception:
                continue
        return sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)
