"""Orchestrates post creation from POC configs."""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from linkedin_poster.api.client import LinkedInClient
from linkedin_poster.api.posts import PostsAPI
from linkedin_poster.api.images import ImagesAPI
from linkedin_poster.auth.token_store import TokenStore
from linkedin_poster.models.poc import PocProject
from linkedin_poster.models.post import PostContent, PostRecord
from linkedin_poster.services.template_engine import TemplateEngine
from linkedin_poster.services.history import HistoryStore

console = Console()


class PostService:
    """High-level service for creating and publishing posts."""

    def __init__(
        self,
        token_store: Optional[TokenStore] = None,
        history: Optional[HistoryStore] = None,
    ):
        self.token_store = token_store or TokenStore()
        self.history = history or HistoryStore()

    def load_poc_config(self, config_path: str) -> PocProject:
        """Load a POC project from a JSON config file."""
        with open(config_path) as f:
            data = json.load(f)
        return PocProject(**data)

    def generate_text(
        self, poc: PocProject, template_name: str = "poc_showcase"
    ) -> str:
        """Generate post text from POC data and template."""
        return TemplateEngine.render(template_name, poc)

    def draft(
        self, config_path: str, template_name: str = "poc_showcase"
    ) -> PostContent:
        """Generate a draft post from a POC config (no API call)."""
        poc = self.load_poc_config(config_path)
        text = self.generate_text(poc, template_name)
        content = PostContent(commentary=text, article_url=poc.github_url)
        self._print_preview(content)
        return content

    def draft_text(self, text: str) -> PostContent:
        """Draft a text-only post."""
        content = PostContent(commentary=text)
        self._print_preview(content)
        return content

    def _resolve_author(self, org_id: Optional[str] = None) -> str:
        """Return org URN if org_id given, otherwise person URN."""
        if org_id:
            return f"urn:li:organization:{org_id}"
        person_urn = self.token_store.get_person_urn()
        if not person_urn:
            raise ValueError("Not authenticated. Run 'linkedin-poster auth login' first.")
        return person_urn

    async def publish(
        self,
        config_path: str,
        template_name: str = "poc_showcase",
        with_images: bool = False,
        org_id: Optional[str] = None,
    ) -> str:
        """Generate and publish a POC showcase post. Returns post URN."""
        poc = self.load_poc_config(config_path)
        text = self.generate_text(poc, template_name)
        author_urn = self._resolve_author(org_id)

        # Check for duplicate
        poc_hash = HistoryStore.compute_hash(config_path)
        if self.history.is_duplicate(poc_hash):
            console.print("[yellow]Warning: This POC config was already posted.[/yellow]")

        client = LinkedInClient(self.token_store)
        try:
            image_urns = []
            if with_images and poc.screenshots:
                images_api = ImagesAPI(client)
                for screenshot in poc.screenshots:
                    urn = await images_api.upload(screenshot, author_urn)
                    image_urns.append(urn)

            content = PostContent(
                commentary=text,
                image_urns=image_urns,
                article_url=poc.github_url if not image_urns else None,
            )

            posts_api = PostsAPI(client)
            post_urn = await posts_api.create_post(author_urn, content)

            # Record in history
            record = PostRecord(
                post_urn=post_urn,
                poc_hash=poc_hash,
                text_preview=text[:100],
                template_name=template_name,
            )
            self.history.add(record)

            return post_urn
        finally:
            await client.close()

    async def publish_text(self, text: str, org_id: Optional[str] = None) -> str:
        """Publish a text-only post. Returns post URN."""
        author_urn = self._resolve_author(org_id)

        client = LinkedInClient(self.token_store)
        try:
            content = PostContent(commentary=text)
            posts_api = PostsAPI(client)
            post_urn = await posts_api.create_post(author_urn, content)

            record = PostRecord(
                post_urn=post_urn,
                poc_hash="text_" + text[:20],
                text_preview=text[:100],
            )
            self.history.add(record)

            return post_urn
        finally:
            await client.close()

    def _print_preview(self, content: PostContent) -> None:
        """Render a rich preview of the post."""
        console.print()
        console.print(Panel(content.commentary, title="Post Preview", border_style="blue"))
        if content.article_url:
            console.print(f"  Article: {content.article_url}")
        if content.image_urns:
            console.print(f"  Images: {len(content.image_urns)} attached")
        console.print()
