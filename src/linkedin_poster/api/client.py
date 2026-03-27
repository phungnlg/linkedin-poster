"""Async httpx client for LinkedIn API."""

import asyncio
from typing import Any, Dict, Optional

import httpx

from linkedin_poster.config import LINKEDIN_API_BASE, LINKEDIN_API_VERSION
from linkedin_poster.auth.token_store import TokenStore


class LinkedInClient:
    """HTTP client with LinkedIn API headers and rate limit retry."""

    MAX_RETRIES = 3
    RETRY_WAIT = 2  # seconds

    def __init__(self, token_store: Optional[TokenStore] = None):
        self.token_store = token_store or TokenStore()
        self._client: Optional[httpx.AsyncClient] = None

    def _get_headers(self) -> Dict[str, str]:
        access_token = self.token_store.get_access_token()
        if not access_token:
            raise ValueError("Not authenticated. Run 'linkedin-poster auth login' first.")
        return {
            "Authorization": f"Bearer {access_token}",
            "LinkedIn-Version": LINKEDIN_API_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=LINKEDIN_API_BASE,
                headers=self._get_headers(),
                timeout=30.0,
            )
        return self._client

    async def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Make an API request with rate limit retry."""
        client = await self._get_client()
        for attempt in range(self.MAX_RETRIES):
            resp = await client.request(method, path, **kwargs)
            if resp.status_code == 429:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_WAIT * (attempt + 1))
                    continue
            resp.raise_for_status()
            return resp
        return resp  # Last response even if 429

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("DELETE", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PUT", path, **kwargs)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
