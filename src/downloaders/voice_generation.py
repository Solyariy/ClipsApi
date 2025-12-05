import asyncio
import uuid
from pathlib import Path

import aiofiles
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from src.config import ELEVENLABS_API_KEY, TEXT_TO_SPEACH, ELEVENLABS_MODEL_ID, ELEVENLABS_OUTPUT_FORMAT, TEMP_PATH
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
        self.text_to_speach = {
            uuid.uuid4().hex: data
            for data in text_to_speach
        }
        self.elevenlabs = AsyncElevenLabs(
            api_key=ELEVENLABS_API_KEY,
            httpx_client=client,
        )

    async def generate_speach(
            self,
            text: str,
            voice: str,
            task_id: str
    ):
        voice_info = get_voice_info(voice)
        if ELEVENLABS_MODEL_ID not in voice_info["model_ids"]:
            raise ValueError(
                f"Can't use model: {ELEVENLABS_MODEL_ID} "
                f"for this voice: {voice_info}"
            )
        # audio = self.elevenlabs.text_to_speech.stream(
        #     voice_id=voice_info["voice_id"],
        #     text=text,
        #     language_code="en",
        #     model_id=ELEVENLABS_MODEL_ID,
        #     output_format=ELEVENLABS_OUTPUT_FORMAT,
        #     voice_settings=VoiceSettings(
        #         stability=0.0,
        #         similarity_boost=1.0,
        #         style=0.0,
        #         use_speaker_boost=False,
        #         speed=1.0,
        #     ),
        # )
        filename = self.path / f"{task_id}_{voice}.mp3"
        # async with aiofiles.open(filename, "wb") as f:
        #     async for chunk in audio:
        #         if chunk:
        #             await f.write(chunk)
        return task_id, filename

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


async def main():
    t = TextToSpeechManager(path=TEMP_PATH, text_to_speach=[
    {
      "text": "test1",
      "voice": "Sarah"
    },
    {
      "text": "test2",
      "voice": "George"
    },
    {
      "text": "test3",
      "voice": "Will"
    }
  ])
    s, f = await t.gather_tasks()
    print(s)
    print(f)

if __name__ == '__main__':
    asyncio.run(main())
