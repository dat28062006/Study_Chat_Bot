import uuid
from pathlib import Path

import boto3
from fastapi import UploadFile

from app.config import settings


class S3Service:
    def __init__(self):
        self.use_s3 = settings.use_s3 and bool(settings.s3_bucket)
        if self.use_s3:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )
            self.bucket = settings.s3_bucket
        else:
            Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    async def upload(self, file: UploadFile) -> str:
        key = f"uploads/{uuid.uuid4()}/{file.filename}"

        if self.use_s3:
            content = await file.read()
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content,
                ContentType=file.content_type or "application/pdf",
            )
            return key

        local_path = Path(settings.upload_dir) / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        local_path.write_bytes(content)
        return key

    def get_local_path(self, key: str) -> str:
        return str(Path(settings.upload_dir) / key)

    def download_bytes(self, key: str) -> bytes:
        if self.use_s3:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        return Path(self.get_local_path(key)).read_bytes()


s3_service = S3Service()
