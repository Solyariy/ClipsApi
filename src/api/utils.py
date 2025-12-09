from os import PathLike
from google.cloud.storage import Bucket

from src.downloaders import TextToSpeechManager, BlocksManager
from src.models import TaskPost
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor
from google.cloud.storage import Client
from src.settings import google_settings


def get_all_managers_kwargs(
        task: TaskPost,
        path: PathLike,
        # client: httpx.AsyncClient,
        # semaphore: asyncio.Semaphore,
        # bucket: Bucket
) -> tuple[TextToSpeechManager, BlocksManager, StorageManager, VideoProcessor]:
    speach_kwargs = dict(
        path=path,
        text_to_speach=task.text_to_speach,
        # client=client,
        # semaphore=semaphore
    )
    dumped = task.model_dump(mode="json")
    blocks_kwargs = dict(
        path=path,
        video_blocks=dumped["video_blocks"],
        audio_blocks=dumped["audio_blocks"],
        # client=client
    )
    storage_kwargs = dict(
        # bucket=bucket,
        base_folder=f"videos/{task.uuid_}"
    )
    processor_kwargs = dict(path=path)

    return speach_kwargs, blocks_kwargs, storage_kwargs, processor_kwargs


def get_gcs_bucket() -> Bucket:
    gcs_client = Client.from_service_account_json(
        google_settings.CREDENTIALS_PATH
    )
    bucket = gcs_client.bucket(
        google_settings.STORAGE_BUCKET_NAME
    )
    return bucket
