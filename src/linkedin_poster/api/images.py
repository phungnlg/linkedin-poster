"""LinkedIn image upload flow."""

from pathlib import Path
from typing import Optional

from linkedin_poster.api.client import LinkedInClient


class ImagesAPI:
    """Handle LinkedIn image uploads."""

    def __init__(self, client: LinkedInClient):
        self.client = client

    async def upload(self, image_path: str, person_urn: str) -> str:
        """Upload an image and return its URN.

        Flow: initialize upload -> PUT binary -> return image URN.
        """
        # Step 1: Initialize upload
        init_body = {
            "initializeUploadRequest": {
                "owner": person_urn,
            }
        }
        resp = await self.client.post("/rest/images?action=initializeUpload", json=init_body)
        upload_data = resp.json()["value"]
        upload_url = upload_data["uploadUrl"]
        image_urn = upload_data["image"]

        # Step 2: Upload binary
        image_bytes = Path(image_path).read_bytes()
        content_type = self._guess_content_type(image_path)

        # Use raw httpx for the upload URL (it's a pre-signed URL, not the API base)
        import httpx
        async with httpx.AsyncClient(timeout=60.0) as upload_client:
            upload_resp = await upload_client.put(
                upload_url,
                content=image_bytes,
                headers={"Content-Type": content_type},
            )
            upload_resp.raise_for_status()

        return image_urn

    def _guess_content_type(self, path: str) -> str:
        ext = Path(path).suffix.lower()
        types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return types.get(ext, "application/octet-stream")
