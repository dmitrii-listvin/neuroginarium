import uuid
import boto3
from ImageStorage.ImageStorage import ImageStorage


class S3ImageStorage(ImageStorage):
    async def if_path_exists(self, path: str) -> bool:
        raise NotImplementedError()

    async def load_image(self, path: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=path)
        data = response['Body'].read()
        return data

    async def save_image(self, image: bytes) -> str:
        filename = f"{uuid.uuid4()}.png"
        self.s3_client.put_object(Bucket=self.bucket, Key=filename, Body=image)
        return filename

    def __init__(self, ak: str, sk: str, bucket: str):
        super().__init__()
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=ak,
            aws_secret_access_key=sk
        )
        self.bucket = bucket
