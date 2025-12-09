import asyncio
from os import PathLike

from google.cloud.storage import Bucket
import httpx

from src.downloaders import TextToSpeechManager, BlocksManager
from src.models import TaskPost
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor


def get_all_managers_kwargs(
        task: TaskPost,
        path: PathLike,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        bucket: Bucket
) -> tuple[TextToSpeechManager, BlocksManager, StorageManager, VideoProcessor]:
    speach_kwargs = dict(
        path=path,
        text_to_speach=task.text_to_speach,
        client=client,
        semaphore=semaphore
    )
    blocks_kwargs = dict(
        path=path,
        video_blocks=task.video_blocks,
        audio_blocks=task.audio_blocks,
        client=client
    )
    storage_kwargs = dict(
        bucket=bucket,
        base_folder="videos"
    )
    processor_kwargs = dict(path=path)

    return speach_kwargs, blocks_kwargs, storage_kwargs, processor_kwargs
