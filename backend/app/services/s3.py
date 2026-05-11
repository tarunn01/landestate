import boto3
from app.core.config import settings
from uuid import uuid4


class S3Service:
    def __init__(self):
        self.client = boto3.client("s3", region_name=settings.AWS_REGION)

    def upload_image(self, file, property_id, filename):
        key = f"properties/{property_id}/{uuid4()}-{filename}"
        self.client.upload_fileobj(file, settings.S3_BUCKET_NAME, key)
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        return key, url

    def delete_image(self, s3_key):
        self.client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
