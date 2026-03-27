"""POC showcase template - full project highlight."""

from typing import List

from linkedin_poster.models.poc import PocProject


class PocShowcaseTemplate:
    """Generate a LinkedIn post showcasing a POC project."""

    NAME = "poc_showcase"

    @staticmethod
    def render(poc: PocProject) -> str:
        lines = []

        # Title
        lines.append(f"Built: {poc.name}")
        lines.append("")

        # Description
        lines.append(poc.description)
        lines.append("")

        # Tech highlights
        if poc.tech_stack:
            lines.append("Tech stack:")
            for tech in poc.tech_stack:
                lines.append(f"  - {tech}")
            lines.append("")

        # GitHub link
        lines.append(f"Source: {poc.github_url}")

        # Demo link
        if poc.demo_url:
            lines.append(f"Demo: {poc.demo_url}")

        lines.append("")

        # Hashtags
        hashtags = _generate_hashtags(poc.keywords)
        lines.append(hashtags)

        return "\n".join(lines)


def _generate_hashtags(keywords: List[str]) -> str:
    """Generate hashtags from keywords."""
    tags = []
    for kw in keywords[:10]:
        tag = kw.replace(" ", "").replace("-", "").replace("/", "")
        tag = tag.replace(".", "").replace("+", "Plus")
        if tag:
            tags.append(f"#{tag}")
    return " ".join(tags)
