from celery import group
from loguru import logger
from src.api.utils import get_all_managers
from src.downloaders import DirManager
from src.downloaders.download_all_files import download_all_files
from src.models import VideoSetup, TaskPost
from src.videos.combinations import get_video_setups
from src.videos.process_setup import process_setup
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor
from src.api.celery_worker import celery_app


@celery_app.task(name="download_all_files_task")
async def download_and_make_setups_task(
        speach_manager, blocks_manager
):
    results = await download_all_files(speach_manager, blocks_manager)
    video_setups: list[VideoSetup] = get_video_setups(
        video_blocks=results["successes_blocks"]["video_blocks"],
        audio_blocks=results["successes_blocks"]["audio_blocks"],
        speach_blocks=list(results["successes_speach"].values())
    )
    return video_setups


@celery_app.task(name="process_setup")
def process_setup_task(
        processor: VideoProcessor,
        storage_manager: StorageManager,
        setup: VideoSetup
):
    logger.debug(f"STARTED PROCESSING SETUP: {setup.uuid_}")
    res = process_setup(processor, storage_manager, setup)
    logger.debug(f"FINISHED PROCESSING SETUP: {setup.uuid_}")
    return res


@celery_app.task(name="process_all_setups_task")
async def process_all_setups_task(
        task,
        client,
        semaphore,
        bucket,
):
    async with DirManager(task_uuid=task.uuid_) as dir_manager:
        speach_manager, blocks_manager, storage_manager, processor = get_all_managers(
            task, dir_manager.path, client, semaphore, bucket
        )
        setups_job = download_and_make_setups_task.delay(
            speach_manager, blocks_manager
        )
        setups = setups_job.get(timeout=10)
        all_processors = group(
            process_setup_task.s(
                processor=processor,
                storage_manager=storage_manager,
                setup=setup
            )
            for setup in setups
        )
        all_processors.delay()
