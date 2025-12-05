import asyncio
import json

import httpx
from fastapi import FastAPI, Response, status, Request

from src.config import TEMP_PATH, DEBUG
from src.utils import get_voice_info, VoiceCache
from src.models import TaskPost, VideoSetup
from contextlib import asynccontextmanager
from src.scripts import download_voices_info
from src.downloaders import TextToSpeechManager, BlocksManager, DirManager
from src.videos.combinations import get_video_setups


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DEBUG:
        print("DEBUGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    async with httpx.AsyncClient() as client:
        await download_voices_info(client=client)
        VoiceCache.load_voices()
        app.state.httpx_client = client
        app.state.speach_semaphore = asyncio.Semaphore(2)
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/test")
def test():
    return get_voice_info("Sarah")


@app.put("/update-voices")
async def update_voices(request: Request):
    await download_voices_info(request.app.state.httpx_client)
    await asyncio.to_thread(VoiceCache.load_voices())
    return Response(status_code=status.HTTP_200_OK)


@app.post("/process_media")
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

        print(f"SUCCESS_SPEACH\n{successes_speach}\n")
        print(f"failures_speach\n{failures_speach}\n")
        for e in failures_speach:
            print(f"\n{e}\n")

        print(f"successes_blocks\n{successes_blocks}\n")
        print(f"failures_blocks\n{failures_blocks}\n")
        for e in failures_blocks:
            print(f"\n{e}\n")

        video_setups: list[VideoSetup] = get_video_setups(
            video_blocks=successes_blocks["video_blocks"],
            audio_blocks=successes_blocks["audio_blocks"],
            speach_blocks=list(successes_speach.values())
        )
        print(f"VIDEOS\n{video_setups}\n")
    data = [
        setup.model_dump()
        for setup in video_setups
    ]
    with open(TEMP_PATH / "test_video_setups.json", "w") as f:
        json.dump(data, f)
    return data