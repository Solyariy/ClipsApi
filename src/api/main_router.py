import asyncio
import json
from fastapi import Response, status, Request, APIRouter
from loguru import logger
from src.config import TEMP_PATH
from src.utils import get_voice_info, VoiceCache
from src.models import TaskPost, VideoSetup
from src.scripts import download_voices_info
from src.downloaders import TextToSpeechManager, BlocksManager, DirManager
from src.videos.combinations import get_video_setups

router = APIRouter(prefix="/api/v1")


@router.get("/")
def root():
    logger.info("root endpoint")
    return Response(status_code=status.HTTP_200_OK)


@router.get("/test")
def test():
    return get_voice_info("Sarah")


@router.put("/update-voices")
async def update_voices(request: Request):
    await download_voices_info(request.app.state.httpx_client)
    await asyncio.to_thread(VoiceCache.load_voices())
    return Response(status_code=status.HTTP_200_OK)


@router.post("/process_media")
async def post_process_media(task: TaskPost, request: Request):
    client = request.app.state.httpx_client
    semaphore = request.app.state.speach_semaphore
    async with DirManager(task_uuid=task.uuid_) as dir_manager:
        speach_manager = TextToSpeechManager(
            path=dir_manager.path,
            text_to_speach=task.text_to_speach,
            client=client,
            semaphore=semaphore
        )
        blocks_manager = BlocksManager(
            path=dir_manager.path,
            video_blocks=task.video_blocks,
            audio_blocks=task.audio_blocks,
            client=client
        )
        successes_speach, failures_speach = await speach_manager.gather_tasks()
        successes_blocks, failures_blocks = await blocks_manager.gather_tasks()

        logger.info(f"SUCCESS_SPEACH\n{successes_speach}\n")
        logger.info(f"failures_speach\n{failures_speach}\n")
        for e in failures_speach:
            logger.info(f"\n{e}\n")

        logger.info(f"successes_blocks\n{successes_blocks}\n")
        logger.info(f"failures_blocks\n{failures_blocks}\n")
        for e in failures_blocks:
            logger.info(f"\n{e}\n")

        video_setups: list[VideoSetup] = get_video_setups(
            video_blocks=successes_blocks["video_blocks"],
            audio_blocks=successes_blocks["audio_blocks"],
            speach_blocks=list(successes_speach.values())
        )
        logger.info(f"VIDEOS\n{video_setups}\n")
    data = [
        setup.model_dump()
        for setup in video_setups
    ]
    with open(TEMP_PATH / "test_video_setups.json", "w") as f:
        json.dump(data, f)
    return data
