"""Post history and deduplication."""

import hashlib
import json
from datetime import datetime
from typing import List, Optional

from linkedin_poster.config import HISTORY_FILE, ensure_data_dir
from linkedin_poster.models.post import PostRecord


class HistoryStore:
    """Record posts to JSON and detect duplicates."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or str(HISTORY_FILE)

    def _load_records(self) -> List[dict]:
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_records(self, records: List[dict]) -> None:
        ensure_data_dir()
        with open(self.path, "w") as f:
            json.dump(records, f, indent=2, default=str)

    def add(self, record: PostRecord) -> None:
        """Add a post record to history."""
        records = self._load_records()
        records.append(record.model_dump())
        self._save_records(records)

    def list_records(self) -> List[PostRecord]:
        """Return all post records."""
        raw = self._load_records()
        return [PostRecord(**r) for r in raw]

    def is_duplicate(self, poc_hash: str) -> bool:
        """Check if a post with this POC hash already exists."""
        records = self._load_records()
        return any(r.get("poc_hash") == poc_hash for r in records)

    @staticmethod
    def compute_hash(config_path: str) -> str:
        """Compute a hash from a POC config file for dedup."""
        try:
            with open(config_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except FileNotFoundError:
            return hashlib.sha256(config_path.encode()).hexdigest()[:16]
