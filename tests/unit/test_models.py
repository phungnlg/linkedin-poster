"""Tests for data models."""

from datetime import datetime

from linkedin_poster.models.poc import PocProject
from linkedin_poster.models.post import PostContent, PostRecord
from linkedin_poster.models.schedule import ScheduledPost


class TestPocProject:
    def test_create_minimal(self):
        poc = PocProject(
            name="Test",
            github_url="https://github.com/test/test",
            description="A test project.",
        )
        assert poc.name == "Test"
        assert poc.keywords == []
        assert poc.screenshots == []
        assert poc.demo_url is None

    def test_create_full(self):
        poc = PocProject(
            name="Full Project",
            github_url="https://github.com/test/full",
            description="Full project.",
            keywords=["Python", "CLI"],
            screenshots=["/path/to/img.png"],
            tech_stack=["Python", "httpx"],
            demo_url="https://demo.example.com",
        )
        assert len(poc.keywords) == 2
        assert poc.demo_url == "https://demo.example.com"

    def test_json_roundtrip(self, sample_poc):
        data = sample_poc.model_dump()
        restored = PocProject(**data)
        assert restored == sample_poc


class TestPostContent:
    def test_defaults(self):
        content = PostContent(commentary="Hello LinkedIn!")
        assert content.visibility == "PUBLIC"
        assert content.image_urns == []
        assert content.article_url is None

    def test_with_article(self):
        content = PostContent(
            commentary="Check this out",
            article_url="https://github.com/test/repo",
        )
        assert content.article_url is not None


class TestPostRecord:
    def test_create(self):
        record = PostRecord(
            post_urn="urn:li:share:123",
            poc_hash="abc123",
            text_preview="Test post...",
        )
        assert record.post_urn == "urn:li:share:123"
        assert isinstance(record.created_at, datetime)


class TestScheduledPost:
    def test_create(self):
        content = PostContent(commentary="Scheduled post")
        post = ScheduledPost(
            post_content=content,
            scheduled_at=datetime(2026, 4, 1, 10, 0),
        )
        assert post.published is False
        assert len(post.id) == 8
