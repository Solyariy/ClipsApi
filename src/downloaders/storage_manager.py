from google.cloud.storage import Bucket
from loguru import logger


class StorageManager:
    def __init__(self, bucket: Bucket, base_folder: str = None):
        if not bucket.exists():
            raise ValueError(f"GCS Bucket: {bucket.name} does not exist")
        self.bucket = bucket
        if base_folder is not None:
            base_folder = base_folder.removeprefix("/")
        self.base_folder = base_folder

    def upload(self, path_to: str, path_from: str, folder: str = None) -> str:
        if folder is not None:
            if self.base_folder.endswith("/"):
                path_to = self.base_folder + path_to
            else:
                path_to = self.base_folder + "/" + path_to
        blob = self.bucket.blob(path_to)
        logger.debug(f"Uploading file to GCS, bucket: {self.bucket}, path: {path_to}")
        blob.upload_from_filename(path_from)
        logger.debug(f"Finished uploading file to GCS, bucket: {self.bucket}, path: {path_to}")
        return blob.public_url
