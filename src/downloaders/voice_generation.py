from pathlib import Path

import aiofiles
from elevenlabs import ElevenLabsEnvironment
from elevenlabs.client import AsyncElevenLabs
from src.config import TEMP_PATH, ELEVENLABS_API_KEY, TEXT_TO_SPEACH, ELEVENLABS_MODEL_ID, ELEVENLABS_OUTPUT_FORMAT
import httpx

from src.utils import get_voice_info


class TextToSpeechManager:
    def __init__(
            self,
            path: Path,
            text_to_speach: TEXT_TO_SPEACH,
            client: httpx.AsyncClient,
    ):
        self.path = path
        self.text_to_speach = text_to_speach
        self.elevenlabs = AsyncElevenLabs(
            timeout=5,
            api_key=ELEVENLABS_API_KEY,
            httpx_client=client,
            environment=ElevenLabsEnvironment.PRODUCTION_EU
        )

    async def generate_speach(
            self,
            text: str,
            voice: str,
            text_id: int
    ):
        voice_info = get_voice_info(voice)
        print(voice_info)
        if ELEVENLABS_MODEL_ID not in voice_info["model_ids"]:
            raise ValueError(
                f"Can't use model: {ELEVENLABS_MODEL_ID} "
                f"for this voice: {voice_info}"
            )
        async with aiofiles.open(self.path / f"{text_id}_{voice}.mp3", "wb") as f:
            audio = await self.elevenlabs.text_to_speech.stream(
                voice_id=voice_info["voice_id"],
                text=text,
                language_code="eu",
                model_id=ELEVENLABS_MODEL_ID,
                output_format=ELEVENLABS_OUTPUT_FORMAT,
            )
            async for chunk in audio:
                print(chunk.decode('utf-8'))
                if chunk:
                    await f.write(chunk)

    async def gather_tasks(self):
        tasks = [
            self.generate_speach(text_id=i, **info)
            for i, info in enumerate(self.text_to_speach)
        ]
        print(tasks)
        return await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    async with httpx.AsyncClient() as client:
        t = TextToSpeechManager(
            path=TEMP_PATH / "test_voices",
            text_to_speach=[
                {
                    "text": "Welcome to Plink — the ultimate platform for gamers who want to find perfect teammates. Whether you’re into competitive shooters, massive online RPGs, or just casual matches after work, Plink instantly connects you with players who match your skill level, playstyle, and favorite games. Say goodbye to random toxic lobbies, and hello to a team that shares your goals and passion for gaming.",
                    "voice": "Sarah"
                }
            ],
            client=client
        )
        await t.gather_tasks()


import asyncio

if __name__ == '__main__':
    asyncio.run(main())
