"""S3 document storage service."""

import logging
from io import BytesIO

import boto3
from botocore.config import Config

from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Manages document storage in S3."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.region = settings.S3_REGION
        
        # Configure boto3 client with retry settings
        config = Config(
            retries={"max_attempts": 3, "mode": "standard"},
            signature_version="s3v4",
        )
        
        self.client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=config,
        )

    async def upload_file(
        self, 
        bucket: str | None = None, 
        key: str = "", 
        content: bytes = b"",
        content_type: str = "text/html",
    ) -> str | None:
        """Upload a file to S3.
        
        Args:
            bucket: Bucket name (defaults to configured bucket)
            key: S3 object key
            content: File content as bytes
            content_type: MIME type of the content
            
        Returns:
            S3 key of the uploaded object, or None if upload failed
        """
        bucket = bucket or self.bucket
        
        if not content:
            logger.warning("No content to upload")
            return None
        
        try:
            self.client.upload_fileobj(
                BytesIO(content),
                bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            logger.info("Uploaded file to s3://%s/%s", bucket, key)
            return key
        except Exception as e:
            logger.error("Failed to upload to S3: %s", e)
            return None

    async def download_file(self, key: str) -> bytes | None:
        """Download a file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            File content as bytes, or None if download failed
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            logger.error("Failed to download from S3: %s", e)
            return None

    async def get_download_url(self, key: str, expires_in: int = 3600) -> str | None:
        """Generate a presigned download URL for a file.
        
        Args:
            key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            Presigned URL, or None if generation failed
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except Exception as e:
            logger.error("Failed to generate presigned URL: %s", e)
            return None

    async def delete_file(self, key: str) -> bool:
        """Delete a file from S3.
        
        Args:
            key: S3 object key
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("Deleted file from s3://%s/%s", self.bucket, key)
            return True
        except Exception as e:
            logger.error("Failed to delete from S3: %s", e)
            return False

    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3.
        
        Args:
            key: S3 object key
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
