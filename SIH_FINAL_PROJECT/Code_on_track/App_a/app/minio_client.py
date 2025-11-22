from minio import Minio
from minio.error import S3Error
import os
from typing import Optional, Tuple
from fastapi import HTTPException, status
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

class MinioClient:
    def __init__(self):
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "qr-codes")
        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=os.getenv("MINIO_SECURE", "False").lower() == "true"
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create it if it doesn't."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                # Set bucket policy to public read for demo purposes
                # In production, use proper access control
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                        }
                    ]
                }
                self.client.set_bucket_policy(self.bucket_name, policy)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize MinIO bucket: {str(e)}"
            )

    def upload_file(self, file_path: str, content_type: str) -> str:
        """
        Upload a file to MinIO and return its URL.
        
        Args:
            file_path: Path to the file to upload
            content_type: MIME type of the file
            
        Returns:
            str: Public URL of the uploaded file
        """
        try:
            # Generate a unique object name
            file_extension = os.path.splitext(file_path)[1]
            object_name = f"{uuid.uuid4()}{file_extension}"
            
            # Upload the file
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_path,
                content_type=content_type
            )
            
            # Generate the URL (this works for public buckets)
            url = f"http://{os.getenv('MINIO_ENDPOINT')}/{self.bucket_name}/{object_name}"
            return url
            
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to MinIO: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}"
            )

    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            object_name: Name of the object to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

# Create a global instance of the MinIO client
minio_client = MinioClient()
