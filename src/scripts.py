import json

import aiofiles
import httpx
from elevenlabs.client import AsyncElevenLabs

from src.config import VOICES_PATH


async def download_voices_info(client: httpx.AsyncClient):
    response = await AsyncElevenLabs(httpx_client=client).voices.get_all()
    data = {
        v.name: {
            "voice_id": v.voice_id,
            "model_ids": v.high_quality_base_model_ids
        }
        for v in response.voices
    }
    data = json.dumps(data)
    async with aiofiles.open(VOICES_PATH, "w") as f:
        await f.write(data)
