"""LinkedIn post creation API."""

from typing import List, Optional

from linkedin_poster.api.client import LinkedInClient
from linkedin_poster.models.post import PostContent


class PostsAPI:
    """Create, get, and delete LinkedIn posts."""

    def __init__(self, client: LinkedInClient):
        self.client = client

    async def create_text_post(self, author_urn: str, content: PostContent) -> str:
        """Create a text-only post. author_urn can be person or org URN."""
        body = {
            "author": author_urn,
            "commentary": content.commentary,
            "visibility": content.visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
        }
        resp = await self.client.post("/rest/posts", json=body)
        return resp.headers.get("x-restli-id", "")

    async def create_image_post(self, author_urn: str, content: PostContent) -> str:
        """Create a post with images. author_urn can be person or org URN."""
        if len(content.image_urns) == 1:
            media_content = {
                "media": {"id": content.image_urns[0]},
            }
        else:
            media_content = {
                "multiImage": {
                    "images": [{"id": urn} for urn in content.image_urns],
                },
            }

        body = {
            "author": author_urn,
            "commentary": content.commentary,
            "visibility": content.visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": media_content,
            "lifecycleState": "PUBLISHED",
        }
        resp = await self.client.post("/rest/posts", json=body)
        return resp.headers.get("x-restli-id", "")

    async def create_article_post(self, author_urn: str, content: PostContent) -> str:
        """Create a post with an article link. author_urn can be person or org URN."""
        body = {
            "author": author_urn,
            "commentary": content.commentary,
            "visibility": content.visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "article": {
                    "source": content.article_url,
                },
            },
            "lifecycleState": "PUBLISHED",
        }
        resp = await self.client.post("/rest/posts", json=body)
        return resp.headers.get("x-restli-id", "")

    async def delete_post(self, post_urn: str) -> None:
        """Delete a post by URN."""
        encoded = post_urn.replace(":", "%3A").replace("(", "%28").replace(")", "%29")
        await self.client.delete(f"/rest/posts/{encoded}")

    async def create_post(self, author_urn: str, content: PostContent) -> str:
        """Create post, automatically choosing type based on content."""
        if content.image_urns:
            return await self.create_image_post(author_urn, content)
        elif content.article_url:
            return await self.create_article_post(author_urn, content)
        else:
            return await self.create_text_post(author_urn, content)
