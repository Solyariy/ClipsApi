import asyncio

import google.cloud.storage
import httpx
from celery import group
from loguru import logger
from src.api.utils import get_all_managers_kwargs
from src.downloaders import DirManager, TextToSpeechManager, BlocksManager
from src.downloaders.download_all_files import download_all_files
from src.models import VideoSetup, TaskPost
from src.videos.combinations import get_video_setups
from src.videos.process_setup import process_setup
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor
from src.api.celery_worker import celery_app


@celery_app.task(name="download_all_files_task")
async def download_and_make_setups_task(
        speach_kwargs: dict,
        blocks_kwargs: dict
) -> list[dict[str, ...]]:
    speach_manager = TextToSpeechManager(**speach_kwargs)
    blocks_manager = BlocksManager(**blocks_kwargs)
    results = await download_all_files(speach_manager, blocks_manager)
    video_setups: list[VideoSetup] = get_video_setups(
        video_blocks=results["successes_blocks"]["video_blocks"],
        audio_blocks=results["successes_blocks"]["audio_blocks"],
        speach_blocks=list(results["successes_speach"].values())
    )
    return [setup.model_dump() for setup in video_setups]


@celery_app.task(name="process_setup")
def process_setup_task(
        processor_kwargs: dict,
        storage_kwargs: dict,
        setup_kwargs: dict
) -> str:
    setup = VideoSetup(**setup_kwargs)
    logger.debug(f"STARTED PROCESSING SETUP: {setup.uuid_}")
    processor = VideoProcessor(**processor_kwargs)
    storage_manager = StorageManager(**storage_kwargs)
    saved_url = process_setup(processor, storage_manager, setup)
    logger.debug(f"FINISHED PROCESSING SETUP: {setup.uuid_}")
    return saved_url


@celery_app.task(name="process_all_setups_task")
async def process_all_setups_task(
        task_kwargs: dict,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        bucket: google.cloud.storage.Bucket,
):
    task = TaskPost(**task_kwargs)
    async with DirManager(task_uuid=task.uuid_) as dir_manager:
        speach_kwargs, blocks_kwargs, storage_kwargs, processor_kwargs = get_all_managers_kwargs(
            task, dir_manager.path, client, semaphore, bucket
        )
        setups_job = download_and_make_setups_task.delay(
            speach_kwargs, blocks_kwargs
        )
        setups_kwargs = setups_job.get(timeout=10)
        all_processors = group(
            process_setup_task.s(
                processor_kwargs=processor_kwargs,
                storage_kwargs=storage_kwargs,
                setup_kwargs=setup
            )
            for setup in setups_kwargs
        )
        all_processors.delay()
