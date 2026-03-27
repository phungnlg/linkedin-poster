"""Integration tests for OAuth flow."""

from urllib.parse import urlparse, parse_qs

from linkedin_poster.auth.oauth import OAuthFlow
from linkedin_poster.config import Settings, LINKEDIN_AUTH_URL


class TestOAuthUrlGeneration:
    def test_auth_url_contains_params(self):
        settings = Settings(client_id="test_id", client_secret="test_secret")
        flow = OAuthFlow(settings)
        url = flow.get_auth_url()

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert "linkedin.com" in parsed.netloc
        assert params["client_id"] == ["test_id"]
        assert params["response_type"] == ["code"]
        assert "openid" in params["scope"][0]
        assert "w_member_social" in params["scope"][0]

    def test_auth_url_has_state(self):
        settings = Settings(client_id="test_id", client_secret="test_secret")
        flow = OAuthFlow(settings)
        url = flow.get_auth_url()

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        assert "state" in params
        assert len(params["state"][0]) > 10  # Should be a secure random string

    def test_auth_url_redirect_uri(self):
        settings = Settings(
            client_id="id",
            client_secret="secret",
            redirect_uri="http://localhost:9090/cb",
        )
        flow = OAuthFlow(settings)
        url = flow.get_auth_url()

        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        assert params["redirect_uri"] == ["http://localhost:9090/cb"]
