import httpx
from fastapi import FastAPI, Response, status, Request

from src.utils import get_voice_id, VoiceCache
from src.models import TaskPost
from contextlib import asynccontextmanager
from src.scripts import download_voices_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        await download_voices_info(client=client)
        await VoiceCache.load_voices()
        app.state.httpx_client = client
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/test")
def test():
    return get_voice_id("Sarah")


@app.post("/update-voices")
async def update_voices(request: Request):
    await download_voices_info(request.app.state.httpx_client)
    await VoiceCache.load_voices()
    return Response(status_code=status.HTTP_200_OK)


# @app.post("/process_media")
# async def post_process_media():
#     return
