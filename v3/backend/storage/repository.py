import os
import json
from pathlib import Path
from typing import List, Optional, Dict
from backend.schemas.models import (
    HiringRoleV3, BatchPipelineRunResult, PipelineRunResultV2, JobDescription
)

ROLES_DIR = Path(__file__).parent / "roles"
AUDIO_DIR = Path(__file__).parent / "audio"

class RoleStorageRepositoryV3:
    @staticmethod
    def _ensure_dirs():
        ROLES_DIR.mkdir(parents=True, exist_ok=True)
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def save_role(cls, role: HiringRoleV3) -> str:
        cls._ensure_dirs()
        file_path = ROLES_DIR / f"{role.role_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(role.model_dump_json(indent=2))
        return str(file_path)

    @classmethod
    def get_role(cls, role_id: str) -> Optional[HiringRoleV3]:
        cls._ensure_dirs()
        file_path = ROLES_DIR / f"{role_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return HiringRoleV3.model_validate(data)

    @classmethod
    def list_roles(cls) -> List[dict]:
        cls._ensure_dirs()
        roles = []
        for p in ROLES_DIR.glob("*.json"):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    roles.append({
                        "role_id": data.get("role_id"),
                        "title": data.get("job_description", {}).get("title"),
                        "company": data.get("job_description", {}).get("company"),
                        "candidate_count": len(data.get("candidate_results", {})),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at")
                    })
            except Exception:
                continue
        return sorted(roles, key=lambda x: x.get("updated_at", ""), reverse=True)
