"""Token persistence to JSON file."""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from linkedin_poster.config import TOKENS_FILE, ensure_data_dir


class TokenStore:
    """Save, load, and clear OAuth tokens."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or str(TOKENS_FILE)

    def save(self, token_data: Dict[str, Any]) -> None:
        """Save token data to file."""
        ensure_data_dir()
        token_data["saved_at"] = datetime.utcnow().isoformat()
        with open(self.path, "w") as f:
            json.dump(token_data, f, indent=2)

    def load(self) -> Optional[Dict[str, Any]]:
        """Load token data from file. Returns None if not found."""
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def clear(self) -> None:
        """Remove stored tokens."""
        try:
            import os
            os.remove(self.path)
        except FileNotFoundError:
            pass

    def get_access_token(self) -> Optional[str]:
        """Get the access token if available."""
        data = self.load()
        if data:
            return data.get("access_token")
        return None

    def get_person_urn(self) -> Optional[str]:
        """Get the stored person URN."""
        data = self.load()
        if data:
            return data.get("person_urn")
        return None
