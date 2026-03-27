"""Configuration and settings."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

DATA_DIR = Path.home() / ".linkedin-poster"
TOKENS_FILE = DATA_DIR / "tokens.json"
HISTORY_FILE = DATA_DIR / "history.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"

LINKEDIN_API_BASE = "https://api.linkedin.com"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_VERSION = "202603"

OAUTH_SCOPES = "w_member_social"


class Settings(BaseModel):
    """Application settings loaded from environment."""

    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080/callback"

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            client_id=os.getenv("LINKEDIN_CLIENT_ID", ""),
            client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", ""),
            redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback"),
        )

    def validate_credentials(self) -> Optional[str]:
        """Return error message if credentials are missing, None if valid."""
        if not self.client_id:
            return "LINKEDIN_CLIENT_ID not set. Copy .env.example to .env and fill in your credentials."
        if not self.client_secret:
            return "LINKEDIN_CLIENT_SECRET not set. Copy .env.example to .env and fill in your credentials."
        return None


def ensure_data_dir() -> Path:
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR
