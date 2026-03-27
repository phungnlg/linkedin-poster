"""LinkedIn OAuth 2.0 3-legged flow."""

import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs

import httpx

from linkedin_poster.config import (
    LINKEDIN_API_BASE,
    LINKEDIN_AUTH_URL,
    LINKEDIN_TOKEN_URL,
    OAUTH_SCOPES,
    Settings,
)
from linkedin_poster.auth.token_store import TokenStore


class _CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback."""

    auth_code: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            _CallbackHandler.auth_code = params["code"][0]
            self._respond(200, "Login successful! You can close this tab.")
        elif "error" in params:
            _CallbackHandler.error = params.get("error_description", params["error"])[0]
            self._respond(400, f"Login failed: {_CallbackHandler.error}")
        else:
            self._respond(400, "Unknown callback response.")

    def _respond(self, status: int, message: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = f"<html><body><h2>{message}</h2></body></html>"
        self.wfile.write(html.encode())

    def log_message(self, format: str, *args: object) -> None:
        pass  # Suppress server logs


class OAuthFlow:
    """Manages the LinkedIn OAuth 2.0 authorization flow."""

    def __init__(self, settings: Optional[Settings] = None, token_store: Optional[TokenStore] = None):
        self.settings = settings or Settings.load()
        self.token_store = token_store or TokenStore()

    def get_auth_url(self) -> str:
        """Generate the LinkedIn authorization URL."""
        self._state = secrets.token_urlsafe(32)
        params = {
            "response_type": "code",
            "client_id": self.settings.client_id,
            "redirect_uri": self.settings.redirect_uri,
            "state": self._state,
            "scope": OAUTH_SCOPES,
        }
        return f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

    def _is_remote_redirect(self) -> bool:
        """Check if redirect URI points to a remote server (not localhost)."""
        parsed = urlparse(self.settings.redirect_uri)
        return parsed.hostname not in ("localhost", "127.0.0.1")

    def run_login(self) -> bool:
        """Run the full OAuth login flow: open browser, capture code, exchange token."""
        error = self.settings.validate_credentials()
        if error:
            raise ValueError(error)

        auth_url = self.get_auth_url()
        webbrowser.open(auth_url)

        if self._is_remote_redirect():
            # Edge function handles token exchange - user will paste token via --token flag
            raise ValueError(
                "Using remote callback. After authorizing in the browser, "
                "copy the token and run:\n"
                "  linkedin-poster auth login --token PASTE_TOKEN_HERE"
            )

        # Local server mode
        _CallbackHandler.auth_code = None
        _CallbackHandler.error = None

        parsed = urlparse(self.settings.redirect_uri)
        port = parsed.port or 8080
        server = HTTPServer(("localhost", port), _CallbackHandler)
        server.handle_request()  # Handle single request
        server.server_close()

        if _CallbackHandler.error:
            raise ValueError(f"OAuth error: {_CallbackHandler.error}")
        if not _CallbackHandler.auth_code:
            raise ValueError("No authorization code received.")

        # Exchange code for token
        token_data = self._exchange_code(_CallbackHandler.auth_code)

        # Get user info for person URN
        person_urn = self._get_person_urn(token_data["access_token"])
        token_data["person_urn"] = person_urn

        self.token_store.save(token_data)
        return True

    def _exchange_code(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "redirect_uri": self.settings.redirect_uri,
        }
        resp = httpx.post(LINKEDIN_TOKEN_URL, data=data)
        resp.raise_for_status()
        return resp.json()

    def _get_person_urn(self, access_token: str) -> str:
        """Get the authenticated user's person URN."""
        resp = httpx.get(
            f"{LINKEDIN_API_BASE}/v2/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        user_info = resp.json()
        return f"urn:li:person:{user_info['id']}"
