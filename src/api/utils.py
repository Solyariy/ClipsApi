import asyncio
from os import PathLike

from google.cloud.storage import Bucket
import httpx

from src.downloaders import TextToSpeechManager, BlocksManager
from src.models import TaskPost
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor


def get_all_managers(
        task: TaskPost,
        path: PathLike,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        bucket: Bucket
) -> tuple[TextToSpeechManager, BlocksManager, StorageManager, VideoProcessor]:
    speach_manager = TextToSpeechManager(
        path=path,
        text_to_speach=task.text_to_speach,
        client=client,
        semaphore=semaphore
    )
    blocks_manager = BlocksManager(
        path=path,
        video_blocks=task.video_blocks,
        audio_blocks=task.audio_blocks,
        client=client
    )
    storage_manager = StorageManager(
        bucket=bucket,
        base_folder="videos"
    )
    processor = VideoProcessor(path)

    return speach_manager, blocks_manager, storage_manager, processor
