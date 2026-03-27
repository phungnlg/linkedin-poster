"""JSON-based post scheduler."""

import json
from datetime import datetime
from typing import List, Optional

from linkedin_poster.config import SCHEDULE_FILE, ensure_data_dir
from linkedin_poster.models.schedule import ScheduledPost
from linkedin_poster.models.post import PostContent


class Scheduler:
    """Add, list, and run scheduled posts from JSON storage."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or str(SCHEDULE_FILE)

    def _load(self) -> List[dict]:
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, items: List[dict]) -> None:
        ensure_data_dir()
        with open(self.path, "w") as f:
            json.dump(items, f, indent=2, default=str)

    def add(self, post: ScheduledPost) -> str:
        """Add a scheduled post. Returns the schedule ID."""
        items = self._load()
        items.append(post.model_dump())
        self._save(items)
        return post.id

    def list_pending(self) -> List[ScheduledPost]:
        """Return all unpublished scheduled posts."""
        items = self._load()
        return [
            ScheduledPost(**item) for item in items
            if not item.get("published", False)
        ]

    def get_due(self) -> List[ScheduledPost]:
        """Return scheduled posts that are due for publishing."""
        now = datetime.utcnow()
        pending = self.list_pending()
        return [p for p in pending if p.scheduled_at <= now]

    def mark_published(self, schedule_id: str) -> None:
        """Mark a scheduled post as published."""
        items = self._load()
        for item in items:
            if item.get("id") == schedule_id:
                item["published"] = True
                break
        self._save(items)

    def remove(self, schedule_id: str) -> bool:
        """Remove a scheduled post. Returns True if found and removed."""
        items = self._load()
        new_items = [i for i in items if i.get("id") != schedule_id]
        if len(new_items) == len(items):
            return False
        self._save(new_items)
        return True
