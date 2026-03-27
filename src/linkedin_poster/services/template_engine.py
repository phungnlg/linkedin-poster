"""Template engine - renders POC data into post text."""

from typing import Optional

from linkedin_poster.models.poc import PocProject
from linkedin_poster.templates.poc_showcase import PocShowcaseTemplate
from linkedin_poster.templates.tech_insight import TechInsightTemplate
from linkedin_poster.templates.project_update import ProjectUpdateTemplate

TEMPLATES = {
    PocShowcaseTemplate.NAME: PocShowcaseTemplate,
    TechInsightTemplate.NAME: TechInsightTemplate,
    ProjectUpdateTemplate.NAME: ProjectUpdateTemplate,
}


class TemplateEngine:
    """Render POC project data using named templates."""

    @staticmethod
    def render(template_name: str, poc: PocProject) -> str:
        """Render a POC project using the specified template.

        Args:
            template_name: One of 'poc_showcase', 'tech_insight', 'project_update'.
            poc: The POC project data.

        Returns:
            Formatted post text.

        Raises:
            ValueError: If template_name is not recognized.
        """
        template_cls = TEMPLATES.get(template_name)
        if template_cls is None:
            available = ", ".join(TEMPLATES.keys())
            raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
        return template_cls.render(poc)

    @staticmethod
    def list_templates():
        """Return list of available template names."""
        return list(TEMPLATES.keys())
