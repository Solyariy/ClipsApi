from google.cloud.storage import Bucket
from loguru import logger


class StorageManager:
    def __init__(self, bucket: Bucket, base_folder: str = None):
        if not bucket.exists():
            raise ValueError(f"GCS Bucket: {bucket.name} does not exist")
        self.bucket = bucket
        if base_folder is not None:
            base_folder = base_folder.removeprefix("/").removesuffix("/")
        self.base_folder = base_folder

    def upload(self, filename: str, path_from: str) -> str:
        filename = self.base_folder + "/" + filename.removeprefix("/").removesuffix("/")

        blob = self.bucket.blob(filename)

        logger.debug(f"Uploading file to GCS, bucket: {self.bucket}, path: {filename}")
        blob.upload_from_filename(path_from)
        logger.debug(f"Finished uploading file to GCS, bucket: {self.bucket}, path: {filename}")

        return blob.public_url
