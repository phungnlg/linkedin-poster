"""Integration tests for API client."""

import pytest
import httpx
import respx

from linkedin_poster.api.client import LinkedInClient
from linkedin_poster.auth.token_store import TokenStore


@pytest.fixture
def mock_token_store(tmp_path):
    store = TokenStore(path=str(tmp_path / "tokens.json"))
    store.save({"access_token": "test_token", "person_urn": "urn:li:person:123"})
    return store


class TestLinkedInClient:
    def test_headers(self, mock_token_store):
        client = LinkedInClient(token_store=mock_token_store)
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer test_token"
        assert "LinkedIn-Version" in headers
        assert headers["X-Restli-Protocol-Version"] == "2.0.0"

    def test_no_token_raises(self, tmp_path):
        store = TokenStore(path=str(tmp_path / "empty_tokens.json"))
        client = LinkedInClient(token_store=store)
        with pytest.raises(ValueError, match="Not authenticated"):
            client._get_headers()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_request(self, mock_token_store):
        client = LinkedInClient(token_store=mock_token_store)

        route = respx.get("https://api.linkedin.com/rest/posts").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        resp = await client.get("/rest/posts")
        assert resp.status_code == 200
        assert route.called
        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_retry_on_429(self, mock_token_store):
        client = LinkedInClient(token_store=mock_token_store)
        client.RETRY_WAIT = 0  # Speed up test

        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return httpx.Response(429)
            return httpx.Response(200, json={"ok": True})

        respx.get("https://api.linkedin.com/rest/test").mock(side_effect=side_effect)

        resp = await client.get("/rest/test")
        assert resp.status_code == 200
        assert call_count == 3
        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_request(self, mock_token_store):
        client = LinkedInClient(token_store=mock_token_store)

        route = respx.post("https://api.linkedin.com/rest/posts").mock(
            return_value=httpx.Response(
                201,
                headers={"x-restli-id": "urn:li:share:456"},
            )
        )

        resp = await client.post("/rest/posts", json={"author": "urn:li:person:123"})
        assert resp.status_code == 201
        assert route.called
        await client.close()
