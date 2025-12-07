import json

import aiofiles
import httpx
from elevenlabs.client import AsyncElevenLabs
from fastapi import HTTPException, status

from src.settings import config


async def download_voices_info(client: httpx.AsyncClient):
    response = await AsyncElevenLabs(httpx_client=client).voices.get_all()
    if not response.voices:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Server was not able to download voices info from Elevenlabs api"
        )
    data = {
        v.name: {
            "voice_id": v.voice_id,
            "model_ids": v.high_quality_base_model_ids
        }
        for v in response.voices
    }
    data = json.dumps(data)
    async with aiofiles.open(config.VOICES_PATH, "w") as f:
        await f.write(data)
