"""Project update template - progress update format."""

from linkedin_poster.models.poc import PocProject
from linkedin_poster.templates.poc_showcase import _generate_hashtags


class ProjectUpdateTemplate:
    """Generate a progress update LinkedIn post."""

    NAME = "project_update"

    @staticmethod
    def render(poc: PocProject) -> str:
        lines = []

        # Update header
        lines.append(f"Project update: {poc.name}")
        lines.append("")

        # What's new
        lines.append(poc.description)
        lines.append("")

        # Tech stack summary
        if poc.tech_stack:
            stack_str = " | ".join(poc.tech_stack[:5])
            lines.append(f"Stack: {stack_str}")
            lines.append("")

        # Links
        lines.append(f"Repo: {poc.github_url}")
        if poc.demo_url:
            lines.append(f"Demo: {poc.demo_url}")
        lines.append("")

        # Hashtags
        hashtags = _generate_hashtags(poc.keywords)
        lines.append(hashtags)

        return "\n".join(lines)
