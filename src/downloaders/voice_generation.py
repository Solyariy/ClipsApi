import asyncio
import uuid
from pathlib import Path

import aiofiles
import httpx
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs

from src.settings import config, elevenlabs_settings
from src.utils import get_voice_info


class TextToSpeechManager:
    def __init__(
            self,
            path: str,
            text_to_speach: config.TEXT_TO_SPEACH,
            client: httpx.AsyncClient,
            semaphore: asyncio.Semaphore
    ):
        self.path = Path(path)
        self.text_to_speach = {
            uuid.uuid4().hex: data
            for data in text_to_speach
        }
        self.elevenlabs = AsyncElevenLabs(
            api_key=elevenlabs_settings.API_KEY,
            httpx_client=client,
        )
        self.semaphore = semaphore

    async def generate_speach(
            self,
            text: str,
            voice: str,
            task_id: str,
    ):
        async with self.semaphore:
            voice_info = get_voice_info(voice)
            if elevenlabs_settings.MODEL_ID not in voice_info["model_ids"]:
                raise ValueError(
                    f"Can't use model: {elevenlabs_settings.MODEL_ID} "
                    f"for this voice: {voice_info}"
                )
            audio = self.elevenlabs.text_to_speech.stream(
                voice_id=voice_info["voice_id"],
                text=text,
                language_code="en",
                model_id=elevenlabs_settings.MODEL_ID,
                output_format=elevenlabs_settings.OUTPUT_FORMAT,
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=False,
                    speed=1.0,
                ),
            )
            filename = self.path / f"{task_id}_{voice}.mp3"
            async with aiofiles.open(filename, "wb") as f:
                async for chunk in audio:
                    if chunk:
                        await f.write(chunk)
            return task_id, str(filename)

    async def gather_tasks(self):
        tasks = [
            self.generate_speach(task_id=task_id, **info)
            for task_id, info in self.text_to_speach.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        failures = []
        successes = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append(result)
            else:
                successes[result[0]] = {
                    "speach_path": result[1],
                    **self.text_to_speach[result[0]]
                }

        return successes, failures
