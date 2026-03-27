"""Tech insight template - shorter learning/insight format."""

from linkedin_poster.models.poc import PocProject
from linkedin_poster.templates.poc_showcase import _generate_hashtags


class TechInsightTemplate:
    """Generate a shorter insight-focused LinkedIn post."""

    NAME = "tech_insight"

    @staticmethod
    def render(poc: PocProject) -> str:
        lines = []

        # Hook
        if poc.tech_stack:
            primary_tech = poc.tech_stack[0]
            lines.append(f"Learned something interesting while working with {primary_tech}.")
        else:
            lines.append(f"Learned something interesting while building {poc.name}.")
        lines.append("")

        # Insight body
        lines.append(poc.description)
        lines.append("")

        # Key takeaway
        if poc.keywords:
            top_keywords = ", ".join(poc.keywords[:3])
            lines.append(f"Key areas: {top_keywords}")
            lines.append("")

        # Link
        lines.append(f"Code: {poc.github_url}")
        lines.append("")

        # Hashtags
        hashtags = _generate_hashtags(poc.keywords)
        lines.append(hashtags)

        return "\n".join(lines)
