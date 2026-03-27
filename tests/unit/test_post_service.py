"""Tests for post service."""

import json

import pytest

from linkedin_poster.services.post_service import PostService
from linkedin_poster.models.poc import PocProject


class TestPostService:
    def test_load_poc_config(self, sample_poc_config, sample_poc):
        service = PostService()
        poc = service.load_poc_config(sample_poc_config)
        assert poc.name == sample_poc.name
        assert poc.github_url == sample_poc.github_url

    def test_generate_text_default_template(self, sample_poc):
        service = PostService()
        text = service.generate_text(sample_poc)
        assert sample_poc.name in text
        assert sample_poc.github_url in text

    def test_generate_text_tech_insight(self, sample_poc):
        service = PostService()
        text = service.generate_text(sample_poc, "tech_insight")
        assert sample_poc.github_url in text

    def test_draft_returns_content(self, sample_poc_config):
        service = PostService()
        content = service.draft(sample_poc_config)
        assert content.commentary
        assert content.article_url

    def test_draft_text(self):
        service = PostService()
        content = service.draft_text("Hello LinkedIn!")
        assert content.commentary == "Hello LinkedIn!"

    def test_load_invalid_config(self, tmp_path):
        bad_config = tmp_path / "bad.json"
        bad_config.write_text("{}")
        service = PostService()
        with pytest.raises(Exception):
            service.load_poc_config(str(bad_config))
