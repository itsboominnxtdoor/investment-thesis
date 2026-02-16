"""S3 document storage service."""

from app.config import settings


class StorageService:
    """Manages document storage in S3."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.S3_REGION

    async def upload_document(self, key: str, content: bytes, content_type: str = "application/pdf") -> str:
        """Upload a document to S3.

        Returns the S3 key of the uploaded object.
        """
        raise NotImplementedError("S3 upload not yet implemented")

    async def get_download_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned download URL for a document."""
        raise NotImplementedError("S3 presigned URL generation not yet implemented")

    async def delete_document(self, key: str) -> None:
        """Delete a document from S3."""
        raise NotImplementedError("S3 delete not yet implemented")
