from fastapi import HTTPException, status

class MockMinioClient:
    def __init__(self):
        self.bucket_name = "qr-codes"
    
    def _ensure_bucket_exists(self):
        pass
    
    def upload_file(self, file_path: str, content_type: str) -> str:
        # Return a mock URL
        return f"http://localhost:8000/mock-qr/{Path(file_path).name}"
    
    def delete_file(self, object_name: str) -> bool:
        return True

# Replace the real MinIO client
minio_client = MockMinioClient()
