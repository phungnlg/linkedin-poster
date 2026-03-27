"""Tests for config module."""

import os
from unittest.mock import patch

from linkedin_poster.config import Settings, ensure_data_dir, DATA_DIR


class TestSettings:
    def test_load_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.load()
            assert settings.client_id == ""
            assert settings.redirect_uri == "http://localhost:8080/callback"

    def test_load_from_env(self):
        env = {
            "LINKEDIN_CLIENT_ID": "test_id",
            "LINKEDIN_CLIENT_SECRET": "test_secret",
            "LINKEDIN_REDIRECT_URI": "http://localhost:9090/cb",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.load()
            assert settings.client_id == "test_id"
            assert settings.client_secret == "test_secret"
            assert settings.redirect_uri == "http://localhost:9090/cb"

    def test_validate_missing_id(self):
        settings = Settings(client_id="", client_secret="secret")
        error = settings.validate_credentials()
        assert error is not None
        assert "CLIENT_ID" in error

    def test_validate_missing_secret(self):
        settings = Settings(client_id="id", client_secret="")
        error = settings.validate_credentials()
        assert error is not None
        assert "CLIENT_SECRET" in error

    def test_validate_ok(self):
        settings = Settings(client_id="id", client_secret="secret")
        assert settings.validate_credentials() is None


class TestEnsureDataDir:
    def test_creates_dir(self, tmp_path):
        from linkedin_poster import config
        original = config.DATA_DIR
        config.DATA_DIR = tmp_path / "test_linkedin_poster"
        try:
            result = ensure_data_dir()
            assert result.exists()
        finally:
            config.DATA_DIR = original
