"""POC project model."""

from typing import List, Optional

from pydantic import BaseModel


class PocProject(BaseModel):
    """Represents a GitHub POC project for LinkedIn showcase."""

    name: str
    github_url: str
    description: str
    keywords: List[str] = []
    screenshots: List[str] = []
    tech_stack: List[str] = []
    demo_url: Optional[str] = None
