"""Tests for template engine and templates."""

import pytest

from linkedin_poster.services.template_engine import TemplateEngine
from linkedin_poster.models.poc import PocProject


@pytest.fixture
def poc():
    return PocProject(
        name="Safari Ad Blocker",
        github_url="https://github.com/tranthienhau/safari-ad-blocker",
        description="Native iOS Safari Content Blocker with SwiftUI.",
        keywords=["Safari", "iOS", "Swift", "SwiftUI", "Privacy"],
        tech_stack=["Swift 6", "SwiftUI", "Safari Web Extension"],
    )


class TestTemplateEngine:
    def test_render_poc_showcase(self, poc):
        text = TemplateEngine.render("poc_showcase", poc)
        assert "Safari Ad Blocker" in text
        assert poc.github_url in text
        assert "#Safari" in text

    def test_render_tech_insight(self, poc):
        text = TemplateEngine.render("tech_insight", poc)
        assert "Swift 6" in text
        assert poc.github_url in text

    def test_render_project_update(self, poc):
        text = TemplateEngine.render("project_update", poc)
        assert "Project update" in text
        assert poc.github_url in text

    def test_unknown_template(self, poc):
        with pytest.raises(ValueError, match="Unknown template"):
            TemplateEngine.render("nonexistent", poc)

    def test_list_templates(self):
        names = TemplateEngine.list_templates()
        assert "poc_showcase" in names
        assert "tech_insight" in names
        assert "project_update" in names
        assert len(names) == 3


class TestPocShowcaseTemplate:
    def test_includes_tech_stack(self, poc):
        text = TemplateEngine.render("poc_showcase", poc)
        assert "Swift 6" in text
        assert "SwiftUI" in text

    def test_includes_hashtags(self, poc):
        text = TemplateEngine.render("poc_showcase", poc)
        assert "#Safari" in text
        assert "#iOS" in text

    def test_no_demo_url(self, poc):
        text = TemplateEngine.render("poc_showcase", poc)
        assert "Demo:" not in text

    def test_with_demo_url(self):
        poc = PocProject(
            name="Test",
            github_url="https://github.com/test/test",
            description="Test project",
            keywords=["Test"],
            demo_url="https://demo.example.com",
        )
        text = TemplateEngine.render("poc_showcase", poc)
        assert "Demo: https://demo.example.com" in text


class TestTechInsightTemplate:
    def test_uses_primary_tech(self, poc):
        text = TemplateEngine.render("tech_insight", poc)
        assert "Swift 6" in text

    def test_key_areas(self, poc):
        text = TemplateEngine.render("tech_insight", poc)
        assert "Key areas:" in text


class TestProjectUpdateTemplate:
    def test_stack_line(self, poc):
        text = TemplateEngine.render("project_update", poc)
        assert "Stack:" in text
        assert "Swift 6" in text
