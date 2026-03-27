"""Vercel Serverless Function - LinkedIn OAuth callback handler."""

import base64
import json
import os
from urllib.parse import parse_qs, urlparse

from http.server import BaseHTTPRequestHandler

import httpx

LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE = "https://api.linkedin.com"


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless handler for OAuth callback."""

    def do_GET(self):
        parsed = urlparse(self.path)
        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        error = params.get("error")
        if error:
            error_desc = params.get("error_description", error)
            self._send(400, f"Login failed: {error_desc}")
            return

        code = params.get("code")
        if not code:
            self._send(400, "No authorization code received.")
            return

        client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
        client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
        redirect_uri = os.environ.get("LINKEDIN_REDIRECT_URI", "")

        if not client_id or not client_secret:
            self._send(500, "Server missing LinkedIn credentials.")
            return

        # Exchange code for token
        try:
            resp = httpx.post(LINKEDIN_TOKEN_URL, data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
            })
            if resp.status_code != 200:
                self._send(500, f"Token exchange failed ({resp.status_code}): {resp.text}")
                return
            token_data = resp.json()
        except Exception as e:
            self._send(500, f"Token exchange failed: {e}")
            return

        # Get person URN
        try:
            access_token = token_data["access_token"]
            user_resp = httpx.get(
                f"{LINKEDIN_API_BASE}/v2/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_resp.raise_for_status()
            user_info = user_resp.json()
            person_urn = f"urn:li:person:{user_info['id']}"
            token_data["person_urn"] = person_urn
        except Exception as e:
            self._send(500, f"Failed to get user info: {e}")
            return

        # Encode token as base64 for CLI paste
        token_json = json.dumps(token_data)
        encoded = base64.b64encode(token_json.encode()).decode()

        html = f"""<!DOCTYPE html>
<html>
<head><title>LinkedIn Auth Success</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 600px; margin: 60px auto; padding: 20px; }}
  h2 {{ color: #0a66c2; }}
  .code-box {{ background: #f3f4f6; padding: 16px; border-radius: 8px; word-break: break-all;
    font-family: monospace; font-size: 13px; cursor: pointer; border: 2px solid #e5e7eb; }}
  .code-box:hover {{ border-color: #0a66c2; }}
  .copied {{ color: #16a34a; display: none; margin-top: 8px; }}
  .instructions {{ color: #6b7280; margin-top: 16px; }}
</style>
</head>
<body>
  <h2>Login Successful!</h2>
  <p>Copy this token code and paste it into your CLI:</p>
  <div class="code-box" onclick="copyToken()" id="token">{encoded}</div>
  <div class="copied" id="copied">Copied to clipboard!</div>
  <div class="instructions">
    <p>In your terminal, run:</p>
    <code>python -m linkedin_poster auth login --token PASTE_TOKEN_HERE</code>
  </div>
  <script>
    function copyToken() {{
      navigator.clipboard.writeText(document.getElementById('token').textContent);
      document.getElementById('copied').style.display = 'block';
    }}
  </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send(self, status, message):
        color = "#dc2626" if status >= 400 else "#0a66c2"
        html = f"""<!DOCTYPE html>
<html><head><title>LinkedIn Auth</title>
<style>body {{ font-family: -apple-system, sans-serif; max-width: 600px; margin: 60px auto; padding: 20px; }}
h2 {{ color: {color}; }}</style>
</head><body><h2>{message}</h2></body></html>"""
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
