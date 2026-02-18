import json
from typing import Dict
import boto3
from .base import ArtifactStore



class S3ArtifactStore(ArtifactStore):
    def __init__(self, bucket_name: str, prefix: str = ""):
        self.bucket = bucket_name
        self.prefix = prefix.rstrip("/")
        self.client = boto3.client("s3")

    def _full_key(self, key: str) -> str:
        if self.prefix:
            return f"{self.prefix}/{key}"
        return key

    def write_json(self, key: str, data: Dict) -> None:
        full_key = self._full_key(key)
        body = json.dumps(data, indent=2)

        self.client.put_object(
            Bucket=self.bucket,
            Key=full_key,
            Body=body,
            ContentType="application/json",
        )

    def read_json(self, key: str) -> Dict:
        full_key = self._full_key(key)
        obj = self.client.get_object(Bucket=self.bucket, Key=full_key)
        body = obj["Body"].read().decode("utf-8")
        return json.loads(body)


    def exists(self, key: str) -> bool:
        full_key = self._full_key(key)
        try:
            self.client.head_object(Bucket=self.bucket, Key=full_key)
            return True
        except self.client.exceptions.ClientError:
            return False
