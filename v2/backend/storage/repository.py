import os
import json
from pathlib import Path
from typing import List, Optional, Dict
from backend.schemas.models import BatchPipelineRunResult, PipelineRunResultV2

STORAGE_DIR = Path(__file__).parent / "runs"
AUDIO_DIR = Path(__file__).parent / "audio"

class RunStorageRepositoryV2:
    @staticmethod
    def _ensure_dirs():
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def save_batch_run(cls, result: BatchPipelineRunResult) -> str:
        cls._ensure_dirs()
        file_path = STORAGE_DIR / f"{result.batch_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.model_dump_json(indent=2))
        return str(file_path)

    @classmethod
    def get_batch_run(cls, batch_id: str) -> Optional[BatchPipelineRunResult]:
        cls._ensure_dirs()
        file_path = STORAGE_DIR / f"{batch_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return BatchPipelineRunResult.model_validate(data)

    @classmethod
    def list_batch_runs(cls) -> List[dict]:
        cls._ensure_dirs()
        runs = []
        for p in STORAGE_DIR.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    runs.append({
                        "batch_id": data.get("batch_id"),
                        "timestamp": data.get("timestamp"),
                        "jd_title": data.get("job_description", {}).get("title"),
                        "candidate_count": len(data.get("candidate_results", {}))
                    })
            except Exception:
                continue
        return sorted(runs, key=lambda x: x.get("timestamp", ""), reverse=True)
