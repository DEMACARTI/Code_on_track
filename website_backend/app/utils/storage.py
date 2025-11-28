"""
Storage utilities for handling file uploads and interactions with MinIO/S3.
"""
import os
from typing import BinaryIO, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status

# MinIO/S3 configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "irf-assets")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=f"http{'s' if MINIO_SECURE else ''}://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    verify=False  # Only for development with self-signed certs
)

def ensure_bucket_exists():
    """Ensure the bucket exists, create it if it doesn't."""
    try:
        s3_client.head_bucket(Bucket=MINIO_BUCKET_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            s3_client.create_bucket(Bucket=MINIO_BUCKET_NAME)
        else:
            raise

def upload_file(
    file_obj: BinaryIO, 
    object_name: str, 
    content_type: str = "application/octet-stream"
) -> str:
    """
    Upload a file to MinIO/S3 storage.
    
    Args:
        file_obj: File-like object to upload
        object_name: Name to save the file as in the bucket
        content_type: MIME type of the file
        
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        ensure_bucket_exists()
        s3_client.upload_fileobj(
            file_obj,
            MINIO_BUCKET_NAME,
            object_name,
            ExtraArgs={
                "ContentType": content_type,
                "ACL": "public-read"
            }
        )
        return f"{s3_client.meta.endpoint_url}/{MINIO_BUCKET_NAME}/{object_name}"
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

async def upload_file_upload(
    file: UploadFile,
    object_name: Optional[str] = None
) -> str:
    """
    Upload a file from a FastAPI UploadFile.
    
    Args:
        file: FastAPI UploadFile object
        object_name: Optional custom object name, defaults to the original filename
        
    Returns:
        str: Public URL of the uploaded file
    """
    if not object_name:
        object_name = file.filename
    
    try:
        contents = await file.read()
        return upload_file(
            file_obj=contents,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file upload: {str(e)}"
        )

def get_presigned_url(object_name: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL for accessing a private object.
    
    Args:
        object_name: Name of the object in the bucket
        expires_in: Expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Presigned URL
    """
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": MINIO_BUCKET_NAME,
                "Key": object_name
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )

def delete_file(object_name: str) -> bool:
    """
    Delete a file from the storage bucket.
    
    Args:
        object_name: Name of the object to delete
        
    Returns:
        bool: True if deletion was successful
    """
    try:
        s3_client.delete_object(Bucket=MINIO_BUCKET_NAME, Key=object_name)
        return True
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
