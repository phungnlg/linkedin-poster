"""Scheduled post model."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from linkedin_poster.models.post import PostContent


class ScheduledPost(BaseModel):
    """A post scheduled for future publishing."""

    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:8])
    post_content: PostContent
    scheduled_at: datetime
    poc_config_path: Optional[str] = None
    template_name: Optional[str] = None
    published: bool = False
