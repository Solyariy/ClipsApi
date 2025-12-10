import asyncio

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Response,
    status,
)
from loguru import logger

from src.api.dependecies import (
    get_httpx_client,
)
from src.api.tasks import (
    process_download_all_setups_task,
)
from src.downloaders.scripts import download_voices_info
from src.models import TaskPost
from src.utils import VoiceCache

router = APIRouter(prefix="/api/v1")


@router.get("/")
def root():
    logger.debug("root endpoint")
    return Response(status_code=status.HTTP_200_OK)


@router.put("/update-voices")
async def update_voices(client=Depends(get_httpx_client)):
    await download_voices_info(client)
    await asyncio.to_thread(VoiceCache.load_voices())
    return Response(status_code=status.HTTP_200_OK)


@router.post("/process_media")
async def post_process_media(
        task: TaskPost,
):
    process_download_all_setups_task.run(
        task_kwargs=task.model_dump(mode="json")
    )
    return Response(status_code=status.HTTP_202_ACCEPTED)
