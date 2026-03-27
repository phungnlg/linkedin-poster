"""Post content and record models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PostContent(BaseModel):
    """Content for a LinkedIn post."""

    commentary: str
    image_urns: List[str] = []
    article_url: Optional[str] = None
    visibility: str = "PUBLIC"


class PostRecord(BaseModel):
    """Record of a published post."""

    post_urn: str
    poc_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    text_preview: str
    template_name: Optional[str] = None
