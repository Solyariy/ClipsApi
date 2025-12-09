import asyncio
import json
from fastapi import Response, status, APIRouter, Body, Depends
from loguru import logger

from src.api.tasks import process_setup_task
from src.api.dependecies import get_httpx_client, get_speach_semaphore, get_gcs_bucket
from src.api.utils import get_all_managers
from src.settings import config, google_settings
from src.utils import get_voice_info, VoiceCache
from src.models import TaskPost, VideoSetup
from src.downloaders.scripts import download_voices_info
from src.downloaders import DirManager
from src.videos.combinations import get_video_setups
from src.videos.storage_manager import StorageManager
from src.videos.video_processor import VideoProcessor

router = APIRouter(prefix="/api/v1")


@router.get("/")
def root():
    logger.debug("root endpoint")
    return Response(status_code=status.HTTP_200_OK)


@router.get("/test")
def test():
    logger.debug("test get voice info")
    logger.debug(config.DEBUG)
    logger.debug(config.SRC_PATH)
    logger.debug(google_settings.CREDENTIALS_PATH)
    return get_voice_info("Sarah")


@router.post("/celery_test")
def celery_test(
        bucket=Depends(get_gcs_bucket),
):
    setup = VideoSetup(
        clips_path=(
            config.TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/block1_1.mp4",
            config.TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/block2_3.mp4",
        ),
        audio_path=config.TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/audio1_1.mp3",
        speach_path=config.TEMP_PATH / "fa06f67fe765436ab8029bb90799f901/be4b86b7dad84219864100027b48e7a7_Will.mp3",
        text="asds",
        voice="asdasd"
    )
    p = VideoProcessor(config.TEMP_PATH / "fa06f67fe765436ab8029bb90799f901")
    s = StorageManager(bucket, base_folder="videos")
    process_setup_task.delay(p, s, setup)
    return {"Task": "Success"}


@router.put("/update-voices")
async def update_voices(client=Depends(get_httpx_client)):
    await download_voices_info(client)
    await asyncio.to_thread(VoiceCache.load_voices())
    return Response(status_code=status.HTTP_200_OK)


@router.post("/process_media")
async def post_process_media(
        task: TaskPost,
        client=Depends(get_httpx_client),
        semaphore=Depends(get_speach_semaphore),
        bucket=Depends(get_gcs_bucket),
):
    async with DirManager(task_uuid=task.uuid_) as dir_manager:
        speach_manager, blocks_manager, storage_manager, processor = get_all_managers(
            task, dir_manager.path, client, semaphore, bucket
        )

        successes_speach, failures_speach = await speach_manager.gather_tasks()
        successes_blocks, failures_blocks = await blocks_manager.gather_tasks()

        logger.debug(f"SUCCESS_SPEACH\n{successes_speach}\n")
        logger.debug(f"failures_speach\n{failures_speach}\n")
        for e in failures_speach:
            logger.debug(f"\n{e}\n")

        logger.debug(f"successes_blocks\n{successes_blocks}\n")
        logger.debug(f"failures_blocks\n{failures_blocks}\n")
        for e in failures_blocks:
            logger.info(f"\n{e}\n")

        video_setups: list[VideoSetup] = get_video_setups(
            video_blocks=successes_blocks["video_blocks"],
            audio_blocks=successes_blocks["audio_blocks"],
            speach_blocks=list(successes_speach.values())
        )
        logger.debug(f"VIDEOS\n{video_setups}\n")

