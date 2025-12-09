import asyncio
from typing import Literal
from time import perf_counter
import httpx
from celery import group, chain
from loguru import logger
from src.api.utils import get_all_managers_kwargs, get_gcs_bucket
from src.downloaders import DirManager, TextToSpeechManager, BlocksManager
from src.downloaders.download_all_files import download_all_files
from src.models import VideoSetup, TaskPost
from src.videos.combinations import get_video_setups
from src.videos.process_setup import process_setup
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor
from src.api.celery_worker import celery_app


@celery_app.task(name="download_files_task")
def download_files_task(
        task_uuid: str,
        speach_kwargs: dict,
        blocks_kwargs: dict
) -> dict[Literal["successes_blocks", "successes_speach"], dict]:
    logger.info(f"DOWNLOADING FILES FOR TASK: {task_uuid}")
    start = perf_counter()

    async def _do_download():
        async with httpx.AsyncClient() as client:
            speach_manager = TextToSpeechManager(client=client, semaphore=asyncio.Semaphore(2), **speach_kwargs)
            blocks_manager = BlocksManager(client=client, **blocks_kwargs)
            results = await download_all_files(speach_manager, blocks_manager)
        return results

    logger.info(
        f"FINISHED DOWNLOADING FILES FOR TASK: {task_uuid}, "
        f"TIME: {perf_counter() - start} s"
    )
    return asyncio.run(_do_download())


@celery_app.task(name="process_setup_task")
def process_setup_task(
        processor_kwargs: dict,
        storage_kwargs: dict,
        setup_kwargs: dict
) -> str:
    bucket = get_gcs_bucket()  # probably bottleneck

    start = perf_counter()
    setup = VideoSetup(**setup_kwargs)
    logger.info(f"STARTED PROCESSING SETUP: {setup.uuid_}")
    processor = VideoProcessor(**processor_kwargs)
    storage_manager = StorageManager(bucket=bucket, **storage_kwargs)
    saved_url = process_setup(processor, storage_manager, setup)
    logger.info(
        f"FINISHED PROCESSING SETUP: {setup.uuid_}"
        f"TIME: {perf_counter() - start} s"
    )
    return saved_url


@celery_app.task(name="group_and_process_task")
def group_and_process_task(
        download_results: dict,
        task_uuid: str,
        processor_kwargs: dict,
        storage_kwargs: dict
):
    logger.info(f"DOWNLOAD RESULTS FOR TASK: {task_uuid} \n{download_results}")
    video_setups: list[VideoSetup] = get_video_setups(
        video_blocks=download_results["successes_blocks"]["video_blocks"],
        audio_blocks=download_results["successes_blocks"]["audio_blocks"],
        speach_blocks=list(download_results["successes_speach"].values())
    )
    all_processors = group(
        process_setup_task.s(
            processor_kwargs=processor_kwargs,
            storage_kwargs=storage_kwargs,
            setup_kwargs=setup.model_dump(mode="json")
        )
        for setup in video_setups
    )
    all_processors.delay()


@celery_app.task(name="process_download_all_setups_task")
def process_download_all_setups_task(
        task_kwargs: dict,
):
    task = TaskPost(**task_kwargs)
    logger.info(f"START process_download_all_setups_task: {task.uuid_}")
    with DirManager(task_uuid=task.uuid_) as dir_manager:
        speach_kwargs, blocks_kwargs, storage_kwargs, processor_kwargs = get_all_managers_kwargs(
            task, dir_manager.path,
        )
        logger.info(f"KWARGS: {speach_kwargs, blocks_kwargs, storage_kwargs, processor_kwargs}")

        job = chain(
            download_files_task.s(
                task_uuid=task.uuid_,
                speach_kwargs=speach_kwargs,
                blocks_kwargs=blocks_kwargs
            ),
            group_and_process_task.s(
                task_uuid=task.uuid_,
                processor_kwargs=processor_kwargs,
                storage_kwargs=storage_kwargs
            )
        )
        job.delay()
